from marshmallow import Schema, fields, validate


class CreateBookSchema(Schema):
    """Schema for creating a new book."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Missing required field: name",
            "invalid": "Book name must be a string",
        },
    )


class UpdateBookSchema(Schema):
    """Schema for updating a book."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Missing required field: name",
            "invalid": "Book name must be a string",
        },
    )
