import uuid

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import items, stores


blp = Blueprint(
    "Items",
    __name__,
    description="Operations on items"
)


@blp.route("/item")
class ItemList(MethodView):

    def get(self):
        return {
            "items": list(items.values())
        }

    def post(self):
        item_data = request.get_json()

        if (
            "name" not in item_data
            or "price" not in item_data
            or "store_id" not in item_data
        ):
            abort(
                400,
                message="Include name, price and store_id in the JSON payload"
            )

        if item_data["store_id"] not in stores:
            abort(
                404,
                message="Store not found"
            )

        for existing_item in items.values():
            if (
                existing_item["name"] == item_data["name"]
                and existing_item["store_id"] == item_data["store_id"]
            ):
                abort(
                    400,
                    message="Item already exists in this store"
                )

        item_id = uuid.uuid4().hex

        item = {
            **item_data,
            "item_id": item_id
        }

        items[item_id] = item

        return item, 201


@blp.route("/item/<string:item_id>")
class Item(MethodView):

    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(
                404,
                message="Item not found"
            )

    def put(self, item_id):
        try:
            item = items[item_id]
        except KeyError:
            abort(
                404,
                message="Item not found"
            )

        item_data = request.get_json()

        if (
            "name" not in item_data
            or "price" not in item_data
            or "store_id" not in item_data
        ):
            abort(
                400,
                message="Include name, price and store_id in the JSON payload"
            )

        if item_data["store_id"] not in stores:
            abort(
                404,
                message="Store not found"
            )

        item["name"] = item_data["name"]
        item["price"] = item_data["price"]
        item["store_id"] = item_data["store_id"]

        return item, 200

    def delete(self, item_id):
        try:
            del items[item_id]

            return {
                "message": "Item deleted successfully"
            }, 200

        except KeyError:
            abort(
                404,
                message="Item not found"
            )