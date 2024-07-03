"""Serves routes relating to Finance Items"""
from datetime import datetime
from flask import request
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/finances/items/search', methods=['GET'])
def get_finance_items_search():
    """Serves the /finances/items/search method.
    Allows for the search of finance items for finances."""
    with connect() as conn:
        date = datetime.strptime(request.args.get('invDate'), '%Y-%m-%d')
        items = conn.search_items(date)
        # return items
        return render_template('fin/item_search.liquid', items=items)
