from flask.views import MethodView
from flask_smorest import Blueprint, abort
import os
import requests
from sqlalchemy import or_

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import UserModel
from resources.schema import UserSchema,UserRegisterSchema


blp = Blueprint(
    "Users",
    __name__,
    description="Operations on users"
)

def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    api_key = os.getenv("MAILGUN_API_KEY")

    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"Jahid Hasan Mahmud <postmaster@{domain}>",
            "to": [to],
            "subject": subject,
            "text": body,
        },
    )
@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):

        if UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        try:
            db.session.add(user)
            db.session.commit()

            send_simple_message(
                to=user.email,
                subject="Successfully signed up",
                body=f"Hi {user.username}! You have successfully signed up to the Stores REST API."
            )

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while creating the user."
            )

        return {
            "message": "User created successfully."
        }, 201

@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):

        user = UserModel.query.filter_by(
            username=user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(
            user_data["password"],
            user.password
        ):

            access_token = create_access_token(
                identity=str(user.id)
            )

            refresh_token = create_refresh_token(
                identity=str(user.id)
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200

        abort(
            401,
            message="Invalid credentials."
        )


@blp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):

        current_user_id = get_jwt_identity()

        new_access_token = create_access_token(
            identity=current_user_id
        )

        return {
            "access_token": new_access_token
        }, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):

        user = UserModel.query.get_or_404(
            user_id
        )

        return user

    def delete(self, user_id):

        user = UserModel.query.get_or_404(
            user_id
        )

        try:
            db.session.delete(user)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while deleting the user."
            )

        return {
            "message": "User deleted."
        }, 200