from flask import Flask
from flask_session import Session
from flask_liquid import Liquid
from datetime import timedelta
import uuid
from src.utils.db_utils import connect


app = Flask(__name__, template_folder='src/interface/liquid',
            static_folder='src/interface/static')
liquid = Liquid(app)
app.config.update(SESSION_PERMANENT=False,
                  SESSION_TYPE="filesystem")

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(1)

Session(app)
# Create a new Secret Key any time the code restarts
with connect() as conn:
    app.secret_key = conn.get_secret()
    print(app.secret_key)

# Import the Front-end Routes
import src.routes

if __name__ == "__main__":
    app.run()