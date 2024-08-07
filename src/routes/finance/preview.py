"""Serves routes pertaining to Finance Preview requests"""
from flask import request
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.post('/finances/new/preview/')
def post_finances_new_preview():
    """Serves requests for /finances/new/preview/.
    Loads the data from the POST request and serves back a rendered preview of
    a financial statement"""
    finance_data = request.json
    header = finance_data['header']
    lines = finance_data['lines']
    with connect() as conn:
        types = conn.get_finance_type_by_seq(header['type'])
        header['type'] = types.get('type_desc').upper()
        creator_user = conn.get_user_by_seq(header.get('creator'))
        creator = creator_user[0]
        header['creator'] = creator.get('first_name', '') + \
            ' ' + creator.get('last_name', '')
        if header.get('approver') == '':
            header['approver'] = 'Not Approved'
        else:
            approver_user = conn.get_user_by_seq(header.get('approver'))
            approver = approver_user[0]
            header['approver'] = approver.get('first_name', '') + \
            ' ' + approver.get('last_name', '')

    return render_template('fin/finance_record.liquid',
                           li=lines,
                           header=header)
