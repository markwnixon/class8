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
from CCC_system_setup import websites, passwords, companydata
from CCC_system_setup import usernames as em
from models import People, Orders

def etemplate_truck(type,kind,odat):
    cdata = companydata()
    key = odat.Bid
    jo = odat.Jo
    order = odat.Order
    signature = cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]

    if 'eprof' in type or 'invoice' in type:
        od, bol, con = odat.Order, odat.BOL, odat.Container
        try:
            od, bol, con = od.strip(), bol.strip(), con.strip()
        except:
            print('Some objects are None')
        dblk = odat.Dropblock2.splitlines()
        pdat = People.query.get(key)
        estatus, epod, eaccts = pdat.Email, pdat.Associate1, pdat.Associate2
        estatus, epod, eaccts = estatus.strip(), epod.strip(), eaccts.strip()

    if type == 'eprof1':
        etitle = f'Update on Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nOur trucker is at the delivery site:\n\t\t{dblk[0]}\n\t\t{dblk[1]}\n\t\t{dblk[2]}\nWe will send a POD as soon as one can be obtained.\n\nSincerely,\n\n{signature}'
        aname = 'none'
        emailin1 = estatus
        emailin2 = ''
        emailcc1 = em['info']
        emailcc2 = ''
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'eprof2':
        etitle = f'Update on Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject container has been pulled from the port. Delivery is scheduled for {odat.Date2} to:\n\t\t{dblk[0]}\n\t\t{dblk[1]}\n\t\t{dblk[2]}\nWe will send a POD as soon as delivery is complete.\n\nSincerely,\n\n{signature}'
        aname = odat.Gate
        emailin1 = estatus
        emailin2 = ''
        emailcc1 = em['info']
        emailcc2 = ''
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'eprof3':
        etitle = f'Invoice for Completed Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject order has been completed, and your invoice for services is attached.\n\nWe greatly appreciate your business.\n\nSincerely,\n\n{signature}'
        aname = odat.Invoice
        emailin1 = estatus
        emailin2 = eaccts
        emailcc1 = em['info']
        emailcc2 = em['expo']
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'eprof4':
        etitle = f'Proof for Completed Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject order has been completed, and your proof of delivery is attached.\n\nPlease do not hesitate to respond if you have any quesitons.\n\nSincerely,\n\n{signature}'
        aname = odat.Proof
        emailin1 = estatus
        emailin2 = epod
        emailcc1 = em['info']
        emailcc2 = em['expo']
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'eprof5':
        etitle = f'Invoice & Proof for Completed Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject order has been completed, and your invoice with proof of delivery is attached.\n\nPlease do not hesitate to respond if you have any quesitons.\n\nSincerely,\n\n{signature}'
        aname = f'Package_{odat.Jo}.pdf'
        emailin1 = estatus
        emailin2 = eaccts
        emailcc1 = em['info']
        emailcc2 = em['expo']
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'eprof6':
        etitle = f'Invoice Package for Completed Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject order has been completed, and your invoice package is attached.\n\nPlease do not hesitate to respond if you have any quesitons.\n\nSincerely,\n\n{signature}'
        aname = f'Package_{odat.Jo}.pdf'
        emailin1 = estatus
        emailin2 = eaccts
        emailcc1 = em['info']
        emailcc2 = em['expo']
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif type == 'invoice':
        etitle = f'Invoice for Completed Order: {od} | {bol} | {con}'
        ebody = f'Dear {odat.Shipper},\n\nThe subject order has been completed, and your invoice for services is attached.\n\nWe greatly appreciate your business.\n\nSincerely,\n\n{signature}'
        aname = odat.Invoice
        emailin1 = estatus
        emailin2 = eaccts
        emailcc1 = em['info']
        emailcc2 = em['expo']
        emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, aname]
        return emaildata

    elif kind == 6:
        etitle = cdata[2] + ' Quote: ' + jo
        ebody = 'Dear Customer:\n\nYour quote is attached. Please sign and return at your earliest convenience.\n\nWe look forward to doing business with you.\n\nSincerely,\n\n' + \
                cdata[3] + '\n\n\n' + cdata[4] + '\n' + cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]
    elif kind == 5:
        etitle = cdata[2] + ' Invoice'
        ebody = 'Dear Global:\n\nYour invoice summary is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\n' + \
                cdata[3] + '\n\n\n' + cdata[4] + '\n' + cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]
    elif kind == 4:
        etitle = cdata[2] + ' Invoice: ' + jo + ' for Order: ' + order
        ebody = 'Dear Customer:\n\nYour invoice is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\n' + \
                cdata[3] + '\n\n\n' + cdata[4] + '\n' + cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]
    elif kind == 3:
        etitle = cdata[2] + ' Invoice: ' + jo + ' for Order: ' + order
        ebody = 'Dear Customer:\n\nYour invoice is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\n' + \
                cdata[3] + '\n\n\n' + cdata[4] + '\n' + cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]
    elif kind == 2:
        etitle = cdata[2] + ' Invoice: ' + jo + ' for Order: ' + order
        ebody = 'Dear Customer:\n\nYour invoice package is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\n' + \
                cdata[3] + '\n\n\n' + cdata[4] + '\n' + cdata[2] + '\n' + cdata[5] + '\n' + cdata[6] + '\n' + cdata[7]

    try:
        pdat = People.query.get(key)
        emailin1 = str(pdat.Email)
    except:
        emailin1 = 'Not Found'
    emailin2 = ''
    emailcc1 = em['info']
    emailcc2 = em['serv']
    emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2, '']

    return emaildata





    
