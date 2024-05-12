from app import app
from src.utils.template_utils import send_template
from src.utils.db_utils import connect
from flask import request, session, redirect


@app.route("/auth/login/", methods=['GET'])
def get_login():
    return send_template("auth/login.liquid")

@app.route("/auth/login/", methods=['POST'])
def post_login():
    with connect() as conn:
        data = dict(request.form)
        username = data['uName']
        password = data['pWord']
        otp = data['OTP']
        is_valid, userID, user_name = conn.check_user_valid(
                                                                username,
                                                                password,
                                                                otp
                                                            )
        if is_valid:
            session['user'] = conn.get_user_by_seq(userID)
            # return send_template("auth/")
            return redirect('/')
        return send_template("auth/login.liquid")