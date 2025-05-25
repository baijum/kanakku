"""Shared validation schemas used across different modules"""

from marshmallow import Schema, ValidationError, fields, validate


class PaginationSchema(Schema):
    """Schema for pagination parameters"""

    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))


class DateRangeSchema(Schema):
    """Schema for date range filtering"""

    start_date = fields.DateTime(missing=None, allow_none=True)
    end_date = fields.DateTime(missing=None, allow_none=True)

    def validate_date_range(self, data, **kwargs):
        """Validate that start_date is before end_date"""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date")


class SearchSchema(Schema):
    """Schema for search parameters"""

    q = fields.String(missing="", validate=validate.Length(max=100))
    sort_by = fields.String(missing="created_at")
    sort_order = fields.String(missing="desc", validate=validate.OneOf(["asc", "desc"]))


class BaseResponseSchema(Schema):
    """Base schema for API responses"""

    status = fields.String(required=True)
    message = fields.String(missing=None, allow_none=True)


class ErrorResponseSchema(BaseResponseSchema):
    """Schema for error responses"""

    error = fields.String(required=True)
    details = fields.Dict(missing=None, allow_none=True)


class SuccessResponseSchema(BaseResponseSchema):
    """Schema for success responses"""

    data = fields.Raw(required=True)


class PaginatedResponseSchema(SuccessResponseSchema):
    """Schema for paginated responses"""

    meta = fields.Dict(required=True)


# Common field validators
def validate_currency(value):
    """Validate currency code"""
    valid_currencies = ["INR", "USD", "EUR", "GBP"]  # Add more as needed
    if value not in valid_currencies:
        raise ValidationError(f'Currency must be one of: {", ".join(valid_currencies)}')


def validate_amount(value):
    """Validate monetary amount"""
    if value is None:
        return
    if not isinstance(value, (int, float)):
        raise ValidationError("Amount must be a number")
    if value < 0:
        raise ValidationError("Amount cannot be negative")


def validate_email_format(value):
    """Enhanced email validation"""
    import re

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, value):
        raise ValidationError("Invalid email format")


def validate_password_strength(value):
    """Validate password strength"""
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long")

    import re

    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one digit")


# Common field definitions
class CommonFields:
    """Common field definitions for reuse"""

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    email = fields.Email(required=True, validate=validate_email_format)
    password = fields.String(
        required=True, validate=validate_password_strength, load_only=True
    )

    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=500), allow_none=True)

    amount = fields.Float(required=True, validate=validate_amount)
    currency = fields.String(missing="INR", validate=validate_currency)

    date = fields.Date(required=True)

    user_id = fields.Integer(required=True)
    book_id = fields.Integer(required=True)
