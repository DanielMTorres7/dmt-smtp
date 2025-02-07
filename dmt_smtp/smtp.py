from typing import Optional
import smtplib
import imaplib
import time
from .utils import setup_logger
from .email import Email
from .models import SMTPResponse

class EmailSender:
    """
    Classe para envio de e-mails utilizando SMTP.
    args:
        url: str - URL do servidor SMTP
        port: int - Porta do servidor SMTP
        login: str - E-mail de login
        password: str - Senha de login
        log_path: str - Caminho para o arquivo de log
    Para enviar e-mails, utilize o método `send`.
    Após o uso, é recomendado fechar a conexão com o servidor SMTP e IMAP utilizando o método `close_connection`.
    """
    def __init__(self, url: str, port: int, login: str, password: str, log_path: str = ""):
        self.logger = setup_logger(log_path)
        self.url = url
        self.port = port
        self.login = login
        self.password = password
        self.server: smtplib.SMTP | smtplib.SMTP_SSL = self._connect_smtp()
        self.imap : imaplib.IMAP4_SSL = self._connect_imap()
        

    def _connect_imap(self):
        """
        Conecta ao servidor IMAP para salvar os e-mails enviados.
        """
        try:
            imap = imaplib.IMAP4_SSL(self.url, 993)
            imap.login(self.login, self.password)
            self.logger.info("Conectado ao servidor IMAP com sucesso.")
            return imap
        except Exception as e:
            raise ConnectionError(f"Falha ao conectar ao servidor IMAP: {e}") from e

    def _connect_smtp(self):
        """
        Conecta ao servidor SMTP usando TLS explícito (porta 587) 
        ou TLS implícito (porta 465), dependendo da porta configurada.
        """
        try:
            if self.port == 587:
                server = smtplib.SMTP(self.url, self.port)
                server.starttls()  # Inicia TLS explicitamente
            elif self.port == 465:
                server = smtplib.SMTP_SSL(self.url, self.port)  # TLS implícito
            else:
                raise ValueError("Porta SMTP inválida. Use 587 ou 465.")

            server.login(self.login, self.password)
            self.logger.info("Conectado ao servidor SMTP com sucesso.")
            self.logger.info(f"Usando o email: {self.login}")
            return server

        except (smtplib.SMTPException, ValueError) as e:
            raise ConnectionError(f"Falha ao conectar ao servidor SMTP: {e}") from e
        except Exception as e:
            raise ConnectionError(f"Erro inesperado ao conectar ao servidor SMTP: {e}") from e
    
    def close_connection(self):
        """
        Fecha a conexão com os servidores SMTP e IMAP.
        """
        if self.server is not None:
            try:
                if self.server.sock:
                    self.server.quit()
                    self.logger.info("Conexão SMTP encerrada.")
                else:
                    self.logger.warning("Tentativa de fechar conexão SMTP já desconectada.")
            except Exception as e:
                self.logger.exception(f"Erro ao encerrar conexão SMTP: {e}")
            finally:
                self.server = None

        if self.imap is not None:
            try:
                self.imap.logout()
                self.logger.info("Conexão IMAP encerrada.")
            except Exception as e:
                self.logger.exception(f"Erro ao encerrar conexão IMAP: {e}")
            finally:
                self.imap = None

    

    def send(self, subject: str, body: str, to_email: str, cc_emails: Optional[str] = None, file_path: Optional[str] = None) -> SMTPResponse:
        """
        Envia o e-mail para os destinatários especificados.
        args:
            subject: str - Assunto do e-mail
            body: str - Corpo do e-mail
            to_email: str - E-mail do destinatário
            cc_emails: str - E-mails de cópia separados por vírgula ou ponto e vírgula
            file_path: str - Caminho para o arquivo a ser anexado
        return:
            SMTPResponse - Objeto com informações sobre o envio do e-mail
            success: bool - Indica se o e-mail foi enviado com sucesso
            subject: str - Assunto do e-mail
            body: str - Corpo do e-mail
            to_email: str - E-mail do destinatário
            file_path: str - Caminho do arquivo anexado
        """
        email = Email(self.logger, self.login, subject, body, to_email, cc_emails, file_path)
        try:
            # Envia o e-mail
            self.logger.info(f"Enviando e-mail \"{subject}\" para: {email.recipients}")
            self.server.sendmail(self.login, email.recipients, email.msg)
            self.logger.info(f"E-mail enviado com sucesso para {email.recipients}")

            # Salva o e-mail na caixa de saída
            self.logger.info("Salvando e-mail na caixa de saída.")
            self.imap.append('INBOX.Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), email.msg.encode('utf8'))
            self.logger.info("E-mail salvo na caixa de saída.")
            
            return SMTPResponse(True, email.from_email, email.subject, email.body, email.html_body, email.to_email, email.cc_emails, email.signature_path, email.file_path)
        
        except Exception as e:
            error = f"Erro ao enviar e-mail para {to_email}: {e}"
            self.logger.exception(error)
            return SMTPResponse(False, email.from_email, email.subject, email.body, email.html_body, email.to_email, email.cc_emails, email.signature_path, email.file_path, error, 500)
        
