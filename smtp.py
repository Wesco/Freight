'''
Created on Apr 30, 2014

@author: TReische
'''

import os
import smtplib
import string
import base64
import sspi
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# NTLM Guide -- http://curl.haxx.se/rfc/ntlm.html

SMTP_EHLO_OKAY = 250
SMTP_AUTH_CHALLENGE = 334
SMTP_AUTH_OKAY = 235


class smtp():
    def __init__(self, server):
        self._smtp = smtplib.SMTP(server)
        self.ehlo_response = ""

    def send(self, To, From, Subject, Body, files):
        _email = MIMEMultipart('mixed')
        _email['Subject'] = Subject
        _email['From'] = From
        _email['To'] = To
        _email.attach(MIMEText(Body))

        if type(files) is list:
            for f in files:
                fp = open(f, 'rb')
                att = MIMEApplication(fp.read())
                fp.close()
                att.add_header('Content-Disposition', 'attachment; filename=%s'
                               % os.path.basename(f))
                _email.attach(att)

        self._smtp.sendmail(From, To, _email.as_string())

    def connect(self):
        """Example:
        >>> import smtplib
        >>> smtp = smtplib.SMTP("my.smtp.server")
        >>> connect_to_exchange_as_current_user(smtp)
        """

        # Send the SMTP EHLO command
        code, response = self._smtp.ehlo()
        self.ehlo_response = response
        if code != SMTP_EHLO_OKAY:
            raise smtplib.SMTPException("Server did not respond as expected \
            to EHLO command")

        sspiclient = sspi.ClientAuth('NTLM')

        # Generate the NTLM Type 1 message
        sec_buffer = None
        code, sec_buffer = sspiclient.authorize(sec_buffer)
        ntlm_message = self._asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 1 message -- Authentication Request
        code, response = self._smtp.docmd("AUTH", "NTLM " + ntlm_message)

        # Verify the NTLM Type 2 response -- Challenge Message
        if code != SMTP_AUTH_CHALLENGE:
            raise smtplib.SMTPException("Server did not respond as expected \
             to NTLM negotiate message")

        # Generate the NTLM Type 3 message
        code, sec_buffer = sspiclient.authorize(base64.decodestring(response))
        ntlm_message = self._asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 3 message -- Response Message
        code, response = self._smtp.docmd(ntlm_message)
        if code != SMTP_AUTH_OKAY:
            raise smtplib.SMTPAuthenticationError(code, response)

    def _asbase64(self, msg):
        return string.replace(base64.encodestring(msg), '\n', '')

    def disconnect(self):
        self._smtp.quit()
