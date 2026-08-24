from flask import Flask, request
from flask_smorest import Api, abort
from db import stores, items
import uuid

app = Flask(__name__)

# Flask-Smorest configuration
app.config["API_TITLE"] = "Store API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"

api = Api(app)


@app.get("/store")
def get_allstore():
    return {"stores": list(stores.values())}


@app.post("/store")
def create_store():
    request_data = request.get_json()

    if "name" not in request_data:
        abort(400, message="Include store name in the JSON payload")

    for store in stores.values():
        if store["name"] == request_data["name"]:
            abort(400, message="Store already exists")

    store_id = uuid.uuid4().hex

    new_store = {
        **request_data,
        "id": store_id
    }

    stores[store_id] = new_store

    return new_store, 201


@app.post("/item")
def create_item():
    item_data = request.get_json()

    # Validate required fields
    if (
        "price" not in item_data
        or "store_id" not in item_data
        or "name" not in item_data
    ):
        abort(
            400,
            message="Include price, store_id and name in the JSON payload"
        )
    if item_data["store_id"] not in stores:
        abort(404, message="Store not found")
    for item in items.values():
        if (
            item["name"] == item_data["name"]
            and item["store_id"] == item_data["store_id"]
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
    print(items)

    return item, 201


@app.get("/item")
def get_allitem():
    return {"items": list(items.values())}


@app.get("/store/<string:store_id>")
def get_store_by_id(store_id):
    try:
        return stores[store_id]
    except KeyError:
        abort(404, message="Store not found")


@app.get("/item/<string:item_id>")
def get_item(item_id):
    try:
        return items[item_id]
    except KeyError:
        abort(404, message="Item not found")
@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message": "Item deleted successfully"}
    except KeyError:
        abort(404, message="Item not found")

@app.put("/item/<string:item_id>")
def update_item(item_id):
    try:
        item = items[item_id]
    except KeyError:
        abort(404, message="Item not found")

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
        abort(404, message="Store not found")

    item["name"] = item_data["name"]
    item["price"] = item_data["price"]
    item["store_id"] = item_data["store_id"]

    return item, 200
@app.put("/store/<string:store_id>")
def update_store(store_id):
    try:
        store = stores[store_id]
    except KeyError:
        abort(404, message="Store not found")

    store_data = request.get_json()

    if "name" not in store_data:
        abort(400, message="Include name in the JSON payload")

    for existing_store in stores.values():
        if (
            existing_store["name"] == store_data["name"]
            and existing_store["id"] != store_id
        ):
            abort(400, message="Store already exists")

    store["name"] = store_data["name"]

    return store, 200
@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        return {"message": "Store deleted successfully"}
    except KeyError:
        abort(404, message="Store not found")