from app import app
from src.utils.template_utils import render_template

@app.route('/finances/', methods=['GET'])
def get_finances():
    records = []
    return render_template('fin/view.liquid',
                           records = records)