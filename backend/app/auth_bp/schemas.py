"""Authentication validation schemas using marshmallow."""

from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from ..shared.schemas import CommonFields, validate_email_format


class RegisterSchema(Schema):
    """Schema for user registration"""

    email = CommonFields.email
    password = fields.String(required=True, validate=validate.Length(min=1))
    confirm_password = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(validate=validate.Length(min=1, max=100), allow_none=True)
    hcaptcha_token = fields.String(required=True)

    # Honeypot fields - should be empty
    website = fields.String(missing="", allow_none=True)
    username = fields.String(missing="", allow_none=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Ensure password and confirm_password match"""
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError("Passwords do not match", "confirm_password")


class LoginSchema(Schema):
    """Schema for user login"""

    email = fields.Email(required=True, validate=validate_email_format)
    password = fields.String(required=True, validate=validate.Length(min=1))


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request"""

    email = fields.Email(required=True, validate=validate_email_format)
    hcaptcha_token = fields.String(required=True)


class ResetPasswordSchema(Schema):
    """Schema for password reset"""

    token = fields.String(required=True, validate=validate.Length(min=1))
    new_password = fields.String(required=True, validate=validate.Length(min=1))
    hcaptcha_token = fields.String(required=True)


class UpdatePasswordSchema(Schema):
    """Schema for password update"""

    current_password = fields.String(required=True, validate=validate.Length(min=1))
    new_password = fields.String(required=True, validate=validate.Length(min=1))

    @validates_schema
    def validate_passwords_different(self, data, **kwargs):
        """Ensure new password is different from current password"""
        if data.get("current_password") == data.get("new_password"):
            raise ValidationError(
                "New password must be different from current password"
            )


class GoogleTokenSchema(Schema):
    """Schema for Google OAuth token authentication"""

    token = fields.String(required=True, validate=validate.Length(min=1))


class CreateTokenSchema(Schema):
    """Schema for creating API tokens"""

    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=500), allow_none=True)
    expires_at = fields.DateTime(allow_none=True)


class UpdateTokenSchema(Schema):
    """Schema for updating API tokens"""

    name = fields.String(validate=validate.Length(min=1, max=100), allow_none=True)
    description = fields.String(validate=validate.Length(max=500), allow_none=True)
    expires_at = fields.DateTime(allow_none=True)
    is_active = fields.Boolean(allow_none=True)


class UserResponseSchema(Schema):
    """Schema for user response data"""

    id = CommonFields.id
    email = fields.Email()
    name = fields.String(allow_none=True)
    is_active = fields.Boolean()
    is_admin = fields.Boolean()
    created_at = CommonFields.created_at
    picture = fields.String(allow_none=True)
    active_book_id = fields.Integer(allow_none=True)
    active_book = fields.Dict(allow_none=True)


class TokenResponseSchema(Schema):
    """Schema for token response data"""

    id = CommonFields.id
    name = fields.String()
    description = fields.String(allow_none=True)
    is_active = fields.Boolean()
    created_at = CommonFields.created_at
    last_used_at = fields.DateTime(allow_none=True)


class AuthResponseSchema(Schema):
    """Schema for authentication response"""

    token = fields.String(required=True)
    user = fields.Nested(UserResponseSchema, required=True)


class GoogleAuthUrlSchema(Schema):
    """Schema for Google OAuth URL response"""

    auth_url = fields.String(required=True)
    state = fields.String(required=True)
