from flask import session, abort, request, redirect
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from src.utils.auth_utils import validate_password

@app.get('/user/preferences')
def get_user_preferences(err_msg: str|None = None):
    if 'user_seq' not in session:
        abort(401)
    with connect() as conn:
        titles = conn.get_standard_titles()
    return render_template('user/prefs.liquid', titles=titles,
                           err_msg=err_msg)

@app.post('/user/preferences/general/')
def post_user_prefs_general():
    if 'user_seq' not in session:
        abort(401)
    with connect() as conn:
        res, _ = conn.update_user_prefs(
            request.form, session.get('user_seq')
            )
    if res:
        return redirect('/user/preferences')
    else:
        
        return get_user_preferences(err_msg='Failed to update user'\
                                        ' preferences. Please contact a user '\
                                        'administrator for more information.')
    
@app.post('/user/preferences/security/')
def post_user_prefs_security():
    if 'user_seq' not in session:
        abort(401)
    existing_pw = request.form.get('current')
    new_pw = request.form.get('new')
    conf_pw = request.form.get('confirm')
    res = validate_password(new_pw, conf_pw)
    with connect() as conn:
        if not conn.check_existing_password(
            session['user_seq'], existing_pw):
            return get_user_preferences(err_msg='Existing password doesn\'t'\
                                        ' match password on file.') 
        if not res:
            return get_user_preferences(err_msg='Password must contain at'\
                                        ' least one of the following:\n'\
                                        '* One Uppercase\n*One Lowercase\n'\
                                        '* One Number\n*One Special Character')
        res, _ = conn.update_user_password(
            new_pw, session['user_seq']
            )
    if res:
        return redirect('/user/preferences')
    else:
        return get_user_preferences(err_msg='Failed to update user'\
                                        ' preferences. Please contact a user '\
                                        'administrator for more information.')
