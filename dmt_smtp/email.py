from typing import List, Optional
import logging
from .utils import CustomMIMEMultipart

class Email:
    """
    Classe de um e-mail a ser enviado.
    args:
        logger: logging.Logger - Objeto de logger
        from_email: str - E-mail do remetente
        subject: str - Assunto do e-mail
        body: str - Corpo do e-mail
        to_email: str - E-mail do destinatário
        cc_emails: str - E-mails de cópia separados por vírgula ou ponto e vírgula
        file_path: str - Caminho para o arquivo a ser anexado
        signature_path: str - Caminho para a assinatura digital
    """
    def __init__(self, logger: logging.Logger, from_email: str, subject: str, body: str, to_email: str, cc_emails: Optional[str] = None, file_path: Optional[str] = None, signature_path: Optional[str] = None):
        self._logger : logging.Logger = logger
        self.from_email = from_email
        self.subject = subject
        self.body = body
        self.html_body = body
        self.to_email = to_email
        self.cc_emails = cc_emails
        self.file_path = file_path
        self.signature_path = signature_path

        self.recipients = self._configure_recipients()
        self.MIME = self._configure_MIME()
        self.msg = self.MIME.as_string()

    def _configure_MIME(self) -> CustomMIMEMultipart:
        """
        Configura o MIME para o envio do e-mail.
        """
        self._logger.info(f"Preparando e-mail para: {self.recipients} com anexo: {self.file_path}")

        mime = CustomMIMEMultipart()
        mime['To'] = self.recipients[0]
        self.to_email = mime['To']

        mime['From'] = self.from_email

        mime['Cc'] = ", ".join(self.recipients[1:])
        self.cc_emails = mime['Cc']

        mime['Subject'] = self.subject.strip()
        self.subject = mime['Subject']


        # Adiciona corpo do e-mail
        mime.attach_html_body(self.body, self.signature_path, self.file_path)

        self.html_body = mime.body_html

        self._logger.info("E-mail preparado com sucesso.")
        return mime

    def _emails_to_list(self, emails: str):
        """
        Configura os e-mails de cópia para o envio.
        args:
            emails: str - E-mails separados por vírgula ou ponto e vírgula
        """
        return [email.strip() for email in emails.replace(";", ",").split(",") if email.strip()]

    def _configure_recipients(self) -> List[str]:
        """
        Configura os destinatários e inclui e-mails de cópia (CC).
        args:
            recipients: str - E-mails dos destinatários separados por vírgula ou ponto e vírgula
            cc_emails: str - E-mails de cópia separados por vírgula ou ponto e vírgula
        """
        recipients_list = self._emails_to_list(self.to_email)
        if self.cc_emails:
            recipients_list.extend(self._emails_to_list(self.cc_emails))

        return recipients_list
    
