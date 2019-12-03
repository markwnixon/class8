def main(order,docref,emailin,monsel,inco, company):
    import smtplib
    import mimetypes
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.message import Message
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    from CCC_system_setup import addpath

    import ntpath
    import shutil
    import os

    emails,passwds,ourserver=emailvals()
    newfile= ntpath.basename(docref)
    shutil.copy(addpath(docref),newfile)

    emailfrom = emails[2]
    emailto = emailin
    emailcc = emails[0]
    
    fileToSend = newfile
    username = emails[0]
    password = passwds[0]
    monvec=['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month=monvec[monsel]

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc
    if inco==0:
        msg["Subject"] = 'Invoice '+ order + ' for ' + company+ ' (Storage for the Month of ' + month +' 2018)'
        body = 'Dear Customer:\n\nYour invoice for storage services is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS,INC.\n\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
    else:
        msg["Subject"] = 'Payment Received for Invoice '+ order
        body = 'Dear Customer:\n\nYour payment receipt for storage services is attached.  Your payment has been applied for the month of ' + month +' 2018.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS,INC.\n\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'

     
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
    
    os.remove(newfile)
    
if __name__ == "__main__":
    main(order,docref,email,monsel,incoder,docref)