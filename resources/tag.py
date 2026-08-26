from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.item import ItemModel
from models.store import StoreModel
from models.tag import TagModel
from resources.schema import TagSchema, TagAndItemSchema


blp = Blueprint(
    "Tags",
    __name__,
    description="Operations on tags"
)


@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):

    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):

        store = StoreModel.query.get(store_id)

        if not store:
            abort(
                404,
                message="Store not found"
            )

        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):

        store = StoreModel.query.get(store_id)

        if not store:
            abort(
                404,
                message="Store not found"
            )

        if TagModel.query.filter(
            TagModel.store_id == store_id,
            TagModel.name == tag_data["name"]
        ).first():
            abort(
                400,
                message="A tag with that name already exists in that store."
            )

        tag = TagModel(
            **tag_data,
            store_id=store_id
        )

        try:
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()

            abort(
                500,
                message=str(e)
            )

        return tag


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):

    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):

        item = ItemModel.query.get(item_id)

        if not item:
            abort(
                404,
                message="Item not found"
            )

        tag = TagModel.query.get(tag_id)

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        if item.store_id != tag.store_id:
            abort(
                400,
                message="Make sure item and tag belong to the same store before linking."
            )

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while linking the tag."
            )

        return tag


    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):

        item = ItemModel.query.get(item_id)

        if not item:
            abort(
                404,
                message="Item not found"
            )

        tag = TagModel.query.get(tag_id)

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            abort(
                500,
                message="An error occurred while unlinking the tag."
            )

        return {
            "message": "Item removed from tag",
            "item": item,
            "tag": tag
        }


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):

        tag = TagModel.query.get(tag_id)

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        return tag


    def delete(self, tag_id):

        tag = TagModel.query.get(tag_id)

        if not tag:
            abort(
                404,
                message="Tag not found"
            )

        if tag.items:

            abort(
                400,
                message="Could not delete tag. Make sure tag is not associated with any items, then try again."
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
        }, 202