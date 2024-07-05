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
        users = conn.get_users()
        assignments = conn.get_assignments()
    return render_template('admin/class_assignments.liquid',
                           db_classes=classes,
                           users=users,
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
