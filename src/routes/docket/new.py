from app import app
from flask import session, request, abort, redirect
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template
import logging

logger = logging.getLogger('DocketNew')

@app.route('/doc/create', methods=['GET'])
@app.route('/doc/create/', methods=['GET'])
def get_new_docket_item():
    
    with connect() as conn:
        docket_users = conn.get_docket_users()
        return render_template("doc/new.liquid", docket_users=docket_users)
    

@app.route('/doc/create', methods=['POST'])
@app.route('/doc/create/', methods=['POST'])
def post_new_docket_item():
    with connect() as conn:
        title = request.form.get('title')
        body = request.form.get('body')
        user_seq = session.get('user_seq')
        status = request.form.get('status', 1)
        vote_type = request.form.get('vote_type', 2)
        assignees = request.form.getlist('assignees')
        res, seq = conn.create_docket_and_assign(title,
                                                 body,
                                                 user_seq,
                                                 status,
                                                 vote_type,
                                                 assignees)
        if res:
            return redirect(f'/doc/view?{seq=}')
        else:
            
            return "Failed to create record"

@app.route('/doc/conv/add', methods=['POST'])
def post_add_conv():
    with connect() as conn:
        conv_body = request.form.get("convBody", "")
        doc_seq = request.args.get('seq')
        stat, res = conn.create_docket_conversation(
            doc_seq,
            session.get('user_seq'),
            conv_body
            )
        if stat:
            return redirect(f'/doc/view/?seq={doc_seq}')
        else:
            return "Whoops!"