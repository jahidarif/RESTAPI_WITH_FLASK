from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    item_id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Str(required=True)


class StoreSchema(PlainStoreSchema):
    pass