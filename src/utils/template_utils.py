from flask_liquid import render_template as _render
from flask import session
import json
from src.utils.db_utilities import connect


def render_template(template_name, **context):
    public_config = load_config()['public']
    user_seq = session.get('user_seq')
    if user_seq is not None:
        with connect() as conn:
            (user,
             perms,
             classes,
             fin_dash,
             doc_dash) = conn.get_user_by_seq(user_seq)
            print(user,
             perms,
             classes,
             fin_dash,
             doc_dash) 
        return _render(template_name, **context, **public_config,
                       isLoggedIn=True, user=user, perms=perms,
                       classes=classes,finance_dashboards=fin_dash,
                       docket_dashboards=doc_dash)
            
    else:
        return _render(template_name, **context, **public_config)


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)