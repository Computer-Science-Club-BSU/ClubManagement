from flask import session, request
from app import app
from src.utils.db_utilities import connect

@app.post('/links/new/')
def post_links_new():
    with connect() as conn:
        target = request.json['link_target']
        link = request.json['link_origin']
        date = request.json['link_date']
        user = session.get('user_seq')
        resp, _ = conn.create_link(link, target, date, user)
    if resp:
        return "OK"
    return "Could not create link", 400