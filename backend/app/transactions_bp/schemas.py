from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class PostingSchema(Schema):
    """Schema for transaction posting validation."""

    account = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    amount = fields.Str(required=True)  # Keep as string to match API contract
    currency = fields.Str(missing="INR", validate=validate.Length(min=3, max=3))

    @validates_schema
    def validate_amount(self, data, **kwargs):
        """Validate that amount is a valid number."""
        try:
            float(data.get("amount", ""))
        except (ValueError, TypeError):
            raise ValidationError("Amount must be a valid number", "amount")


class TransactionCreateSchema(Schema):
    """Schema for transaction creation validation."""

    date = fields.Date(required=True, format="%Y-%m-%d")
    payee = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    status = fields.Str(missing="", validate=validate.Length(max=50))
    postings = fields.List(
        fields.Nested(PostingSchema), required=True, validate=validate.Length(min=1)
    )

    @validates_schema
    def validate_postings(self, data, **kwargs):
        """Validate posting-specific business rules."""
        postings = data.get("postings", [])

        if not postings:
            raise ValidationError("At least one posting is required", "postings")

        # Validate that a single transaction doesn't debit and credit the same account
        account_directions = {}
        for posting in postings:
            account_name = posting.get("account")
            amount_str = posting.get("amount")

            if not account_name or amount_str is None:
                continue

            try:
                amount_float = float(amount_str)
                if amount_float == 0:
                    continue

                direction = "debit" if amount_float > 0 else "credit"

                if account_name not in account_directions:
                    account_directions[account_name] = direction
                elif account_directions[account_name] != direction:
                    raise ValidationError(
                        f"Cannot debit and credit the same account '{account_name}' in a single transaction.",
                        "postings",
                    )
            except ValueError:
                continue


class TransactionUpdateSchema(Schema):
    """Schema for transaction update validation."""

    date = fields.Date(format="%Y-%m-%d")
    description = fields.Str(validate=validate.Length(max=255))
    payee = fields.Str(validate=validate.Length(min=1, max=255))
    amount = fields.Str()  # Keep as string to match API contract
    currency = fields.Str(validate=validate.Length(min=3, max=3))
    status = fields.Str(validate=validate.Length(max=50))

    @validates_schema
    def validate_amount(self, data, **kwargs):
        """Validate that amount is a valid number if provided."""
        amount = data.get("amount")
        if amount is not None:
            try:
                float(amount)
            except (ValueError, TypeError):
                raise ValidationError("Amount must be a valid number", "amount")


class TransactionQuerySchema(Schema):
    """Schema for transaction query parameter validation."""

    limit = fields.Int(validate=validate.Range(min=1, max=1000))
    offset = fields.Int(validate=validate.Range(min=0))
    start_date = fields.Date(format="%Y-%m-%d")
    end_date = fields.Date(format="%Y-%m-%d")
    search = fields.Str(validate=validate.Length(max=255))
    book_id = fields.Int(validate=validate.Range(min=1))

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        """Validate that start date is before end date."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be before end date", "start_date")


class RecentTransactionsQuerySchema(Schema):
    """Schema for recent transactions query parameter validation."""

    limit = fields.Int(missing=7, validate=validate.Range(min=1, max=100))
    book_id = fields.Int(validate=validate.Range(min=1))
