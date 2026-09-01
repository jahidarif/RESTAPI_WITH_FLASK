import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from rq import Queue

from db import db
from redis_conn import get_redis_connection
import models


def create_app(db_url=None):
    load_dotenv()

    app = Flask(__name__)

    # --- Redis / RQ setup ---
    connection = get_redis_connection()
    app.queue = Queue("emails", connection=connection)

    # --- App config ---
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"

    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "change-this-secret-key"
    )

    # --- Extensions ---
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    api = Api(app)

    # --- Blueprints ---
    from resources.store import blp as StoreBlueprint
    from resources.item import blp as ItemBlueprint
    from resources.user import blp as UserBlueprint

    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(UserBlueprint)

    return app