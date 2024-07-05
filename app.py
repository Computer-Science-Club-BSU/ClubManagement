from flask import Flask
from flask_liquid import Liquid
from src.utils.template_utils import render_template
import logging
from uuid import uuid4
import datetime
from src.utils import cfg_utils
from src.utils.send_email import send_email
from src.utils.db_utilities import connect
# @lambda _: _()
# def start_time():
#     # cfg = cfg_utils.get_cfg_params()
#     # # Sun, June 30, 2024 16:22
#     # start_time = datetime.datetime.now().strftime("%a, %B %d, %Y %H:%M:%S")
#     # with connect() as conn:
#     #     emails = conn.get_dev_email_addr()
#     # send_email("Application Started", f"""
#     #            <body>
#     #            <p>Club Management Server has started at {start_time}</p>
#     #            <p>SMTP Settings: {cfg[0]}</p>
#     #            <p>Database Settings: {cfg[1]}</p>
#     #            </body>
#     #            """, "root@example.com", emails, [], [])
#     return start_time
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/cms/gen.log", level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format="[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
                    )
app = Flask(__name__,
            static_folder="src/interface/static",
            template_folder="src/interface/templates/")
app.url_map.strict_slashes = False
if app.debug != True:
    logger.info('Application Started')
app.secret_key = "secret"
logger.debug("Flask App Started")
Liquid(app)
logger.debug("Liquid Registered")

import src.routes
if __name__ == "__main__":
    app.run()
