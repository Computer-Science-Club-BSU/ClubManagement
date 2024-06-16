from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from flask import request
from datetime import datetime

@app.post('/finances/new/preview/')
def post_finances_new_preview():
    finance_data = request.json
    header = finance_data['header']
    lines = finance_data['lines']
    print(request.json)
    with connect() as conn:
        header['type'] = conn.get_finance_type_by_seq(header['type'])['type_desc'].upper()
        creator_user = conn.get_user_by_seq(header.get('creator'))
        creator = creator_user[0]['first_name'] + \
            ' ' + creator_user[0]['last_name']
        header['creator'] = creator
        if header.get('approver') == '':
            header['approver'] = 'Not Approved'
        else:
            approver_user = conn.get_user_by_seq(header.get('approver'))
            header['approver'] = approver_user[0]['first_name'] + \
            ' ' + approver_user[0]['last_name']
    
    return render_template('fin/finance_record.liquid',
                           li=lines,
                           header=header)

@app.route('/test/')
def test_finance_preview():
    finance_data={'header': {'id': '', 'creator': '1', 'approver': '', 'status': '1', 'inv_date': '2024-06-16', 'type': '1', 'tax': '0.00', 'fees': '0.00', 'total': '0.00'}, 'lines': []}
    header = finance_data['header']
    lines = finance_data['lines']
    with connect() as conn:
        header['type'] = conn.get_finance_type_by_seq(header['type'])['type_desc'].upper()
        creator_user = conn.get_user_by_seq(header.get('creator'))
        creator = creator_user[0]['first_name'] + \
            ' ' + creator_user[0]['last_name']
        header['creator'] = creator
        if header.get('approver') == '':
            header['approver'] = 'Not Approved'
        else:
            approver_user = conn.get_user_by_seq(header.get('approver'))
            header['approver'] = approver_user[0]['first_name'] + \
            ' ' + approver_user[0]['last_name']
    return render_template('fin/finance_record.liquid',
                           li=lines,
                           header=header)