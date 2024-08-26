"""Serves routes relating to Finance Items"""
from datetime import datetime
from flask import request, session
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/finance/items/search', methods=['GET'])
def get_finance_items_search():
    """Serves the /finance/items/search method.
    Allows for the search of finance items for finances."""
    with connect() as conn:
        date = datetime.strptime(request.args.get('invDate'), '%Y-%m-%d')
        items = conn.search_items(date)
        # return items
        return render_template('fin/item_search.liquid', items=items)

@app.route('/finance/items', methods=['GET'])
def get_finance_items():
    with connect() as conn:
        data = conn.get_item_data()
    return render_template('fin/item_new.liquid', data=data)

@app.post('/finance/vend/new/')
def post_finance_vend_new():
    data = request.json
    name = data['vend_name']
    status = data['vend_status']
    with connect() as conn:
        res, err = conn.create_vendor(name, status, session['user_seq'])
    if res:
        return "", 200
    return str(err), 500

@app.post('/finance/vend/edit/')
def post_finance_vend_edit():
    data = request.json
    old_name = data['old_name']
    new_name = data['new_name']
    status = data['vend_status']
    with connect() as conn:
        res, err = conn.update_vendor(old_name, new_name, status, session['user_seq'])
    if res:
        return "", 200
    return str(err), 500

@app.post('/finance/item/new/')
def post_finance_item_new():
    data = request.json
    item_name = data['item_name']
    displayed = data['displayed']
    vend_seq = data['vend_seq']
    initial_price = data['init_price']
    with connect() as conn:
        res, err = conn.create_item(item_name, displayed, vend_seq, initial_price, session['user_seq'])
    if res:
        return "", 200
    return str(err), 500

@app.post('/finance/item/price/new/')
def post_finances_item_price_new():
    data = request.json
    price = data['price']
    date = datetime.strptime(data['date'], '%Y-%m-%d')
    status = data['status']
    item = data['seq']
    with connect() as conn:
        res, err = conn.update_price(item, date, price, status, session['user_seq'])
    if res:
        return "", 200
    return str(err), 500
