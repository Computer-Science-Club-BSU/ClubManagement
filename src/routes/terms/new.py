from flask import session, redirect, request
from app import app
from src.utils.db_utilities import connect

@app.post('/terms/new/')
def post_terms_new():
    with connect() as conn:
        start = request.json['start_date']
        end = request.json['end_date']
        desc = request.json['term_desc']
        res, err = conn.create_term(desc, start, end, session['user_seq'])
    if res:
        return "", 200
    return repr(err), 500
