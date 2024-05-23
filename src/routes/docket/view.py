from app import app
from flask import session, request, abort
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template
import logging

logger = logging.getLogger('DocketView')

@app.route('/doc/view', methods=['GET'])
@app.route('/doc/view/', methods=['GET'])
def get_doc_view():
    if 'user_seq' not in session:
        logger.error(
            f'[401] User {request.remote_addr} attempted to load /doc/view')
        abort(401)
    
    with connect() as conn:
        user_perms = conn.get_user_perms_by_user_seq(session['user_seq'])
        if (user_perms['doc_view'] | user_perms['doc_admin']) != 1:
            user = conn.get_user_data_by_seq(session['user_seq'])
            logger.error(
                f'[403] User {user['user_name']} attempted to load /doc/view.')
            abort(403)
        records = conn.get_all_non_archived_docket()
        return render_template("doc/view.liquid", results=records)
    
@app.route('/doc/view/<int:seq>', methods=['GET'])
def get_doc_view_by_seq(seq: int):
    if 'user_seq' not in session:
        logger.error(
            f'[401] User {request.remote_addr} attempted to load /doc/view')
        abort(401)
    with connect() as conn:
        user_perms = conn.get_user_perms_by_user_seq(session['user_seq'])
        if (user_perms['doc_edit'] | user_perms['doc_admin']) != 1:
            user = conn.get_user_data_by_seq(session['user_seq'])
            logger.error(
                f'[403] User {user['user_name']} attempted to load /doc/view.')
            abort(403)
        records = conn.get_all_docket_data_by_seq(seq)
        print(records)
        return render_template("doc/view_single.liquid", doc=records)
