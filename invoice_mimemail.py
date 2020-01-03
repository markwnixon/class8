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
import datetime
today = datetime.datetime.today()
#today = today.date()

def invoice_mimemail(order,docref,eprof):

    ourserver = websites['mailserver']

    emailin1=request.values.get('edat2')
    emailin2=request.values.get('edat3')
    emailcc1=request.values.get('edat4')
    emailcc2=request.values.get('edat5')
    etitle=request.values.get('edat0')
    ebody=request.values.get('edat1')
    newfile = request.values.get('edat6')
    order=order.strip()
    try:
        iprof = int(eprof)
    except:
        iprof = 0

    if newfile != 'none':
        if iprof > 0:
            cfrom = addpath(f'tmp/{scac}/data/vpackages/{docref}')
        else:
            cfrom = addpath(f'tmp/{scac}/data/vinvoice/{docref}')
        print(cfrom,newfile)
        shutil.copy(cfrom,newfile)

    #emailto = "export@firsteaglelogistics.com"
    emailfrom = em['invo']
    username = em['invo']
    password = passwords['invo']

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailin1
    emailto=[emailin1]
    if emailin2 is not None:
        msg["To"] = emailin2
        emailto.append(emailin2)
    if emailcc1 is not None:
        msg["CC"] = emailcc1
        emailto.append(emailcc1)
    if emailcc2 is not None:
        msg["Cc"] = emailcc2
        emailto.append(emailcc2)
    #msg["Subject"] = 'First Eagle Logistics Invoice: '+ invo + ' for Order: '+ order
    msg["Subject"] = etitle

    #body = 'Dear Customer:\n\nYour invoice is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS,INC.\n\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
    msg.attach(MIMEText(ebody, 'plain'))

    if newfile != 'none':
        attachment = open(newfile, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % newfile)
        msg.attach(part)
        attachment.close()
        os.remove(newfile)

    print('username=',username,password)
    server = smtplib.SMTP(ourserver)
    #server.connect(ourserver, 465)
    #server.ehlo()
    server.starttls()

    #server.starttls()
    server.login(username,password)
    #emailto = [emailin1, emailin2, emailcc1, emailcc2]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()



    return emailin1
