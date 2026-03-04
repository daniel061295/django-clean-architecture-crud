"""
Resend Email Service Implementation.

This module provides the Resend-specific implementation of the EmailServiceInterface.
It uses the official `resend` Python SDK to send emails.
"""

import logging
from django.conf import settings
import resend

from identity.domain.interfaces import EmailServiceInterface

logger = logging.getLogger(__name__)


class ResendEmailService(EmailServiceInterface):
    """
    Implementation of EmailServiceInterface using the Resend API.
    """

    def __init__(self) -> None:
        """Initializes the service with the API key from Django settings."""
        self.api_key = getattr(settings, "RESEND_API_KEY", "")
        self.from_email = getattr(settings, "RESEND_DEFAULT_FROM_EMAIL", "onboarding@resend.dev")
        resend.api_key = self.api_key

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """
        Sends a password reset email using Resend.

        Args:
            to_email: The recipient's email address.
            reset_link: The frontend URL with the reset token.
        """
        if not self.api_key:
            logger.warning("RESEND_API_KEY is not configured. Email will not be sent.")
            return

        subject = "Restablece tu contraseña"
        
        # HTML content for the email
        html_content = f"""
        <html>
            <body>
                <h2>Restablecimiento de Contraseña</h2>
                <p>Hola,</p>
                <p>Has solicitado restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva:</p>
                <p>
                    <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px;">
                        Restablecer Contraseña
                    </a>
                </p>
                <p>Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
                <br />
                <p>Gracias,</p>
                <p>El equipo de la plataforma</p>
            </body>
        </html>
        """

        try:
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            logger.info("Sending password reset email via Resend to %s", to_email)
            response = resend.Emails.send(params)
            logger.info("Email sent successfully via Resend. ID: %s", response.get("id"))
        except Exception as e:
            logger.error("Failed to send email via Resend: %s", str(e))
            # Depending on business rules, we might want to suppress the error
            # or raise a Custom Domain Exception here so the view returns a 500.
            # For now, we log the error securely.
