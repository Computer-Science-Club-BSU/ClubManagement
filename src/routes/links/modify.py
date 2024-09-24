from flask import session, request
from app import app
from src.utils.db_utilities import connect


@app.post('/links/quick_links/edit/')
def post_links_quick_links_edit():
    req = request.json
    seq = req['seq']
    target = req['link_target']
    text = req['link_text']
    perm = req['perm_seq']
    rank = req['ranking']
    with connect() as conn:
        res, err = conn.update_quick_link(seq, target, text, perm, rank, session['user_seq'])
    if res:
        return "", 200
    return str(err), 400

@app.post('/links/quick_links/delete/')
def post_links_quick_links_delete():
    req = request.json
    seq = req['seq']
    password = req['password']
    username = req['username']
    with connect() as conn:
        res, err = conn.delete_quick_link(seq, username, password)
    if res:
        return "", 200
    return str(err), 400


@app.post('/links/quick_links/move')
def post_links_quick_links_move():
    req = request.json
    seq = req['seq']
    step = req['step']
    with connect() as conn:
        if step == 1:
            res, err = conn.move_quick_link_up(seq, session['user_seq'])
        elif step == -1:
            res, err = conn.move_quick_link_down(seq, session['user_seq'])
        else:
            raise Exception('Invalid step')
    if res:
        return "", 200
    return str(err), 400

