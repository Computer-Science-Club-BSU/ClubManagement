"""Handles requests for viewing docket"""

import bleach
from flask import Response
import logging
import tempfile
from flask import session, send_file
from app import app
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template


logger = logging.getLogger('DocketView')

@app.route('/doc/view/', methods=['GET'])
def get_doc_view():
    """Handles /doc/view/. Gets records from db and renders template"""

    with connect() as conn:
        records = conn.get_all_non_archived_docket()

        # deepcode ignore XSS: All data from DB is sterilized with Bleach Clean
        return render_template("doc/view.liquid", results=records)


@app.route('/doc/view/<seq>', methods=['GET'])
def get_doc_view_by_seq(seq):
    """Handled /doc/view with a number provided after. Gets record from DB and
    renders resulting data"""

    with connect() as conn:
        records = conn.get_all_docket_data_by_seq(seq)

        user_seq = session.get('user_seq')
        can_user_edit = conn.can_user_edit_docket(user_seq,seq)
        attachments = conn.get_docket_attachments_summary(seq)
        # deepcode ignore XSS: All data from DB is sterilized with Bleach Clean
        return render_template("doc/view_single.liquid", doc=records,
                               can_user_edit=can_user_edit,
                               attachments=attachments)

@app.get('/doc/attach/<attach_seq>')
def get_doc_attach(attach_seq):
    """Handles requests to get docket attachment"""
    with connect() as conn:
        name, data = conn.get_docket_attachment(attach_seq)
        name = name.replace('../', '')
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(tmpdir + '/' + name, 'wb') as f:
                f.write(data)
            return send_file(tmpdir + '/' + name)
