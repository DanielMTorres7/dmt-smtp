from typing import Optional
import smtplib
import imaplib
import time
from .utils import setup_logger
from .email import Email
from .models import SMTPResponse
import logging

class EmailSender:
    """
    Classe para envio de e-mails utilizando SMTP.\n
    :param url: str - URL do servidor SMTP\n
    :param port: int - Porta do servidor SMTP\n
    :param login: str - E-mail de login\n
    :param password: str - Senha do e-mail\n
    :param logger: logging.Logger - Logger personalizado (default: Console)\n
    :param signature_path: str - Caminho para o arquivo de assinatura (default: None)\n
    Para enviar e-mails, utilize o método `send`.\n
    Após o uso, é recomendado fechar a conexão com o servidor SMTP e IMAP utilizando o método `close_connection`.
    """
    def __init__(self, url: str, port: int, login: str, password: str, logger: logging.Logger = None, signature_path: Optional[str] = None):
        self.logger = setup_logger(logger)
        self.url = url
        self.port = int(port)
        self.login = login
        self.password = password
        self.signature_path = signature_path
        self.server: smtplib.SMTP | smtplib.SMTP_SSL = self._connect_smtp()
        self.imap : imaplib.IMAP4_SSL = self._connect_imap()
        self.logger.info(f"Usando o email: {self.login}")
        

    def _connect_imap(self):
        """
        Conecta ao servidor IMAP para salvar os e-mails enviados.
        """
        try:
            imap_url = self.url.replace("smtp", "imap")
            imap = imaplib.IMAP4_SSL(imap_url, 993)
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
        """Envia um e-mail.

        Args:
            subject: O assunto do e-mail.
            body: O corpo do e-mail.
            to: O endereço de e-mail do destinatário principal.
            cc: Uma string contendo endereços de e-mail em cópia, separados por vírgula (opcional).
            attachment: O caminho para o arquivo a ser anexado ao e-mail (opcional).

        Returns:
            Um objeto SMTPResponse contendo informações sobre o resultado do envio.  Este objeto possui os seguintes atributos:
                success (bool): True se o e-mail foi enviado com sucesso, False caso contrário.
                subject (str): O assunto do e-mail.
                body (str): O corpo do e-mail.
                to (str): O endereço de e-mail do destinatário principal.
                attachment (str, optional): O caminho para o arquivo anexado, se houver.

        """
        email = Email(self.logger, self.login, subject, body, to_email, cc_emails, file_path, self.signature_path)
        try:
            # Envia o e-mail
            self.logger.info(f"Enviando e-mail \"{subject}\"")
            self.server.sendmail(self.login, email.recipients, email.msg)
            self.logger.info(f"E-mail enviado com sucesso")

            # Salva o e-mail na caixa de saída
            sent_folder = self._find_sent_folder()
            self.logger.info(f"Salvando e-mail em {sent_folder}")        
            self.imap.append(sent_folder, '', imaplib.Time2Internaldate(time.time()), email.msg.encode('utf8'))
            self.logger.info("E-mail salvo com sucesso")
            
            return SMTPResponse(True, email.from_email, email.subject, email.body, email.html_body, email.to_email, email.cc_emails, email.signature_path, email.file_path)
        
        except Exception as e:
            error = f"Erro ao enviar e-mail para {to_email}: {e}"
            self.logger.exception(error)
            return SMTPResponse(False, email.from_email, email.subject, email.body, email.html_body, email.to_email, email.cc_emails, email.signature_path, email.file_path, error, 500)
        
    def _find_sent_folder(self):
        """
        Encontra a pasta de enviados no servidor IMAP.
        """
        # Lista de mapeamentos para provedores de e-mail comuns e suas pastas de enviados
        email_folders = {
            'gmail': '"[Gmail]/Sent Mail"',
            'yahoo': 'Sent',
            'outlook': '"[Outlook]/Sent"',
            'hotmail': '"[Hotmail]/Sent"',
            'aol': 'Sent',
            'icloud': 'Sent Messages'
        }
        status, mailboxes = self.imap.list()
        # Variável para armazenar a pasta de enviados
        sent_folder = None
        # Buscando pela pasta de enviados
        for mailbox in mailboxes:
            mailbox_name = mailbox.decode()
            if 'sent' in mailbox_name.lower():
                for provider, folder in email_folders.items():
                    if provider in mailbox_name.lower():
                        sent_folder = folder
                        break
                if not sent_folder:
                    sent_folder = mailbox_name.split(' "." ')[-1]
                break
        return sent_folder