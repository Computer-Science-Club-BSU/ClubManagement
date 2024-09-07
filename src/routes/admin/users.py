from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from flask import request, session


@app.get('/admin/users/view')
def get_admin_users_view():
    with connect() as conn:
        users = conn.get_user_info()
    return render_template('admin/users/view.liquid', users=users)

@app.get('/admin/users/create')
def get_admin_users_create():
    with connect() as conn:
        terms = conn.get_terms()
        classes = conn.get_user_classes()
        titles = conn.get_all_titles()
        themes = conn.get_themes()
        tz = conn.get_timezones()
        date_formats = conn.get_all_date_formats()
    return render_template('admin/users/create.liquid', terms=terms, db_classes=classes, titles=titles,
                           themes=themes, tz=tz, formats=date_formats)

@app.post('/admin/users/create/')
def post_admin_users_create():
    with connect() as conn:
        user_obj = request.json
        res, data = conn.add_user(user_obj, session, request)

    if res:
        return str(data), 400
    return '', 200

@app.get('/admin/users/admin')
def get_admin_users_administrate():
    with connect() as conn:
        users = conn.get_user_info()
        titles = conn.get_all_titles()
        themes = conn.get_themes()
    return render_template('admin/users/admin.liquid', users=users,
                           themes=themes, titles=titles)

@app.post('/admin/users/admin')
def post_admin_users_administrate():
    body = request.json
    with connect() as conn:
        res, err = conn.update_user(body, session['user_seq'])
    if res:
        return "ok", 200
    return str(err), 400



@app.post('/admin/users/reset')
def post_admin_users_reset():
    with connect() as conn:
        res, err = conn.create_password_reset_admin(request.json['seq'], request, session)
    if res:
        return "Password reset request successful", 200
    raise err

@app.post('/admin/users/update_locale/')
def post_admin_users_update_locale():
    print(request.json)
    with connect() as conn:
        res, err = conn.update_user_locale(request.json['target'],
                                           request.json['timezone'],
                                           request.json['datetime_format'],
                                           session['user_seq'])
    if res:
        return "Update locale request successful", 200
    else:
        return err, 500


@app.post('/admin/users/change_user_state')
def post_admin_users_change_user_state():
    with connect() as conn:
        res, err = conn.change_user_state(request.json['seq'],request.json['state'], session['user_seq'])
    if res:
        return "State change request successful", 200
    return err, 500


@app.get('/admin/users/edit/<seq>')
def get_admin_users_edit_seq(seq):
    with connect() as conn:
        user = conn.get_user_data_by_seq(seq)
        audit = conn.get_user_audit(seq)
        themes = conn.get_themes()
        tz = conn.get_timezones()
        tclasses = conn.get_user_classes_by_user_seq(seq)
        date_formats = conn.get_all_date_formats()
        titles = conn.get_all_titles()
    print(titles)
    return render_template('admin/users/edit.liquid', tuser=user, audit=audit, themes=themes,
                           tz=tz, tclasses=tclasses, formats=date_formats, titles=titles)

@app.post('/admin/users/general/<seq>')
def post_admin_users_update(seq):
    with connect() as conn:
        res, err = conn.update_user_prefs(seq, request.form, session.get('user_seq'))
    if res:
        return "User preferences updated successfully", 200
    return err, 500
