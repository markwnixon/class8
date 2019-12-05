def main(odata, cdata1, cdata2, tdata):
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
    from CCC_system_setup import addpath, emailvals, scac

    prefix='processing/to_email/'
    done='originals_processed/emailed/'
    wk=f'tmp/{scac}/data/vmanifest/'

    jo=str(odata.Jo)
    order=str(odata.Order)
    driver=str(odata.Driver)
    drv_email=str(tdata.Email)
    mfile=wk+'Manifest'+jo+'.pdf'
    mfile=addpath(mfile)
    
    emails,passwds,ourserver=emailvals()

    #newfile= ntpath.basename(mfile)
    #shutil.copy(mfile,newfile)

    emailfrom = emails[2]
    emailto = drv_email
    emailcc = emails[0]
    fileToSend = mfile
    username = emails[2]
    password = passwds[0]

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc
    msg["Subject"] = 'Manifest for Order '+ order

    body = 'Hello ' + driver + ',\n\nThe attached file is a manifest for a load to which you are the primary driver.\n\nPlease review and let us know if any corrections are required.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS DISPATCH\n\n\n'

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(fileToSend, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % fileToSend)

    msg.attach(part)

    server = smtplib.SMTP(ourserver)
    #server.starttls()
    server.login(username,password)
    emailto = [emailto, emailcc]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

    #os.remove(newfile)

if __name__ == "__main__":
    main()
