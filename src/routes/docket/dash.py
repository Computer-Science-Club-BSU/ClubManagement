from app import app
from src.utils.template_utils import render_template
from flask import request, session, abort
from src.utils.db_utilities import connect


@app.route('/doc/dash')
def get_doc_dash():
    user_seq = session.get('user_seq')
    dash_id = request.args.get('dash')
    with connect() as conn:
        data = conn.get_docket_dash_data(user_seq, dash_id)
        
        if data is None:
            abort(504)
        return render_template("doc/view.liquid", results=data)
