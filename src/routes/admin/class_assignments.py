"""Handles routes pertaining to Administrative Class Assignment Endpoints"""
from logging import getLogger
from flask import request, session
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

logger = getLogger("AdminClassAssignments")

@app.get('/admin/class_assignments')
def get_admin_class_assignments():
    """Handles requests for admin/class_assignment [GET].
    Constructs a list of users and classes and renders them to the user
    """
    with connect() as conn:
        classes = conn.get_user_classes()
        assignments = conn.get_assignments()
    return render_template('admin/class_assignments.liquid',
                           db_classes=classes,
                           assignments=assignments)



@app.get('/admin/edit_assignment/<seq>')
def get_admin_edit_assignment(seq):
    """Handles requests for admin/edit_assignment [GET].
    Renders a form to update details about a user's class assignment
    """
    with connect() as conn:
        data = conn.get_class_assignment_by_seq(seq)
        classes = conn.get_user_classes()
        terms = conn.get_terms()
        return render_template('admin/edit_assignment.liquid',data=data,
                               _classes=classes,
                               terms=terms)

@app.get('/admin/create_assignment/')
def get_admin_create_assignment():
    """Handles requests for admin/edit_assignment [GET].
    Renders a form to update details about a user's class assignment
    """
    with connect() as conn:
        users = conn.get_users()
        classes = conn.get_user_classes()
        terms = conn.get_terms()
        return render_template('admin/create_assignment.liquid',
                               users=users,
                               _classes=classes,
                               terms=terms)


@app.post('/admin/create_assignment/')
def post_admin_create_assignment():
    """Handles requests for admin/edit_assignment [POST].
    Handles form updates and sends changes to DB
    """
    user = request.json.get('user')
    _class = request.json.get('role')
    start = request.json.get('start')
    end = request.json.get('end')
    user_seq = session.get('user_seq')
    with connect() as conn:
        res, _ = conn.create_class_assignment(user, #pylint: disable=unpacking-non-sequence
                                              _class,
                                              start,
                                              end,
                                              user_seq)
        if res:
            return "", 200
        return "", 400


@app.post('/admin/edit_assignment/<seq>')
def post_admin_edit_assignment(seq):
    """Handles requests for admin/edit_assignment [POST].
    Handles form updates and sends changes to DB
    """
    _class = request.json.get('role')
    start = request.json.get('start')
    end = request.json.get('end')
    user_seq = session.get('user_seq')
    with connect() as conn:
        res, _ = conn.update_class_assignment(seq, #pylint: disable=unpacking-non-sequence
                                              _class,
                                              start,
                                              end,
                                              user_seq)
        if res:
            return "", 200
        return "", 400

@app.post('/admin/delete_assignment/<seq>')
def post_admin_delete_assignment(seq):
    with connect() as conn:
        user_seq = session.get('user_seq')
        res, _ = conn.delete_class_assignment(seq, user_seq)  #pylint: disable=unpacking-non-sequence
    
    if res:
        return "",200
    return "", 400
