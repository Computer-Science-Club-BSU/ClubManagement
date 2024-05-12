from app import app
from flask_liquid import render_template as _render
from flask import session
from src.utils.db_utils import connect

def send_template(template_name, **context):
    user_data = {"logged_in": True} | session.get("user",
                                                  {
                                                        "theme": 1,
                                                        "logged_in": False,
                                                        "permissions": {
                                                            "doc_admin": True,
                                                            "fin_admin": True
                                                        }
                                                   }
                                                )
    with connect() as conn:
        config = conn.get_config()
        return _render(template_name, **context, user=user_data,
                       config=config,doc_dash=['Pending Items'])
