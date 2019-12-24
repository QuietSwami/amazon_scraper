#!bin/usr/env python3

# This module has all the email capabilities of the bot.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import os

class EmailServer:

    def __init__(self, host, port, username, password):
        self.s = smtplib.SMTP(host=host, port=port)
        print(self.s.ehlo())
        self.s.starttls()
        self.s.login(username, password)

    def sendMessage(self, message):
        self.s.send_message(message)

    def quit(self):
        self.s.quit()

class Message:

    def __init__(self, path, f, to, subject):
        self.f = f
        self.to = to
        self.subject = subject
        self.template = Template(open(path, 'r').read())

    def createMessage(self, **kwargs):
        print(kwargs)
        msg = MIMEMultipart()
        msg['From'] = self.f
        msg['To'] = self.to
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.template.render(kwargs), 'html'))
        return msg

def sendEmail(emailTemp, receiverEmail, id, link, previousPrice, newPrice, country):
    """Sends a email address when the price drops.
    TODO Change it to take and email address as the receiver

    Arguments:
        emailTemp {string} -- Path to the template

    """
    testEmail = os.environ['EMAIL']
    print(testEmail)
    server = EmailServer('smtp.zoho.eu', 587, testEmail, os.environ['PASSWORD'])
    Subject = "The item with ID {} just dropped its price!!".format(id)
    mess = Message(emailTemp, testEmail, receiverEmail, Subject)\
        .createMessage(id=id, link=link, previousPrice=previousPrice, newPrice=newPrice, country=country)
    server.sendMessage(mess)
    server.quit()

def sendPriceDrop(users, productID):
    pass

def sendDeal():
    pass

if __name__ == "__main__":
    sendEmail("emailTemplate.html", os.environ['EMAIL'], "TEST", "https://www.amazon.co.uk/dp/B07WLT8RLB/", "90", "70", "UK")