from flask import session
from app import app
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

@app.route('/terms/view', methods=['GET'])
def get_terms_view():
    with connect() as conn:
        terms = conn.get_terms_formatted(session['user_seq'])
        return render_template('terms/view.liquid', terms=terms)
