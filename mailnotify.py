# -*- coding: UTF-8 -*-
#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr

ISOTIMEFORMAT = '%Y-%m-%d %X'


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.decode('utf-8') if not isinstance(addr, str) else addr))


class MailNotify(object):
    def __init__(self, account, password, from_name):
        self.account = account
        self.password = password
        self.from_name = from_name

    def send_text_by_163mail(self, subject, text, to_list, t_type='plain'):
        # Create an instance with attachment
        msg = MIMEMultipart()

        from_addr = self.account  # Sender
        pwd = self.password  # Password
        to_addr = to_list  # Recipient
        smtp_server = "smtp.163.com"

        # File content
        text_msg = MIMEText(text, t_type, 'utf-8')
        msg.attach(text_msg)

        # Email header content
        msg['Subject'] = subject
        msg['From'] = _format_addr('{} <{}>'.format(self.from_name, from_addr))
        msg['To'] = ";".join(to_list)

        try:
            server = smtplib.SMTP_SSL(smtp_server, 465)
            server.login(from_addr, pwd)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.close()
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    mailto_list = ["mailtest@163.com"]

    ntf = MailNotify("mailrecv@163.com", "psw", "mail-from")
    ntf.send_text_by_163mail("subject", "mail content", mailto_list)