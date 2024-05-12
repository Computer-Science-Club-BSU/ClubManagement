from app import app
from flask import session, redirect, request
from src.utils.db_utils import connect
from src.utils.template_utils import send_template
import tempfile
import qrcode
import base64

@app.route("/auth/otp/verify", methods=['POST'])
def verify_otp():
    print(session)
    user_id = session['user']['_id']
    with connect() as conn:
        if conn.check_user_otp(user_id, request.form.get('OTP')):
            return redirect('/')
        else:
            with tempfile.NamedTemporaryFile('wb+') as f:
                OTP_URI = conn.get_totp(user_id)
                img = qrcode.make(OTP_URI)
                img.save(f.name)

                f.seek(0)
                img_data = base64.b64encode(f.read()).decode()

                # Send template to authenticate
                return send_template("auth/OTP.liquid",
                                    uri = OTP_URI,
                                    otp_qr_data = img_data)
            