from flask import request
from app import app
from conf import LOG_DIR

@app.route('/reload/', methods=['POST'])
def post_reload_webhook():
    print(request.headers)
    with open(LOG_DIR + 'reload', 'w') as f:
        f.write(request.json['ref'].split('/')[-1])
    return "200 OK"


