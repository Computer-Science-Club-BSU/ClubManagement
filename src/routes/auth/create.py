from src.utils.db_utils import connect
from app import app
from src.utils.template_utils import send_template
import pyotp
import time
from flask import request, session
import qrcode
import tempfile
import base64

@app.route("/auth/create", methods=['GET'])
def get_create_user():
    return send_template("auth/create.liquid")

@app.route("/auth/create", methods=['POST'])
def post_create_user():
    data = dict(request.form)
    # Insert into database
    with connect() as conn:
        OTP_URI = conn.store_user(data)
        with tempfile.NamedTemporaryFile('wb+') as f:
            img = qrcode.make(OTP_URI)
            img.save(f.name)

            f.seek(0)
            img_data = base64.b64encode(f.read()).decode()
            full_name = data.get('fName') + data.get('lName')
            session['user'] = conn.get_user_by_full_name(full_name)

            # Send template to authenticate
            return send_template("auth/OTP.liquid",
                                uri = OTP_URI,
                                otp_qr_data = img_data)
