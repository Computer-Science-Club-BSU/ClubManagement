import logging
from flask import request
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from src.utils.auth_utils import validate_password

logger = logging.getLogger('ForgotPassword')


@app.post('/forgot_password')
def post_forgot_password():
    logger.warning("Password reset requested for username %s", request.json.get('username'))
    with connect() as conn:
        conn.create_password_reset(
            request.json.get('username'),
            request)
    return "If the username provided is in our system, an email will be sent out with a link to reset your password.", 200



@app.post('/forgot_password/<string:token>')
def post_forgot_password_token(token: str):
    result = validate_password(request.form['password'], request.form['c_password'])
    if result == True:
        with connect() as conn:
            conn.reset_password_token(token, request.form)
        return render_template('auth/forgot_password.liquid', token=token,
                               resp="If the token provided matches our records, then your password has been reset."), 200
    return render_template('auth/forgot_password.liquid', token=token, resp=result), 400
    return render_template('auth/forgot_password.liquid', token=token, resp=result), 400
