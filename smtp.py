'''
Created on Apr 30, 2014

@author: TReische
'''

import smtplib
import string
import base64
import sspi
from email.mime.text import MIMEText

# NTLM Guide -- http://curl.haxx.se/rfc/ntlm.html

SMTP_EHLO_OKAY = 250
SMTP_AUTH_CHALLENGE = 334
SMTP_AUTH_OKAY = 235


class smtp():
    def __init__(self, server):
        self._smtp = smtplib.SMTP(server)
        self._connect(self._smtp)

    def send(self, To, From, Subject, Body):
        email = MIMEText(Body)
        email['Subject'] = Subject
        email['From'] = From
        email['To'] = To
        self._smtp.sendmail(From, To, email.as_string())

    def _connect(self, smtpObj):
        """Example:
        >>> import smtplib
        >>> smtp = smtplib.SMTP("my.smtp.server")
        >>> connect_to_exchange_as_current_user(smtp)
        """

        # Send the SMTP EHLO command
        response = smtpObj.ehlo()   # response = (code, response)
        if response[0] != SMTP_EHLO_OKAY:
            raise smtplib.SMTPException("Server did not respond as expected \
            to EHLO command")

        sspiclient = sspi.ClientAuth('NTLM')

        # Generate the NTLM Type 1 message
        sec_buffer = None
        err, sec_buffer = sspiclient.authorize(sec_buffer)
        ntlm_message = self._asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 1 message -- Authentication Request
        code, response = smtpObj.docmd("AUTH", "NTLM " + ntlm_message)

        # Verify the NTLM Type 2 response -- Challenge Message
        if code != SMTP_AUTH_CHALLENGE:
            raise smtplib.SMTPException("Server did not respond as expected \
             to NTLM negotiate message")

        # Generate the NTLM Type 3 message
        err, sec_buffer = sspiclient.authorize(base64.decodestring(response))
        ntlm_message = self._asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 3 message -- Response Message
        code, response = smtpObj.docmd("", ntlm_message)
        if code != SMTP_AUTH_OKAY:
            raise smtplib.SMTPAuthenticationError(code, response)

    def _asbase64(self, msg):
        return string.replace(base64.encodestring(msg), '\n', '')

    def _disconnect(self, smtpObj):
        smtpObj.exi()


mail = smtp("email.wescodist.com")
mail.send("treische@wesco.com", "treische@wesco.com", "Test Subject",
          "Test email :D")
