import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api

from db import db

import models


def create_app(db_url=None):
    app = Flask(__name__)

    load_dotenv()

    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"

    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-secret-key"
    )

    db.init_app(app)

    migrate = Migrate(app, db)

    jwt = JWTManager(app)

    api = Api(app)

    # Import blueprints here according to your existing project files
    from resources.store import blp as StoreBlueprint
    from resources.item import blp as ItemBlueprint
    from resources.user import blp as UserBlueprint

    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(UserBlueprint)

    return app