def email_app_exporter(pdata):
    

    ourserver = websites['mailserver']
    cdat = companydata()
    
    for pdat in pdata:
        ptype=pdat.Ptype
        if ptype=='exporter':
            emailin=pdat.Email
            print('Eporter email=',emailin)
            exporter=pdat.First+' '+pdat.Middle+' '+pdat.Last
            exporter=exporter.replace('  ',' ')
            idn=pdat.id

    if emailin is None or emailin=='None' or len(emailin)<5 or '@' not in emailin:
        emailin = usernames['expo']
        code='Either no email or a bad email was provided'
        
    #emailto = "export@firsteaglelogistics.com"
    emailfrom = emails['expo']
    emailto = emailin
    #emailcc = "info@firsteaglelogistics.com"
    emailcc1 = emails['info']
    emailcc2 = emails['serv']
    
    
    #fileToSend = absdocref
    username = emails[2]
    password = passwords['expo']

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc1
    msg["Cc"] = emailcc2
    msg["Subject"] = f'{cdat[0]} Application Received'

    body = 'Dear '+exporter+':\n\nThis email confirms receipt of your international shipping application with confirmation code Fapp'+str(idn)
    body = body+', and the following summarizes the information we received from you:\n\n'
    for pdat in pdata:
        ptype=pdat.Ptype
        if ptype=='exporter':

            body = body+'Exporter: '+pdat.First+' '+pdat.Middle+' '+pdat.Last+'\n'
            body = body+'Address:'+pdat.Addr1+' '+pdat.Addr2+' '+pdat.Addr3+'\n'
            body = body+'ID:'+pdat.Idtype+' '+pdat.Idnumber+'\n'
            body = body+'Telephone:'+pdat.Telephone+'\n'
            body = body+'Email: '+pdat.Email+'\n\n'
            
        if ptype=='consignee':
            
            body = body+'Consignee: ' + pdat.First +' '+ pdat.Middle +' '+ pdat.Last +'\n'
            body = body+'Address:'+pdat.Addr1+' '+pdat.Addr2+' '+pdat.Addr3+'\n'
            body = body+'Telephone:'+pdat.Telephone+'\n'
            body = body+'Email: '+pdat.Email+'\n\n'
            
        if ptype=='notify':
            
            body = body+'Notify Party: ' + pdat.First +' '+ pdat.Middle +' '+ pdat.Last +'\n'
            body = body+'Address:'+pdat.Addr1+' '+pdat.Addr2+' '+pdat.Addr3+'\n'
            body = body+'Telephone:'+pdat.Telephone+'\n'
            body = body+'Email: '+pdat.Email+'\n\n'

    body = body+'\n\nSincerely,\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
    msg.attach(MIMEText(body, 'plain'))

    #attachment = open(fileToSend, "rb")
 
    #part = MIMEBase('application', 'octet-stream')
    #part.set_payload((attachment).read())
    #encoders.encode_base64(part)
    #part.add_header('Content-Disposition', "attachment; filename= %s" % fileToSend)
 
    #msg.attach(part)
    
    server = smtplib.SMTP(ourserver)
    #server.starttls()
    server.login(username,password)
    emailto = [emailto, emailcc1, emailcc2]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()
    
    #os.remove(newfile)
    
    
def email_app(pdat):

    emails,passwds,ourserver=emailvals()

    emailin=pdat.Email
    if emailin is None or emailin=='None' or len(emailin)<5 or '@' not in emailin:
        emailin = emails[4]
        code='Either no email or a bad email was provided'
        
    #emailto = "export@firsteaglelogistics.com"
    emailfrom = emails[2]
    emailto = emailin
    #emailcc = "info@firsteaglelogistics.com"
    emailcc1 = emails[0]
    emailcc2 = emails[1]
    
    
    #fileToSend = absdocref
    username = emails[2]
    password = passwds[0]

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc1
    msg["Cc"] = emailcc2
    msg["Subject"] = 'First Eagle Logistics Application Received'

    body = 'Dear '+pdat.Company+':\n\nThis email confirms receipt of your application with confirmation code Fapp'+str(pdat.id)
    body = body+', and the following summarizes the information we received from you:\n\n'
    body = body+'Name: '+pdat.Company+'\n'
    body = body+'Address:'+pdat.Addr1+' '+pdat.Addr2+'\n'
    body = body+'CDL:'+pdat.Idtype+' '+pdat.Idnumber+'\n'
    body = body+'Telephone:'+pdat.Telephone+'\n'
    body = body+'Email: '+pdat.Email+'\n'
    body = body+'TWIC Info: '+pdat.Associate1+'\n'
    body = body+'Medical: '+pdat.Associate2+'\n'
    body = body+'Experience: '+pdat.Temp1+'\n\n'
    body = body+'We will review your information promptly and contact very soon.'
    body = body+'\n\nSincerely,\n\nNorma Ghanem\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
    msg.attach(MIMEText(body, 'plain'))

    #attachment = open(fileToSend, "rb")
 
    #part = MIMEBase('application', 'octet-stream')
    #part.set_payload((attachment).read())
    #encoders.encode_base64(part)
    #part.add_header('Content-Disposition', "attachment; filename= %s" % fileToSend)
 
    #msg.attach(part)
    
    server = smtplib.SMTP(ourserver)
    #server.starttls()
    server.login(username,password)
    emailto = [emailto, emailcc1, emailcc2]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()
    
    #os.remove(newfile)
