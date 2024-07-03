"""Handles reuqests to view docket dashboards"""
from flask import session, abort
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect


@app.route('/doc/dash/<dash_seq>')
def get_doc_dash(dash_seq):
    """Handles requests to view dashboard"""
    user_seq = session.get('user_seq')
    with connect() as conn:
        data = conn.get_docket_dash_data(dash_seq, user_seq)

        if len(data) == 0:
            abort(504)
        return render_template("doc/view.liquid", results=data)
