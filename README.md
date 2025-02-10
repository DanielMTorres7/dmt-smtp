# DMT SMTP

This Python library provides a class, `EmailSender`, for sending emails using SMTP and saving sent emails via IMAP. It also includes utility classes and functions for email creation (`Email`), custom MIME part handling (`CustomMIMEMultipart`), and logging (`MyLogger`, `setup_logger`).

## Features

* **SMTP Connection:** Establishes secure connections to SMTP servers using TLS (both explicit and implicit).
* **IMAP Integration:** Saves sent emails to the "Sent" folder via IMAP.  Automatically attempts to locate the correct sent folder.
* **Email Creation:**  The `Email` class simplifies email construction, including handling recipients (To and CC), attachments, and HTML email bodies with signatures.
* **Customizable MIME:** The `CustomMIMEMultipart` class allows for customized MIME parts, including attachments and HTML body with inline images for signatures.
* **Logging:** Integrated logging with customizable format and level.
* **Error Handling:**  Provides `SMTPResponse` objects for tracking success/failure of email sending.

## Class Structure

* **`EmailSender`:** Main class for sending emails. Manages SMTP and IMAP connections.
* **`Email`:** Represents an email message, including headers, body, attachments, and signature.
* **`CustomMIMEMultipart`:** Custom MIME part handling for attachments and HTML body.
* **`SMTPResponse`:** Data model for the result of an email sending operation.
* **`MyLogger`:** Wrapper around the standard logger to customize format temporarily.

## Logging

The library uses Python's built-in `logging` module. You can provide your own logger or use the included `setup_logger` function.

## Error Handling

The `EmailSender.send()` method returns an `SMTPResponse` object, which contains a `success` flag and an `error` message if the email sending failed. This facilitates robust error handling.

## Email Formatting

The `CustomMIMEMultipart` and `Email` classes handle the formatting of the email, including attachments, HTML bodies, and signatures. The HTML body is generated from a template and uses a `<pre>` tag to preserve the original layout and tabs in the email body.

## IMAP Sent Folder

The library attempts to automatically find the "Sent" folder on the IMAP server by checking common folder names.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.