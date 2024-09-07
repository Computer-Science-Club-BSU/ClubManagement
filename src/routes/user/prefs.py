from flask import request, session, abort
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect


@app.get('/user/preferences')
def get_user_preferences():
    if 'user_seq' not in session:
        abort(401)
    return render_template('user/prefs.liquid')