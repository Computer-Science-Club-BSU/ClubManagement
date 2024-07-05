from flask_liquid import render_template as _render
from flask import session
import json
from src.utils.db_utilities import connect


def render_template(template_name, **context):
    public_config = load_config()['public']
    user_seq = session.get('user_seq')
    nav_pages = [
                "home.liquid",
                "quick_links.liquid"
            ]
    with connect() as conn:
        nav_pages.extend(conn.get_nav_pages())
        nav_pages.append('account.liquid')
        if user_seq is not None:

            (user,
             perms,
             classes,
             fin_dash,
             doc_dash) = conn.get_user_by_seq(user_seq)

            
            return _render(template_name, **context, **public_config,
                        isLoggedIn=True, user=user, perms=perms,
                        classes=classes,finance_dashboards=fin_dash,
                        docket_dashboards=doc_dash,
                        nav_pages=nav_pages)

        else:
            return _render(template_name, **context, **public_config,
                        nav_pages=nav_pages)


def load_config():
    with open('/etc/cms/config.json', 'r') as f:
        return json.load(f)