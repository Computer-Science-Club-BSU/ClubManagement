from app import app
from flask import request, session
from src.utils.db_utilities import connect
'''src/routes/user/favorites.py
Will host the following routes:
/favorites/add/
POST Request -- JSON Body should contain the URL of the current page
javascript
{
  "url": window.location.pathname
}
**stop talking crazy?**'''


@app.post('/favorites/add/')
def post_add_favorite():
    json = request.json
    user_seq = session['user_seq']
    with connect() as conn:
        res, err = conn.create_user_favorite(user_seq, json)
    if res:
        return "", 200
    return repr(err), 400
    # A function will also need to be created called addFavorite that POSTs to /favorites/add
    # POST...
