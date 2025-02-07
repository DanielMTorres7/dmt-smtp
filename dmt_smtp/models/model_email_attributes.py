from typing import Optional

class Model_EmailAttributes:
    def __init__(self, from_email: str, subject: str, body: str, html_body: str, to_email: str, cc_emails: Optional[str] = None, signature_path: Optional[str] = None, file_path: Optional[str] = None):
        self.from_email = from_email
        self.subject = subject
        self.body = body
        self.html_body = html_body
        self.to_email = to_email
        self.cc_emails = cc_emails
        self.signature_path = signature_path
        self.file_path = file_path