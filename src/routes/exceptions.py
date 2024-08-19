from app import app


# @app.errorhandler(Exception)
# def handle_423(e):
#     e_code = str(e)[0:3]
#     if e_code.isdigit():
#         return f'<img src=https://http.cat/{e_code}></img>', int(e_code)
#     return f"Error: {str(e)}", 400