from flask import render_template_string, current_app
from flask_mail import Message
from .extensions import mail


def send_password_reset_email(user, token):
    """Send a password reset email to the user."""
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}?email={user.email}"

    email_template = """
    <p>Dear User,</p>
    <p>You requested a password reset for your Kanakku account. Please click the link below to reset your password:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>This link will expire in 24 hours.</p>
    <p>Thanks,<br>The Kanakku Team</p>
    """

    html_content = render_template_string(email_template, reset_url=reset_url)

    msg = Message(
        subject="Reset Your Kanakku Password",
        recipients=[user.email],
        html=html_content,
    )

    mail.send(msg)

    return True
