from app import app


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    return f"Error: {error=}", 500