from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from flask import request
from datetime import datetime

@app.route('/finances/', methods=['GET'])
def get_finances():
    records = []
    return render_template('fin/view.liquid',
                           records = records)

@app.route('/finances/items/search', methods=['GET'])
def get_finance_items_search():
    with connect() as conn:
        # ?invDate=2024-06-12
        date = datetime.strptime(request.args.get('invDate'), '%Y-%m-%d')
        items = conn.search_items(date)
        # return items
        return render_template('fin/item_search.liquid', items=items)