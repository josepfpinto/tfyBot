"""Flask start"""

import sys
from flask import Flask
from resolvers import webhook_blueprint
from lib import logger
import serverless_wsgi


this_logger = logger.configure_logging("APP")

# Load Flask
app = Flask(__name__)
app.register_blueprint(webhook_blueprint)

if __name__ == "__main__":
    this_logger.info("Flask app started")
    # app.run(host="0.0.0.0", port=8080)
    app.run()


def handler(event, context):
    """Lambda Handler"""
    return serverless_wsgi.handle_request(app, event, context)
