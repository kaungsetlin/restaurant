from app.admin import bp
from app.admin.utils import allowed_file, to_int
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
    menu = query_db('select id, name, category, price, description, is_special, is_active from menu')
    return render_template('admin/menu.html', title='Menu', menu=menu)
    
@bp.route('/menu/update/<int:id>', methods=['GET', 'POST'])
def update_item(id):
    item = query_db('select * from menu where id = ?', (id,), one=True)
    if not item: abort(404)

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        description = description.strip() if description else description
        image = request.files.get('image')
        special = request.form.get('special')
        special = to_int(special)
        active = request.form.get('active')
        active = to_int(active)
        filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = item['image']


        query_db('''update menu set name=?, category=?, price=?, description=?, image=?, is_special=?, is_active=? where id=?''',
                (name, category, price, description, filename, special, active, id))
        get_db().commit()
        flash('Menu item has been updated')
        return redirect(url_for('admin.update_item', id=id))
    return render_template('admin/update_item.html', title=f'Item #{item["id"]:02d}', item=item) 

@bp.route('/menu/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('image')

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        query_db('''insert or replace into menu (name, category, price, description, image)
                values (?, ?, ?, ?, ?)''',
                (name, category, price, description, secure_filename(image.filename)))
        get_db().commit()
        flash('Menu item has been added')
    return render_template('admin/add_item.html', title='Add Menu Item')

@bp.route('/menu/delete/<int:id>', methods=['POST'])
def delete_item(id):
    item = query_db('select * from menu where id = ?', (id,), one=True)
    if not item: abort(404)
    query_db('delete from menu where id = ?', (id,))
    get_db().commit()
    flash(f"Item #{id:02d} has been deleted")
    return redirect(url_for('admin.menu'))
