from app.admin import bp
from app.admin.utils import allowed_file
from flask import render_template, request, flash, current_app, redirect, url_for
from db import query_db, get_db, to_object
from werkzeug.utils import secure_filename
from datetime import datetime
import os

@bp.route('/')
def index():
    return render_template('admin/index.html', title='Admin')

@bp.route('/orders')
def orders():
    orders = query_db('select id, cust_name, due, is_paid, status from orders')
    orders = to_object(orders)
    if orders:
        for order in orders:
            order['due'] = datetime.strptime(order['due'], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
    return render_template('admin/orders.html', title='Orders', orders=orders)

@bp.route('/status/<int:id>/<int:status>')
def updateStatus(id, status):
    query_db('update orders set status= ? where id = ?', (status, id,))
    get_db().commit()
    flash('Order status updated')
    return redirect(url_for('admin.orders'))

@bp.route('/paid/<int:id>/<int:paid>')
def updatePaid(id, paid):
    query_db('update orders set is_paid= ? where id = ?', (paid, id,))
    get_db().commit()
    flash('Paid status updated')
    return redirect(url_for('admin.orders'))

@bp.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('image')

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        query_db('''insert into menu (name, category, price, description, image)
                values (?, ?, ?, ?, ?)''',
                (name, category, price, description, secure_filename(image.filename)))
        get_db().commit()
        flash('Menu item has been added')
    return render_template('admin/menu.html', title='Menu')
