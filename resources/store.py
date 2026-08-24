import uuid

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import stores


blp = Blueprint(
    "Stores",
    __name__,
    description="Operations on stores"
)


@blp.route("/store")
class StoreList(MethodView):

    def get(self):
        return {"stores": list(stores.values())}

    def post(self):
        store_data = request.get_json()

        if "name" not in store_data:
            abort(
                400,
                message="Include name in the JSON payload"
            )

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

    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(
                404,
                message="Store not found"
            )

    def put(self, store_id):
        try:
            store = stores[store_id]
        except KeyError:
            abort(
                404,
                message="Store not found"
            )

        store_data = request.get_json()

        if "name" not in store_data:
            abort(
                400,
                message="Include name in the JSON payload"
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