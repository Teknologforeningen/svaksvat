import smtplib

from email.mime.text import MIMEText

MAIL_CONFIG_SECTION = 'emailaccount'
MAIL_CONFIG_USERNAME = 'username'
MAIL_CONFIG_SMTP_SERVER = 'smtp_server'
MAIL_CONFIG_SMTP_PORT = 'smtp_port'


def try_login(mail_server, username, password):
    try:
        return mail_server.login(username or '', password or '')

    except smtplib.SMTPAuthenticationError:
        return False


def send_mail(password_safe, to_adress, subject, text):
    sender = password_safe.get_config_value(MAIL_CONFIG_SECTION,
                                            MAIL_CONFIG_USERNAME)
    recipient = to_adress
    msg = MIMEText(text)
    msg['From'] = 'infochef@teknolog.fi'
    msg['To'] = recipient
    msg['Subject'] = subject
    smtp_server = password_safe.get_config_value(
        MAIL_CONFIG_SECTION,
        MAIL_CONFIG_SMTP_SERVER)
    smtp_port = password_safe.get_config_value(
        MAIL_CONFIG_SECTION,
        MAIL_CONFIG_SMTP_PORT)

    mail_server = smtplib.SMTP(smtp_server, smtp_port)
    mail_server.ehlo()
    try:
        mail_server.sendmail(sender, recipient, msg.as_string())

    except smtplib.SMTPSenderRefused as e:
        if handle_user_authentication(mail_server, password_safe):
            mail_server.sendmail(sender, recipient, msg.as_string())
            return
        raise e


def handle_user_authentication(mail_server, password_safe):
    mail_server.starttls()
    mail_server.ehlo()
    password_safe.askcredentials(
        lambda username, password: try_login(mail_server, username, password),
        MAIL_CONFIG_SECTION,
        MAIL_CONFIG_USERNAME)
    return True
