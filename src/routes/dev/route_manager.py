"""Contains functions relating to maintaining routes and system endpoints"""
from flask import request, session
from app import app
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

@app.get('/dev/path_audit/')
def get_dev_path_audit() -> str:
    """Serves the /dev/path_audit/ path from the web interface"""
    paths = list({x.endpoint for x in app.url_map.iter_rules()})
    paths.sort()
    with connect() as conn:
        path_rules = conn.get_all_path_rules()
        path_rules = {x.get('path_func_name'): x for x in path_rules} # path_rules is executed with the convert_to_dict decorator. pylint: disable=not-an-iterable
        print(path_rules)

        return render_template('dev/audit.liquid', paths=paths,
                            rules=path_rules)


@app.get('/dev/path_audit/edit/<string:endpoint>')
def get_path_audit_edit(endpoint: str) -> str:
    with connect() as conn:
        perms = conn.get_permission_data()
        plugins = conn.get_plugins()
        return render_template("dev/edit_path.liquid", endpoint=endpoint, db_perms=perms, plugins=plugins)

@app.post('/dev/path_audit/edit/')
def post_path_audit_edit() -> tuple[str, int|None]:
    data = request.json
    with connect() as conn:
        res, _ = conn.update_path_permission(data, session['user_seq'])
    if res:
        return "", 200
    return "", 400
