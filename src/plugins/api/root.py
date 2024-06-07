from app import app

is_active = True

@app.route('/api/test')
def get_api_test():
    return "This works!"