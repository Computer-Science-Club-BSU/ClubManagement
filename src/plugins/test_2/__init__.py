import src.plugins.test_2.root
from app import app

@app.route('/test/2')
def test2():
    return "This should work"