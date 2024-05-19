from app import app
from src.utils.template_utils import render_template
from flask import request, session, redirect
from src.utils.db_utilities import connect
import logging


@app.route("/auth/login", methods=['GET'])
@app.route("/auth/login/", methods=['GET'])
def get_auth_login():
    return render_template("auth/login.liquid")


@app.route("/auth/login", methods=['POST'])
@app.route("/auth/login/", methods=['POST'])
def post_auth_login():
    with connect() as conn:
        username = request.form.get('uname')
        password = request.form.get('pword')
        seq = conn.authorize_user(username, password)
        if seq == -1:

            return render_template("auth/login.liquid",
                                    err="Invalid username or password")
        session['user_seq'] = seq
        return redirect('/')

@app.route("/auth/logout")
@app.route("/auth/logout/")
def auth_logout():
    session.clear()
    return redirect('/')