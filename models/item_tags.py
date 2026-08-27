from db import db


class ItemsTags(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.item_id"),
        nullable=False
    )

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey("tags.id"),
        nullable=False
    )