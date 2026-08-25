import uuid

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import items, stores
from resources.schema import ItemSchema


blp = Blueprint(
    "Items",
    __name__,
    description="Operations on items"
)


@blp.route("/item")
class ItemList(MethodView):

    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return list(items.values())

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
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

    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(
                404,
                message="Item not found"
            )

    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        try:
            item = items[item_id]
        except KeyError:
            abort(
                404,
                message="Item not found"
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
                and existing_item["item_id"] != item_id
            ):
                abort(
                    400,
                    message="Item already exists in this store"
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