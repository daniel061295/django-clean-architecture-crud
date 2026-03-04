"""
Email Infrastructure Service — Django Implementation.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings

from identity.domain.interfaces import EmailServiceInterface

logger = logging.getLogger(__name__)


class DjangoEmailService(EmailServiceInterface):
    """Django implementation of EmailServiceInterface."""

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """Sends an email containing the password reset link."""
        subject = "Recuperación de Contraseña"
        message = (
            f"Hola,\n\n"
            f"Hemos recibido una solicitud para restablecer tu contraseña.\n"
            f"Por favor, haz clic en el siguiente enlace para continuar:\n\n"
            f"{reset_link}\n\n"
            f"Si no solicitaste este cambio, puedes ignorar este correo.\n"
        )
        
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost")
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            logger.info("Password reset email sent to %s", to_email)
        except Exception as e:
            logger.error("Failed to send password reset email to %s: %s", to_email, str(e))
