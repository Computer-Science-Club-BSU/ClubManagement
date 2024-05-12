from app import app
from src.utils.template_utils import send_template


@app.route("/")
def get_root():
    return send_template("index.liquid")