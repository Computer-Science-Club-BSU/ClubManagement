"""Contains functions pertaining to create docket record endpoints"""
import logging
from flask import session, request, redirect
from app import app
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

logger = logging.getLogger('DocketNew')

@app.route('/doc/create/', methods=['GET'])
def get_new_docket_item():
    """Handles /doc/create/ requests [GET]
    Sends a form for creating docket requests"""
    with connect() as conn:
        docket_users = conn.get_docket_users()
        return render_template("doc/new.liquid", docket_users=docket_users)


@app.route('/doc/create/', methods=['POST'])
def post_new_docket_item():
    """Handles /doc/create/ requests [POST]
    Handles form requests and creates relevant data."""
    with connect() as conn:
        title = request.form.get('title')
        body = request.form.get('body')
        user_seq = session.get('user_seq')
        status = request.form.get('status', 1)
        vote_type = request.form.get('vote_type', 2)
        assignees = request.form.getlist('assignees')
        res, seq = conn.create_docket_and_assign(title, #pylint: disable=unpacking-non-sequence
                                                 body,
                                                 user_seq,
                                                 status,
                                                 vote_type,
                                                 assignees)
        if res:
            return redirect(f'/doc/view?{seq=}')
        return "Failed to create record"

@app.route('/doc/conv/add', methods=['POST'])
def post_add_conv():
    """Handles /doc/conv/add requests [POST]
    Handles posts to a docket's conversation tab."""
    with connect() as conn:
        conv_body = request.form.get("convBody", "")
        doc_seq = request.args.get('seq')
        stat, _ = conn.create_docket_conversation( #pylint: disable=unpacking-non-sequence
            doc_seq,
            session.get('user_seq'),
            conv_body
            )
        if stat:
            return redirect(f'/doc/view/{doc_seq}')
        return "Whoops!"
