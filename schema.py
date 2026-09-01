from marshmallow import Schema, fields


class UserSchema(Schema):

    id = fields.Int(dump_only=True)

    username = fields.Str(
        required=True
    )

    password = fields.Str(
        required=True,
        load_only=True
    )


class PlainItemSchema(Schema):

    item_id = fields.Int(
        dump_only=True
    )

    name = fields.Str(
        required=True
    )

    price = fields.Float(
        required=True
    )


class PlainStoreSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    name = fields.Str(
        required=True
    )


class PlainTagSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    name = fields.Str(
        required=True
    )


class ItemUpdateSchema(Schema):

    name = fields.Str()

    price = fields.Float()


class StoreSchema(PlainStoreSchema):

    items = fields.List(
        fields.Nested(
            lambda: PlainItemSchema()
        ),
        dump_only=True
    )

    tags = fields.List(
        fields.Nested(
            lambda: PlainTagSchema()
        ),
        dump_only=True
    )


class ItemSchema(PlainItemSchema):

    store_id = fields.Int(
        required=True,
        load_only=True
    )

    store = fields.Nested(
        lambda: PlainStoreSchema(),
        dump_only=True
    )

    tags = fields.List(
        fields.Nested(
            lambda: PlainTagSchema()
        ),
        dump_only=True
    )


class TagSchema(PlainTagSchema):

    store_id = fields.Int(
        load_only=True
    )

    store = fields.Nested(
        lambda: PlainStoreSchema(),
        dump_only=True
    )

    items = fields.List(
        fields.Nested(
            lambda: PlainItemSchema()
        ),
        dump_only=True
    )


class TagAndItemSchema(Schema):

    message = fields.Str()

    item = fields.Nested(
        ItemSchema
    )

    tag = fields.Nested(
        TagSchema
    )


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)