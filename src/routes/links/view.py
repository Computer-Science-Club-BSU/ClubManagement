from app import app
from flask import redirect, abort
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

@app.route('/links/', methods=['GET'])
def get_links():
    with connect() as conn:
        links = conn.get_all_links()
        return render_template("links/view.liquid", links=links)