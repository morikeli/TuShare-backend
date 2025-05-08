from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pathlib import Path

from ..core.config import Config


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MESSAGE_TEMPLATE_PATH = Path(BASE_DIR, 'templates')


mail_config = ConnectionConfig(
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_FROM_NAME = Config.MAIL_FROM_NAME,
    MAIL_STARTTLS = Config.MAIL_STARTTLS,
    MAIL_SSL_TLS = Config.MAIL_SSL_TLS,
    USE_CREDENTIALS = Config.USE_CREDENTIALS,
    VALIDATE_CERTS = Config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=MESSAGE_TEMPLATE_PATH,
)

mail = FastMail(mail_config)

def create_message(recipients: list[str], subject: str, template_body: dict):
    """
    Creates an email message schema with the specified recipients, subject, and template body.

    Args:
        recipients (list[str]): A list of recipient email addresses.
        subject (str): The subject line of the email.
        template_body (dict): A dictionary containing dynamic values for the email template.

    Returns:
        MessageSchema: An instance of MessageSchema configured with the provided subject, recipients, and template body.
    """

    return MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype=MessageType.html,
    )
