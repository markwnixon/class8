from flask import render_template, flash, redirect, url_for, session, logging, request
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import ntpath
import shutil
import os
from CCC_system_setup import addpath
from CCC_system_setup import websites, passwords, companydata, scac
from CCC_system_setup import usernames as em

def send_mimemail(emaildata,emailsender):

    ourserver = websites['mailserver']
    #emaildata is packed as emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2]

    emailfrom = em[emailsender]
    username = em[emailsender]
    password = passwords[emailsender]

    etitle = emaildata[0]
    ebody = emaildata[1]
    emailin1 = emaildata[2]
    emailin2 = emaildata[3]
    emailcc1 = emaildata[4]
    emailcc2 = emaildata[5]

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailin1


    emailto=[emailin1]
    if emailin2 is not None:
        msg["CC"] = emailin2
        emailto.append(emailin2)
    if emailcc1 is not None:
        msg["CC"] = emailcc1
        emailto.append(emailcc1)
    if emailcc2 is not None:
        msg["Cc"] = emailcc2
        emailto.append(emailcc2)

    msg["Subject"] = etitle
    msg.attach(MIMEText(ebody, 'html'))

    if 1 == 2:
        attachment = open(newfile, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % newfile)
        msg.attach(part)

    print('username=',username,password)
    server = smtplib.SMTP(ourserver)
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

    return emailin1
