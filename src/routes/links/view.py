from app import app
from flask import redirect, abort, request, session
from src.utils.db_utilities import connect
from src.utils.template_utils import render_template

@app.route('/links/', methods=['GET'])
def get_links():
    with connect() as conn:
        links = conn.get_all_links()
        return render_template("links/view.liquid", links=links)

@app.get('/links/quick_links')
def get_links_quick_links():
    with connect() as conn:
        links = conn.get_quick_links()
        db_perms = conn.get_all_perm_types()
        return render_template("links/quick.liquid", links=links, db_perms=db_perms)

@app.post('/links/quick_links/new/')
def post_links_quick_links_new():
    req = request.json
    with connect() as conn:
        res, err = conn.create_quick_link(
            req['link_text'],
            req['link_target'],
            req['perm_seq'],
            session['user_seq']
        )
        if res:
            return "", 200
        return str(err), 400