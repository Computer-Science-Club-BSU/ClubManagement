from app import app
from src.utils.template_utils import render_template
from flask import request, session, redirect, Response
from src.utils.db_utilities import connect
import logging


handler = logging.FileHandler('logs/access.log')        
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logger = logging.getLogger("AuthManager")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)



@app.route("/auth/login", methods=['GET'])
@app.route("/auth/login/", methods=['GET'])
def get_auth_login():
    return Response(render_template("auth/login.liquid"), mimetype='text/html')


@app.route("/auth/login", methods=['POST'])
@app.route("/auth/login/", methods=['POST'])
def post_auth_login():
    with connect() as conn:
        username = request.form.get('uname')
        logger.info(f"New Login request for username: {username}")
        password = request.form.get('pword')
        seq = conn.authorize_user(username, password)
        if seq == -1:
            logger.warn(f"Login Attempt Failed")
            return Response(render_template("auth/login.liquid",
                                    err="Invalid username or password"),
                                    mimetype='text/html')
        session['user_seq'] = seq
        logger.info(f"{username} Logged in successfully")

        return redirect('/')

@app.route("/auth/logout")
@app.route("/auth/logout/")
def auth_logout():
    session.clear()
    return redirect('/')