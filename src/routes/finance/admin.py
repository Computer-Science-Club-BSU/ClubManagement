from flask import request, session
from logging import getLogger
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

logger = getLogger('FinanceAdministrator')

@app.get('/finances/admin/')
def get_finances_admin():
    with connect() as conn:
        data = conn.get_finance_admin_data()
    return render_template('fin/admin.liquid', records=data)


@app.delete('/finance/delete/')
def delete_finances_delete():
    data = request.json
    with connect() as conn:
        user_seq = conn.authorize_user(data['username'], data['password'])
        can_delete = conn.can_user_delete_finance(user_seq)
        if user_seq != -1 and can_delete:
            logger.warning('UserSeq %s submitted delete request for record %s. Authorized as: %s',
                           session['user_seq'], data['seq'], user_seq)
            res, _ = conn.delete_finance_rec(data['seq'])
            if res:
                return "Record Deleted", 200
            return "Failed to delete record", 500
        elif user_seq != -1 and not can_delete:
            return "User cannot delete finances", 401
        elif user_seq == -1:
            return "Could not validate user.", 403