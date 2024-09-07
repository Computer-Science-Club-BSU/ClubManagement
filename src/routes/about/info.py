from app import app
from src.utils.template_utils import render_template

@app.route('/about/system/')
def get_about_system():
    return render_template('about/system_info.liquid')