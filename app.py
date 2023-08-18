import os
from flask import Flask
from flask import render_template
from applications import config
from applications.config import LocalDevelopmentConfig
from applications.database import db
from flask_restful import Resource, Api

app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)
    api = Api(app)
    app.app_context().push()

    return app, api

app, api = create_app()

from applications.admin_controllers import *
from applications.customer_controllers import *

from applications.api import UserAPI

api.add_resource(UserAPI, "/api/")

if __name__ == '__main__':
    app.run()