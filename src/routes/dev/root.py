from app import app
from src.utils.template_utils import render_template

@app.get('/documentation/')
@app.get('/documentation/<path:path>')
def get_documentation(path='root'):
    return render_template(f'dev/docs/{path}.liquid')