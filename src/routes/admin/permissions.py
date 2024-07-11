"""Handles requests pertaining to Admin Permission Assignment endpoints"""
from logging import getLogger
from flask import request, session
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

logger = getLogger("AdminPermissions")

@app.route('/admin/permissions/', methods=['GET'])
def get_admin_permissions():
    """Handles requests to /admin/permissions [GET].
    Gets perms, classes, and class perms and
    renders a form to users for editing"""
    with connect() as conn:
        perm_desc = conn.get_permission_data()
        db_classes=conn.get_user_classes()
        class_perms = conn.get_class_perms()
    return render_template('admin/permissions.liquid',
                           perm_descs=perm_desc,
                           db_classes=db_classes,
                           class_perms=class_perms)

@app.route('/admin/permissions/edit', methods=['POST'])
def post_admin_permissions_edit():
    """Handles requests to /admin/permissions/edit [POST]
    Updates all information in the DB regarding permissions."""
    user_seq = session.get('user_seq')
    with connect() as conn:
        perms = conn.get_all_db_perms()
        for perm in perms: #pylint: disable=not-an-iterable
            seq = perm['seq']
            stat = request.form.get(str(seq), 'off')
            res, _ = conn.update_permissions(seq, stat == 'on', user_seq) #pylint: disable=unpacking-non-sequence
            if not res:
                return "Err", 400
    return "Success"

@app.route('/admin/permissions/class/new', methods=['POST'])
def post_admin_permissions_class_new():
    """Handles /admin/permissions/class/new [POST]
    Creates a new class in the database and adds in all permission fields."""
    class_name = request.json['name']
    user = session.get('user_seq')
    with connect() as conn:
        res, _ = conn.create_class(class_name, user) #pylint: disable=unpacking-non-sequence
    if res:
        return "Success"
    return "Failed", 500
