"""Contains all functions pertaining to sending emails from web interface"""
from flask import request, session, abort
from app import app
from src.utils.template_utils import render_template, load_config
from src.utils.db_utilities import connect

@app.route('/email/compose/', methods=['GET'])
def get_email_compose():
    """Handle /email/compose/ requests [GET]
    Returns the email composition form."""
    return render_template('email/compose.liquid')

@app.route('/email/preview/', methods=['POST'])
def post_email_preview():
    """Handles /email/preview/ requests [POST]
    Creates an email draft and renders the draft to the user."""
    body = request.form.get('emailBody')
    config = load_config()
    with connect() as conn:
        user_seq = session.get('user_seq')
        user = conn.get_user_by_seq(user_seq)
        subject = request.form.get('subject')
        position = request.form.get('position')
        user_classes = conn.get_user_classes_by_user_seq(user_seq)
        if position not in [
            result['position_name'] for result in user_classes #pylint: disable=not-an-iterable
        ]:
            abort(403)
        sig_fname = user[0].get('first_name')
        sig_lname = user[0].get('last_name')
        body += f"""<p>{sig_fname} {sig_lname}<br>
        {position} | {config['public']['sys_name']}<br>
        {config['public']['sys_loc']}
        <p>"""
        to = request.form.get('to').split(';')
        cc = request.form.get('cc').split(';')
        bcc = request.form.get('bcc').split(';')
        res, seq = conn.create_email(subject, body, user_seq, to, cc, bcc)
    if res:
        return render_template('email/preview.liquid', body=body, id=seq)
    return "Error, could not preview email!"

@app.route('/email/send', methods=['POST'])
def post_send_email():
    """Handles requests to /email/send [POST]. Sends email ID requested"""
    user = session.get('user_seq')
    with connect() as conn:
        email_id = request.args.get('seq')
        res, _ = conn.mark_email_for_sending(email_id, user) #pylint: disable=unpacking-non-sequence
        if res:
            return "Email marked for sending"
        return "Failed to mark email for sending, 500"
