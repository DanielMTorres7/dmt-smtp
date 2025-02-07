from typing import Optional
from .model_error import ModelError
from .model_email_attributes import Model_EmailAttributes

class SMTPResponse:
    """
    Classe para armazenar a resposta do envio de e-mails.
    """
    def __init__(self, success: bool, from_email: str, subject: str, body: str, html_body: str, to_email: str, cc_emails: Optional[str] = None, signature_path: Optional[str] = None, file_path: Optional[str] = None, error_message: Optional[str] = None, error_code: Optional[int] = None):
        self.success = success
        self.error = ModelError(error_message, error_code) if not success else None
        self.email_attributes = Model_EmailAttributes(from_email, subject, body, html_body, to_email, cc_emails, signature_path, file_path)