from flask import request, session
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.get('/finances/edit/<seq>')
def get_finances_edit(seq):
    with connect() as conn:
        header, lines = conn.get_finance_object_for_edit(seq)
        users = conn.get_finance_users()
        approvers = conn.get_finance_approvers()
        statuses = conn.get_finance_statuses()
        types = conn.get_finance_types()
        return render_template('fin/create.liquid', header=header, lines=lines, finance_users=users,
                           approvers=approvers,
                           finance_types=types,
                           statuses=statuses)


@app.post('/finances/edit/<seq>')
def post_finances_edit(seq):
    record = request.json
    with connect() as conn:
        res, err = conn.update_finance_object(seq, record, session['user_seq'])

    if res:
        return "", 200
    return str(err), 400
