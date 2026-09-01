from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    jwt_required,
    get_jwt
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)

from db import db
from models.item import ItemModel
from models.store import StoreModel
from schema import (
    ItemSchema,
    ItemUpdateSchema,
    PlainItemSchema
)


blp = Blueprint(
    "Items",
    __name__,
    description="Operations on items"
)


@blp.route("/item")
class ItemList(MethodView):

    @jwt_required()
    @blp.response(
        200,
        PlainItemSchema(many=True)
    )
    def get(self):

        return ItemModel.query.all()


    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(
        201,
        ItemSchema
    )
    def post(self, item_data):

        store = StoreModel.query.get(
            item_data["store_id"]
        )

        if not store:
            abort(
                404,
                message="Store not found"
            )

        existing_item = ItemModel.query.filter_by(
            name=item_data["name"],
            store_id=item_data["store_id"]
        ).first()

        if existing_item:
            abort(
                400,
                message="Item already exists in this store"
            )

        item = ItemModel(
            name=item_data["name"],
            price=item_data["price"],
            store_id=item_data["store_id"]
        )

        try:
            db.session.add(item)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            abort(
                400,
                message="Unable to create item due to database constraints."
            )

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while creating the item."
            )

        return item


@blp.route("/item/<int:item_id>")
class Item(MethodView):

    @jwt_required()
    @blp.response(
        200,
        ItemSchema
    )
    def get(self, item_id):

        item = ItemModel.query.get(
            item_id
        )

        if not item:
            abort(
                404,
                message="Item not found"
            )

        return item


    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(
        200,
        ItemSchema
    )
    def put(self, item_data, item_id):

        item = ItemModel.query.get(
            item_id
        )

        if not item:
            abort(
                404,
                message="Item not found"
            )

        if "name" in item_data:
            item.name = item_data["name"]

        if "price" in item_data:
            item.price = item_data["price"]

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            abort(
                400,
                message="Unable to update item due to database constraints."
            )

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while updating the item."
            )

        return item


    @jwt_required()
    def delete(self, item_id):

        jwt_data = get_jwt()

        if not jwt_data.get("is_admin"):
            abort(
                403,
                message="Admin privilege required."
            )

        item = ItemModel.query.get(
            item_id
        )

        if not item:
            abort(
                404,
                message="Item not found"
            )

        try:
            db.session.delete(item)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while deleting the item."
            )

        return {
            "message": "Item deleted successfully"
        }, 200