"""Flask start"""
import sys
import os
import boto3
from flask import Flask
from resolvers import webhook_blueprint
from lib import logger

logger = logger.configure_logging('APP')

# Load Flask
app = Flask(__name__)
app.register_blueprint(webhook_blueprint)

# dynamodb_client = boto3.client('dynamodb')
# if os.environ.get('IS_OFFLINE'):
#     dynamodb_client = boto3.client(
#         'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
#     )
# USERS_TABLE = os.environ['USERS_TABLE']

if __name__ == '__main__':
    logger.info("Flask app started")
    # app.run(host="0.0.0.0", port=8080)
    app.run()
