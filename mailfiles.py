from runmain import db
from models import Vehicles, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers
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
import numpy as np
import subprocess
import fnmatch
from collections import Counter
import datetime
from PyPDF2 import PdfFileReader
from CCC_system_setup import addpath, scac


def mail_efile(odat, emailin):

    wk = addpath(f'tmp/{scac}/data/vdockr/')

    booking = odat.Booking
    container = odat.Container
    jo = odat.Jo
    sfile = addpath(f'tmp/{scac}/data/vdockr/'+odat.Dpath)
    tfile = odat.Dpath
    shutil.copy(sfile, tfile)

    frfor = odat.FrFor

    adata = Autos.query.filter(Autos.Jo == jo).all()
    ncars = len(adata)

    #newfile= ntpath.basename(mfile)
    # shutil.copy(mfile,newfile)
    emails, passwds, ourserver = emailvals()

    emailfrom = emails[2]
    emailto = emailin
    emailcc = emails[0]
    fileToSend = tfile
    username = emails[2]
    password = passwds[2]

    adverb = ' are '
    aword = ' vehicles '
    if ncars == 1:
        adverb = ' is '
        aword = ' vehicle '

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc
    msg["Subject"] = 'Please File Dock Receipt for Bk:' + booking + ' with C: '+container

    body = 'Dear ' + frfor + ',\n\nPlease file the attached informational dock receipt for booking: ' + \
        booking + ' and container '+container+'.'
    body = body + ' There'+adverb+str(ncars)+aword+'in this container:\n\n'
    for a in adata:
        body = body + 'The '+a.Year+' '+a.Make+' '+a.Model+' with VIN: '+a.VIN + \
            ' has curb weight '+a.EmpWeight + 'lb. and an estimated value of: $'+a.Value+'\n\n'

    body = body + '\n\nAlso, we would greatly appreciate the Proof Copy to review as soon as it becomes available.\n\n'
    body = body + '\n\nThank You,\n\nFIRST EAGLE LOGISTICS\n\n\n'

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(fileToSend, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % fileToSend)

    msg.attach(part)

    server = smtplib.SMTP(ourserver)
    # server.starttls()
    server.login(username, password)
    emailto = [emailto, emailcc]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

    os.remove(tfile)
