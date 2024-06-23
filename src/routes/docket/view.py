from app import app
from flask import session, request, abort, send_file
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template
import logging
import tempfile

logger = logging.getLogger('DocketView')

@app.route('/doc/view', methods=['GET'])
@app.route('/doc/view/', methods=['GET'])
def get_doc_view():    
    
    if len(request.args.keys()) >= 1:
        return get_doc_view_by_seq()
    
    with connect() as conn:
        records = conn.get_all_non_archived_docket()
        return render_template("doc/view.liquid", results=records)
    
def get_doc_view_by_seq():
    
    if (seq := request.args.get('seq')) is None:
        abort(400)
    
    
    with connect() as conn:
        records = conn.get_all_docket_data_by_seq(seq)
        user_seq = session.get('user_seq')
        can_user_edit = conn.can_user_edit_docket(user_seq,seq)
        attachments = conn.get_docket_attachments_summary(seq)
        return render_template("doc/view_single.liquid", doc=records,
                               can_user_edit=can_user_edit,
                               attachments=attachments)

@app.get('/doc/attach/<attach_seq>')
def get_doc_attach(attach_seq):
    with connect() as conn:
        name, data = conn.get_docket_attachment(attach_seq)
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(tmpdir + '/' + name, 'wb') as f:
                f.write(data)
            return send_file(tmpdir + '/' + name)
            