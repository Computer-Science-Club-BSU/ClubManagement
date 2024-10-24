"""Serves requests pertaining to creation of finances"""
from flask import request, session, abort
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.get('/finances/create/')
def get_finances_create():
    """Serves the /finances/create/ GET request.
    Returns a template with all users who can add finances,
    approve finances, as well as statuses and types for finances."""
    with connect() as conn:
        users = conn.get_finance_users()
        approvers = conn.get_finance_approvers()
        statuses = conn.get_finance_statuses()
        types = conn.get_finance_types()
    return render_template('fin/create.liquid',
                           finance_users=users,
                           approvers=approvers,
                           finance_types=types,
                           statuses=statuses)

@app.post('/finances/create/')
def post_finances_create():
    """Serves the /finances/create/ POST request."""
    with connect() as conn:
        data = request.json
        if data['header']['id'] == '':
            return "ID Cannot be blank!", 400
        res, e = conn.create_finance_record(
            data,
            session['user_seq']
        )
    if res:
        return ""
    abort(400)

@app.post('/finances/create/validate')
def post_finances_create_validate():
    with connect() as conn:
        date = conn.date_check(request.json['recordDate'])
    if date:
        return "", 200
    else:
        return "This record is outside the allowed finance window. Please proceed with caution", 200
    return str(e), 400

