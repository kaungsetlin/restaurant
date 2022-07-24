from flask import session, flash
from db import query_db, get_db, to_object

def updateCart(id, qty):
    if 'cart' in session:
        cart = session['cart']
        if not any(obj['id'] == str(id) for obj in cart):
            cart.append({'id': str(id), 'qty': qty})
            flash('Item added to cart')
        elif any(obj['id'] == str(id) for obj in cart):
            for obj in cart:
                if obj['id'] == str(id):
                    obj.update({'id': str(id), 'qty': qty})
            flash('Item updated in cart')
        session['cart'] = cart
    else:
        session['cart'] = [{'id': str(id), 'qty': qty}]
        flash('Item added to cart')

def getCartItems():
    cart = session.get('cart')
    items = None
    if cart:
        ids = [i['id'] for i in cart]
        items = query_db(f'''select menu.id, menu.name, category.name category,
                            price, description from menu join category
                            on menu.category = category.code
                            where menu.id in ({','.join(['?']*len(ids))})''', tuple(ids))
        items = to_object(items)

        for item in items:
            for c in cart:
                if str(c['id']) == str(item['id']):
                    item.update({'qty': c['qty']})

    return items

def getTotal():
    items = getCartItems()
    total = 0
    if items:
        total = sum(float(i['qty']) * float(i['price']) for i in items)
    return total
