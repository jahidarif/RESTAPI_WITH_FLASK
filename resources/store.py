from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)

from db import db
from models.store import StoreModel
from schema import StoreSchema


blp = Blueprint(
    "Stores",
    __name__,
    description="Operations on stores"
)


@blp.route("/store")
class StoreList(MethodView):

    @blp.response(
        200,
        StoreSchema(many=True)
    )
    def get(self):

        return StoreModel.query.all()


    @blp.arguments(StoreSchema)
    @blp.response(
        201,
        StoreSchema
    )
    def post(self, store_data):

        existing_store = StoreModel.query.filter_by(
            name=store_data["name"]
        ).first()

        if existing_store:
            abort(
                400,
                message="Store already exists"
            )

        store = StoreModel(
            name=store_data["name"]
        )

        try:
            db.session.add(store)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            abort(
                400,
                message="Store already exists"
            )

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while creating the store."
            )

        return store


@blp.route("/store/<int:store_id>")
class Store(MethodView):

    @blp.response(
        200,
        StoreSchema
    )
    def get(self, store_id):

        store = StoreModel.query.get(
            store_id
        )

        if not store:
            abort(
                404,
                message="Store not found"
            )

        return store


    @blp.arguments(StoreSchema)
    @blp.response(
        200,
        StoreSchema
    )
    def put(self, store_data, store_id):

        store = StoreModel.query.get(
            store_id
        )

        if not store:
            abort(
                404,
                message="Store not found"
            )

        existing_store = StoreModel.query.filter(
            StoreModel.name == store_data["name"],
            StoreModel.id != store_id
        ).first()

        if existing_store:
            abort(
                400,
                message="Store already exists"
            )

        store.name = store_data["name"]

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            abort(
                400,
                message="Store already exists"
            )

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while updating the store."
            )

        return store


    def delete(self, store_id):

        store = StoreModel.query.get(
            store_id
        )

        if not store:
            abort(
                404,
                message="Store not found"
            )

        try:
            db.session.delete(store)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while deleting the store."
            )

        return {
            "message": "Store and associated items and tags deleted successfully"
        }, 200