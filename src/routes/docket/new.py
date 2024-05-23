from app import app
from flask import session, request, abort
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template
import logging
from src.utils.permission_checker import check_perms

logger = logging.getLogger('DocketNew')

@app.route('/doc/create', methods=['GET'])
@app.route('/doc/create/', methods=['GET'])
def get_new_docket_item():
    check_perms(request, session.get('user_seq'), logger)
    
    with connect() as conn:
        records = conn.get_all_non_archived_docket()
        return render_template("doc/view.liquid", results=records)
