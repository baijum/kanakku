"""
Email utility functions for the Kanakku application.
"""

from flask import render_template_string, current_app
from flask_mail import Message
from ..extensions import mail


def send_password_reset_email(user, token):
    """
    Send a password reset email to the user.

    Args:
        user: User model instance
        token: Reset token string

    Returns:
        bool: True if email was sent successfully
    """
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}?email={user.email}"

    # Log the email being sent (without exposing the full token)
    masked_token = token[:5] + "..." if token else "None"
    current_app.logger.info(
        f"Sending password reset email to {user.email} with token starting with {masked_token}"
    )

    email_template = """
    <p>Dear User,</p>
    <p>You requested a password reset for your Kanakku account. Please click the link below to reset your password:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This link will expire in 24 hours.</p>
    <p>Thanks,<br>The Kanakku Team</p>
    """

    html_content = render_template_string(email_template, reset_url=reset_url)

    try:
        msg = Message(
            subject="Reset Your Kanakku Password",
            recipients=[user.email],
            html=html_content,
        )

        mail.send(msg)
        current_app.logger.info(
            f"Password reset email sent successfully to {user.email}"
        )
        return True
    except Exception as e:
        current_app.logger.error(
            f"Failed to send password reset email: {str(e)}", exc_info=True
        )
        raise
