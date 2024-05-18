from flask import Flask
from flask_liquid import Liquid
from src.utils.template_utils import render_template
import logging
from uuid import uuid4

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format="[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
                    )
app = Flask(__name__,
            static_folder="src/interface/static",
            template_folder="src/interface/templates/")
app.secret_key = uuid4().hex

logger.info("Flask App Started")
Liquid(app)
logger.info("Liquid Registered")

from src.routes import root

if __name__ == "__main__":
    app.run(debug=True)
