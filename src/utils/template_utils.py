from flask_liquid import render_template as _render
from flask import session
import json


def render_template(template_name, **context):
    public_config = load_config()['public']
    user_seq = session.get('user_seq')
    return _render(template_name, **context, **public_config)


def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)