from app import app


@app.route('/doc/edit/', methods=['GET'])
@app.route('/doc/edit', methods=['GET'])
def get_doc_edit():
    return ""
