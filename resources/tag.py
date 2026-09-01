from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import (
    TagModel,
    StoreModel,
    ItemModel
)
from schema import (
    TagSchema,
    TagAndItemSchema
)


blp = Blueprint(
    "Tags",
    __name__,
    description="Operations on tags"
)


@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):

    @blp.response(
        200,
        TagSchema(many=True)
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

        return store.tags.all()


    @blp.arguments(TagSchema)
    @blp.response(
        201,
        TagSchema
    )
    def post(self, tag_data, store_id):

        store = StoreModel.query.get(
            store_id
        )

        if not store:
            abort(
                404,
                message="Store not found"
            )

        existing_tag = TagModel.query.filter_by(
            store_id=store_id,
            name=tag_data["name"]
        ).first()

        if existing_tag:
            abort(
                400,
                message="A tag with that name already exists in this store."
            )

        # Remove store_id if Swagger/client sends it
        tag_data.pop(
            "store_id",
            None
        )

        tag = TagModel(
            **tag_data,
            store_id=store_id
        )

        try:
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while creating the tag."
            )

        return tag


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):

    @blp.response(
        201,
        TagSchema
    )
    def post(self, item_id, tag_id):

        item = ItemModel.query.get(
            item_id
        )

        if not item:
            abort(
                404,
                message="Item not found"
            )

        tag = TagModel.query.get(
            tag_id
        )

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        # Item and Tag must belong to the same Store
        if item.store_id != tag.store_id:
            abort(
                400,
                message=(
                    "Item and tag must belong "
                    "to the same store."
                )
            )

        if tag in item.tags:
            abort(
                400,
                message="Tag is already linked to this item."
            )

        item.tags.append(tag)

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while linking the tag to the item."
            )

        return tag


    @blp.response(
        200,
        TagAndItemSchema
    )
    def delete(self, item_id, tag_id):

        item = ItemModel.query.get(
            item_id
        )

        if not item:
            abort(
                404,
                message="Item not found"
            )

        tag = TagModel.query.get(
            tag_id
        )

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        if tag not in item.tags:
            abort(
                400,
                message="This tag is not linked to this item."
            )

        item.tags.remove(tag)

        try:
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while removing the tag from the item."
            )

        return {
            "message": "Tag removed from item.",
            "item": item,
            "tag": tag
        }


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):

    @blp.response(
        200,
        TagSchema
    )
    def get(self, tag_id):

        tag = TagModel.query.get(
            tag_id
        )

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        return tag


    def delete(self, tag_id):

        tag = TagModel.query.get(
            tag_id
        )

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        if tag.items:
            abort(
                400,
                message=(
                    "Could not delete tag. "
                    "Remove all item associations first."
                )
            )

        try:
            db.session.delete(tag)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while deleting the tag."
            )

        return {
            "message": "Tag deleted."
        }, 200