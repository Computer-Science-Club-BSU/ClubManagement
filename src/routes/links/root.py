from app import app
from flask import redirect, abort
from src.utils.db_utilities import connect


@app.get('/l/<link_code>')
def get_l_link(link_code):
    """Handles URL Link Redirections"""
    with connect() as conn:
        _, link = conn.get_redirect_link(link_code)
        if link != None:
            return redirect(link)
        abort(404)