from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/about/officers/')
@app.route('/about/officers')
def about_officers():
    with connect() as conn:
        positions = conn.get_about_page_assignments()
    print(positions)
    format_pos = {}
    for pos in positions:
        p_name = pos['position_name']
        pos_list = format_pos.get(p_name, [])
        pos_list.append(pos['name'])
        format_pos[p_name] = pos_list

    print(format_pos)
    return render_template("about/officers.liquid", positions=format_pos)