from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect



@app.get('/finances/create/')
def get_finances_new():
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