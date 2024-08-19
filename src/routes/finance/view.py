"""Serves routes relating to viewing finances."""
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/finances/', methods=['GET'])
def get_finances():
    """Serves the /finances/ path
    Serves a table of all financial records"""
    with connect() as conn:
        results = conn.get_finance_headers_summary()
        return render_template('fin/view.liquid',
                           records = results)

@app.get('/finances/view/<seq>')
def get_finances_view(seq):
    with connect() as conn:
        data = conn.get_finance_object(seq)
        print(data)
        header = data['header']
        li = data['lines']
        return render_template('fin/finance_record.liquid',
                           li=li,
                           header=header)
