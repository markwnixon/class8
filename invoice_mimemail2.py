def main(invo,order,docref,emailin):
    import smtplib
    import mimetypes
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.message import Message
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    import shutil
    import os
    from CCC_system_setup import addpath, emailvals
    
    emails,passwds,ourserver=emailvals()
    absdocref=addpath(docref)
    letter=invo[1]
    if letter=='O':
        word='Booking'
    else:
        word='Order'

    emailfrom = emails[2]
    emailto = emailin
    #emailto = "export@firsteaglelogistics.com"
    emailcc = emails[0]
    fileToSend = absdocref
    username = emails[2]
    password = passwds[0]

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc
    msg["Subject"] = 'First Eagle Logistics Invoice: '+ invo + ' for '+word+': '+ order

    body = 'Dear Customer:\n\nYour invoice is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS,INC.\n\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
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
    
if __name__ == "__main__":
    main()