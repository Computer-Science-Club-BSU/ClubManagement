"""Handles requests regarding user registration"""
import logging
from flask import request
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

logger = logging.getLogger('RegistrationAssistant')

@app.route('/auth/register/', methods=['GET'])
def get_auth_register():
    """Serves the registration page to users"""
    # deepcode ignore XSS: All data from DB is sterilized with Bleach Clean
    return render_template('auth/register.liquid')

@app.route('/auth/register/', methods=['POST'])
def post_auth_register():
    """Handles submitted requests to register a new user account"""
    with connect() as conn:
        logger.log("New registration request received. Name: %s %s, Email: %s",
                    request.form.get('email'),
                    request.form.get('fName'),
                    request.form.get('lName')
                    )
        res, _ = conn.add_requested_user(request.form) #pylint: disable=unpacking-non-sequence
        if res:
        # deepcode ignore XSS: All data from DB is sterilized with Bleach Clean
            return render_template('auth/register.liquid',
                                   error_msg="User created successfully!"\
                                   "You should receive an email when your "\
                                       "request has been completed.")
        # deepcode ignore XSS: All data from DB is sterilized with Bleach Clean
        return render_template('auth/register.liquid',
                                error_msg="Your request could not be "\
                                    "processed at this time.\\n"\
                                    "If this error continues, please "
                                    "contact your system administrators.")
