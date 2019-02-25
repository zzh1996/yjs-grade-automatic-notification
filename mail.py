import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from config import *


def send_email(subject, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    sender = Header('成绩', 'utf-8')
    sender.append('<%s>' % smtp_username, 'ascii')
    msg['From'] = sender
    msg['To'] = smtp_to
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    if smtp_ssl:
        s = smtplib.SMTP_SSL(smtp_server)
    else:
        s = smtplib.SMTP(smtp_server)
    s.login(smtp_username, smtp_password)
    s.sendmail(smtp_username, smtp_to, msg.as_string())
    s.quit()
