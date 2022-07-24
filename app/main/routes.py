from app.main import bp
from app.main.utils import updateCart, getCartItems, getTotal
from flask import render_template, session, redirect, url_for, request, jsonify, abort, flash, current_app
from db import query_db, get_db, to_object
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash

@bp.route('/')
def index():
    menu = query_db('''select menu.id, menu.name, category.name category,
                        price, description from menu join category
                        on menu.category = category.code
                        where is_special=1''')
    return render_template('main/index.html', title='Home', menu=menu)

@bp.route('/menu')
def menu():
    menu = query_db('''select menu.id, menu.name, category.name category,
                        price, description from menu join category
                        on menu.category = category.code''')
    return render_template('main/menu.html', title='Menu', menu=menu)

@bp.route('/cart')
def cart():
    items = getCartItems()
    return render_template('main/cart.html', title='Cart', items=items)

@bp.route('/addtocart/<int:id>/<int:qty>')
def addtoCart(id, qty):
    updateCart(id, qty)
    return redirect(request.referrer)

@bp.route('/remove/<int:id>')
def remove(id):
    cart = session.get('cart')
    if not cart: return abort(404)
    for i in cart:
        if str(i['id']) == str(id):
            cart.remove(i)
    session['cart'] = cart
    flash('Item removed from cart')
    return redirect(request.referrer)

@bp.route('/checkout')
def checkout():
    scheduled = session.get('scheduled')
    items = getCartItems()
    total = getTotal()
    if not items: abort(404)
    return render_template('main/checkout.html', title='Checkout', items=items, total=total, scheduled=scheduled)

@bp.route('/scheduled', methods=['GET', 'POST'])
def scheduled():
    min = datetime.today().strftime('%Y-%m-%d')
    max = (datetime.today() + timedelta(days=30)).strftime('%Y-%m-%d')

    if request.method == 'POST':
        date = request.form.get('date') # e.g. "2022-07-23"
        time = request.form.get('time') # e.g. "12:00"
        session['scheduled'] = {'date': date, 'time': time}
        return redirect(url_for('main.checkout'))
    return render_template('main/scheduled.html', title='Scheduled Order', min=min, max=max)

@bp.route('/payment', methods=['GET', 'POST'])
def payment():
    items = session.get('cart')
    if not items: abort(404)
    # make order, pop session scheduled and cart
    if request.method == 'POST':
        payment = request.form.get('payment')
        name = str(request.form.get('name')).title()
        email = request.form.get('email')
        phone = request.form.get('phone')
        phone = request.form.get('phone')
        note = request.form.get('note')
        next = int(query_db('select seq from sqlite_sequence where name="orders"', one=True)['seq']) + 1
        hash = generate_password_hash(current_app.config['SECRET_KEY'] + str(next))
        due = datetime.now()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'scheduled' in session:
            scheduled = session.get('scheduled')
            due = scheduled['date'] + ' ' + scheduled['time']
            due = datetime.strptime(due, "%Y-%m-%d %H:%M").strftime('%Y-%m-%d %H:%M:%S')

        query_db('insert into orders values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (None, name, email, phone, due, timestamp, note, payment, 0, hash, 1))
        for item in items:
            query_db('insert into order_items values (?, ?, ?)',
            (str(next), item['id'], item['qty']))
        get_db().commit()
        # send email
        session.pop('cart', None)
        session.pop('scheduled', None)
        flash('An order confirmation will be sent to your email.')
        return redirect(url_for('main.index'))
    return render_template('main/payment.html', title='Payment')

@bp.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if request.method == 'POST':
        hash = request.form.get('hash')
        order = query_db('select * from orders where hash = ?', (hash,), one=True)
        if order:
            return redirect(url_for('main.order', hash=hash))
        else:
            abort(404)
    return render_template('main/lookup.html', title='Order Lookup')

@bp.route('/order/<hash>')
def order(hash):
    status = {"0": "Cancelled", "1": "Created", "2": "Preparing", "3": "Ready"}
    progress = {"0": "0", "1": "33", "2": "66", "3": "100"}
    order = query_db('select * from orders where hash = ?', (hash,), one=True)
    if not order: abort(401)

    items = query_db('''select * from order_items oi join menu m
                        on oi.item_id = m.id where oi.order_id = ?''',
                        (order['id'],))
    order = to_object(order)
    order['progress'] = progress[str(order['status'])]
    order['status'] = status[str(order['status'])]
    return render_template('main/order.html', title=f'Order #{order["id"]:02d}', order=order, items=items)

@bp.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact')
