import os
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

from App.database import init_db
from App.config import load_config
from flask_jwt_extended import JWTManager


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin
from App.views.views import views

def add_views(app):
    app.register_blueprint(views, url_prefix='/api')

def setup_jwt(app):
    app.config["JWT_SECRET_KEY"] = "your_secret_key_here"
    jwt = JWTManager(app)
    return jwt

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    setup_admin(app)
    setup_jwt(app)
    return app



