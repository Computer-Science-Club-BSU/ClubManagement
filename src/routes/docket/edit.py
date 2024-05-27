from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from flask import request, session, redirect

@app.route('/doc/edit/', methods=['GET'])
@app.route('/doc/edit', methods=['GET'])
def get_doc_edit():
    doc_seq = request.args.get('seq')
    with connect() as conn:
        doc = conn.get_all_docket_data_by_seq(doc_seq)
        status = conn.get_docket_statuses()
        vote_types = conn.get_docket_vote_types()
    return render_template('doc/mod.liquid', doc=doc, status=status,
                           vote_types=vote_types)

@app.route('/doc/edit/', methods=['POST'])
@app.route('/doc/edit', methods=['POST'])
def post_doc_edit():
    doc_seq = request.args.get('seq')
    user_seq = session.get('user_seq')
    with connect() as conn:
        title = request.form.get('title')
        body = request.form.get('body')
        status = request.form.get('stat')
        vote_type = request.form.get('vote')
        print(status, vote_type)
        res, _ = conn.update_docket(
            doc_seq,
            title,
            body,
            user_seq,
            status,
            vote_type,
            )
        if res:
            return redirect(f'/doc/view?seq={doc_seq}')
        else:
            return "Error!"
