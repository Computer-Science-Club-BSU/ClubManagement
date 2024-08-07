"""Contains functions relating to maintaining routes and system endpoints"""
from app import app
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

@app.get('/dev/path_audit/')
def get_dev_path_audit() -> str:
    """Serves the /dev/path_audit/ path from the web interface"""
    paths = list({x.endpoint for x in app.url_map.iter_rules()})
    with connect() as conn:
        path_rules = conn.get_all_path_rules()
        path_rules = {x.get('path_func_name'): x for x in path_rules} # path_rules is executed with the convert_to_dict decorator. pylint: disable=not-an-iterable
        print(path_rules)

        return render_template('dev/audit.liquid', paths=paths,
                            rules=path_rules)
