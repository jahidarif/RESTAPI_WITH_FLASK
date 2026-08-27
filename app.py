import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db

from resources.user import blp as UserBlueprint
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    # API configuration
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"

    # Swagger UI configuration
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    # Swagger JWT configuration
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "security": [
            {
                "bearerAuth": []
            }
        ],
    }

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        db_url
        or os.getenv("DATABASE_URL", "sqlite:///data.db")
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # JWT configuration
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY",
        "super-secret-development-key"
    )

    # Access token expires after 1 hour
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    # Refresh token expires after 30 days
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Smorest
    api = Api(app)

    # Initialize JWT
    jwt = JWTManager(app)

    # ----------------------------------------
    # JWT ROLE-BASED AUTHORIZATION
    # ----------------------------------------

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if str(identity) == "1":
            return {
                "is_admin": True
            }

        return {
            "is_admin": False
        }

    # ----------------------------------------
    # JWT ERROR HANDLING
    # ----------------------------------------

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message": "The token has expired.",
                "error": "token_expired"
            }),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({
                "message": "Signature verification failed.",
                "error": "invalid_token"
            }),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({
                "description": "Request does not contain an access token.",
                "error": "authorization_required"
            }),
            401,
        )

    # ----------------------------------------
    # CREATE DATABASE TABLES
    # ----------------------------------------

    with app.app_context():
        import models  # noqa: F401

        db.create_all()

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------------------

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)

    return app
