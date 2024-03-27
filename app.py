"""Flask start"""
from flask import Flask
from resolvers import webhook_blueprint
from lib import logger

logger = logger.configure_logging('APP')

# Load Flask
app = Flask(__name__)
app.register_blueprint(webhook_blueprint)

if __name__ == '__main__':
    logger.info("Flask app started")
    app.run(host="0.0.0.0", port=8080)
    # app.run()
