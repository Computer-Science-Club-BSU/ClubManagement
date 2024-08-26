from flask import Flask
from flask_liquid import Liquid
import logging
from uuid import uuid4
from os import getcwd
from werkzeug.middleware.proxy_fix import ProxyFix
from conf import LOG_DIR

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



logger = logging.getLogger(__name__)


def configLogging():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    logging.basicConfig(filename=f"{LOG_DIR}gen.log", level=logging.ERROR,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format="[%(asctime)s][%(name)s][%(levelname)s] - %(message)s"
                    )



configLogging()

app = Flask(__name__,
            static_folder="src/interface/static",
            template_folder="src/interface/templates/")
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
app.url_map.strict_slashes = False
if app.debug != True:
    logger.info('Application Started')
# app.secret_key = uuid4().hex
app.secret_key = "secret"

Liquid(app)

import src.routes
if __name__ == "__main__":
    app.run()
