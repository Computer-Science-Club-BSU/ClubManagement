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

@app.route('/finance/items/new', methods=['GET'])
def get_finance_items_new():
    return render_template('fin/item_new.liquid')

@app.route('/finance/items/new', methods=['POST'])
def post_finance_items_new():
    # 'type': mode,
    # 'vendor': document.getElementById('vendor').value,
    # 'name': document.getElementById('name').value,
    # 'price': document.getElementById('price').value,
    # 'date': document.getElementById('date').value
    data = request.json
    type = data.get('type')
    vendor = data.get('vendor')
    name = data.get('name')
    price = data.get('price')
    date = data.get('date')
    visible = data.get('visible', False)
    user = session.get('user_seq')
    with connect() as conn:
        if type == 'c':
            res, _ = conn.create_fin_item(vendor, name, price, date,
                                          visible, user)
        elif type == 'u':
            res, _ = conn.update_fin_item(vendor, name, price, date,
                                          visible, user)
        else:
            res = False
    
    if res:
        return "",200
    return "",400