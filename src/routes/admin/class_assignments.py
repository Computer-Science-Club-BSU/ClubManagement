from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from flask import request, session
from logging import getLogger

logger = getLogger("AdminClassAssignments")

@app.get('/admin/class_assignments')
def get_admin_class_assignments():
    with connect() as conn:
        classes = conn.get_user_classes()
        users = conn.get_users()
        assignments = conn.get_assignments()
    return render_template('admin/class_assignments.liquid',
                           db_classes=classes,
                           users=users,
                           assignments=assignments)

@app.post('/admin/assignments/edit')
def post_admin_assignments_edit():
    user_seq = session.get('user_seq')
    with connect() as conn:
        perms = conn.get_assignments()
        for perm in perms:
            seq = perm['seq']
            stat = request.form.get(str(seq), 'off')
            res, _ = conn.update_permissions(seq, stat == 'on', user_seq)
            if not res:
                return "Err", 400
    return "Success"