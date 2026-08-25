import uuid

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import stores
from resources.schema import StoreSchema


blp = Blueprint(
    "Stores",
    __name__,
    description="Operations on stores"
)


@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return list(stores.values())

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        for existing_store in stores.values():
            if existing_store["name"] == store_data["name"]:
                abort(
                    400,
                    message="Store already exists"
                )

        store_id = uuid.uuid4().hex

        new_store = {
            "id": store_id,
            "name": store_data["name"]
        }

        stores[store_id] = new_store

        return new_store, 201


@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(
                404,
                message="Store not found"
            )

    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def put(self, store_data, store_id):
        try:
            store = stores[store_id]
        except KeyError:
            abort(
                404,
                message="Store not found"
            )

        for existing_store in stores.values():
            if (
                existing_store["name"] == store_data["name"]
                and existing_store["id"] != store_id
            ):
                abort(
                    400,
                    message="Store already exists"
                )

        store["name"] = store_data["name"]

        return store, 200

    def delete(self, store_id):
        try:
            del stores[store_id]

            return {
                "message": "Store deleted successfully"
            }, 200

        except KeyError:
            abort(
                404,
                message="Store not found"
            )