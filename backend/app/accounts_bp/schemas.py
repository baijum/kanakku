from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class AccountCreateSchema(Schema):
    """Schema for account creation validation."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(missing="", validate=validate.Length(max=500))
    currency = fields.Str(missing="INR", validate=validate.Length(min=3, max=3))
    balance = fields.Float(missing=0.0)

    @validates_schema
    def validate_balance(self, data, **kwargs):
        """Validate that balance is a valid number."""
        balance = data.get("balance", 0.0)
        if balance is not None and not isinstance(balance, (int, float)):
            raise ValidationError("Balance must be a valid number", "balance")


class AccountUpdateSchema(Schema):
    """Schema for account update validation."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=500))
    currency = fields.Str(validate=validate.Length(min=3, max=3))
    balance = fields.Float()

    @validates_schema
    def validate_balance(self, data, **kwargs):
        """Validate that balance is a valid number if provided."""
        balance = data.get("balance")
        if balance is not None and not isinstance(balance, (int, float)):
            raise ValidationError("Balance must be a valid number", "balance")


class AccountQuerySchema(Schema):
    """Schema for account query parameter validation."""

    include_details = fields.Bool(missing=False)


class AutocompleteQuerySchema(Schema):
    """Schema for autocomplete query parameter validation."""

    prefix = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    limit = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
