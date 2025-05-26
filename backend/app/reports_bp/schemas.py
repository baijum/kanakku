from marshmallow import Schema, fields, validate


class BalanceReportSchema(Schema):
    """Schema for balance report query parameters."""

    account = fields.Str(
        missing=None, allow_none=True, validate=validate.Length(min=1, max=255)
    )
    depth = fields.Str(
        missing=None, allow_none=True, validate=validate.Regexp(r"^\d+$")
    )
    book_id = fields.Int(missing=None, allow_none=True, validate=validate.Range(min=1))


class RegisterReportSchema(Schema):
    """Schema for register report query parameters."""

    account = fields.Str(
        missing=None, allow_none=True, validate=validate.Length(min=1, max=255)
    )
    limit = fields.Int(
        missing=None, allow_none=True, validate=validate.Range(min=1, max=10000)
    )
