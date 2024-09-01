"""Handles requests relating to docket editing"""
from flask import request, session, redirect, abort
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/doc/edit/<doc_seq>', methods=['GET'])
def get_doc_edit(doc_seq):
    """Handles requests for /doc/edit/
    Gets docket seq and sends back file to allow for modifications."""
    with connect() as conn:
        doc = conn.get_all_docket_data_by_seq(doc_seq)
        if doc['locked'] == True:
            abort(423)
        status = conn.get_docket_statuses()
        vote_types = conn.get_docket_vote_types()
        docket_users = conn.get_docket_users()
    # deepcode ignore XSS: All results from DB are run through bleach clean
    return render_template('doc/mod.liquid', doc=doc, status=status,
                           vote_types=vote_types, docket_users=docket_users)

@app.route('/doc/edit/', methods=['POST'])
def post_doc_edit():
    """Handles submitted edit forms for docket.
    Updates database record based on data submitted from form"""
    doc_seq = request.args.get('seq')
    user_seq = session.get('user_seq')
    with connect() as conn:
        if conn.is_doc_locked(doc_seq):
            abort(423)
        title = request.form.get('title')
        body = request.form.get('body')
        if body.strip() == '':
            return "Body cannot be blank!", 400
        if title.strip() == '':
            return "Title cannot be blank!", 400
        status = request.form.get('stat')
        vote_type = request.form.get('vote')
        res, _ = conn.update_docket( #pylint: disable=unpacking-non-sequence
            doc_seq,
            title,
            body,
            user_seq,
            status,
            vote_type
            )
        if res:
            return redirect(f'/doc/view?seq={doc_seq}')
        return "Error!"

@app.post("/doc/attach/<doc>")
def post_doc_attach(doc):
    """Handles requests to attach files to docket"""
    # /doc/attach/{{ doc.docket.seq }}
    user_seq = session.get('user_seq')
    with connect() as conn:
        res, _ = conn.add_docket_attachment(doc, request.json, user_seq)#pylint: disable=unpacking-non-sequence
        if res:
            return "Docket Record added successully", 201
        return "Error adding attachment", 400

@app.post('/doc/update_assignees/<doc>')
def post_doc_update_assignees(doc):
    """Handles requests to update docket assignees"""
    user_seq = session.get('user_seq')
    with connect() as conn:
        data = request.form.getlist('assignees')
        res, _ = conn.update_docket_assignees(doc, data, user_seq)#pylint: disable=unpacking-non-sequence
        if res:
            return "Assignee added successfully", 201
        return "Error adding assignee", 400
