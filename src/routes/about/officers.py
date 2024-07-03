"""Handles requests regarding the About Officers page."""
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect

@app.route('/about/officers/')
def about_officers():
    """Handles requests for the about page. Lists current and former officers
    from the history of the club."""
    with connect() as conn:
        positions = conn.get_about_page_assignments()
        former_positions = conn.get_about_former_officers()
    format_pos = {}
    for pos in positions: # Positions is a list of dict. pylint: disable=not-an-iterable
        p_name = pos['position_name']
        pos_list = format_pos.get(p_name, [])
        pos_list.append((pos['title'],pos['name']))
        format_pos[p_name] = pos_list

    return render_template("about/officers.liquid", positions=format_pos,
                           former_officers=former_positions)
