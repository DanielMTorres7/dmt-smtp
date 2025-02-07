from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

template = """
<html>
    <body>
        <pre style="{font_family} {font_size} white-space: pre-wrap;">
{body}
        </pre>
        _signature_
    </body>
</html>
"""

class CustomMIMEMultipart(MIMEMultipart):
    def __init__(self):
        super().__init__()
        self.font_family = "Calibri, sans-serif"
        self.font_size = 14
        self.signature_style = "height:200px;"
        self.body_html = "\n".join(template.strip().splitlines())
    def attach_file(self, file_path:str):
        """
        Anexa um arquivo ao e-mail a partir do caminho fornecido.
        """
        if file_path:
            # Anexar arquivo ao e-mail
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {basename(file_path)}'
                )
                self.attach(part)
    
    def add_signature(self, signature_path):
        """
        Adiciona a assinatura digital ao e-mail.
        """
        if signature_path:
            self.body_html = self.body_html.replace("_signature_", '<img src="cid:signature_image" style="{}">'.format(self.signature_style))
            with open(signature_path, "rb") as image_file:
                image = MIMEImage(image_file.read())
                image.add_header('Content-ID', '<signature_image>')
                self.attach(image)
        else:
            # remove a linha da assinatura do e-mail
            self.body_html = "\n".join(line for line in self.body_html.splitlines() if "_signature_" not in line)

    def attach_html_body(self, body: str, signature_path: str = None, file_path: str = None):
        """
        Converte o corpo do e-mail para HTML e anexa,
        preservando tabulações e formatando com `<pre>` para manter o layout original.
        """
        # Usar <pre> para preservar tabulação e formatação original
        self.body_html = self.body_html.format(body=body, font_family=f"font-family: {self.font_family};", font_size=f"font-size: {self.font_size}px;")
        # Adicionar assinatura ao e-mail
        self.add_signature(signature_path)
        # Anexar arquivo ao e-mail
        self.attach_file(file_path)
        # Anexar ao e-mail
        self.attach(MIMEText(self.body_html, 'html'))

        return self.body_html