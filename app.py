"""Flask start"""
import logging
from flask import Flask
from lib import utils
from resolvers import webhook_blueprint

# Load Flask
app = Flask(__name__)
utils.configure_logging()
app.register_blueprint(webhook_blueprint)

if __name__ == '__main__':
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8080)
    # app.run()
