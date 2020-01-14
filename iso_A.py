from runmain import app, db
from models import users, ChalkBoard, Interchange, Orders, General
from models import Services, Drivers, JO, People, OverSeas, Chassis, LastMessage
from models import Autos, Bookings, Vehicles, Invoices, Income, Accounts, Bills, Drops

from flask import render_template, flash, redirect, url_for, session, logging, request
import math
from decimal import Decimal

import datetime
import os
import json


from twilio.twiml.messaging_response import MessagingResponse
from messager import msg_analysis
import requests
import mimetypes
from urllib.parse import urlparse
import img2pdf
from viewfuncs import make_new_order, nonone

today = datetime.datetime.today()
year = str(today.year)
day = str(today.day)
month = str(today.month)

from CCC_system_setup import companydata, statpath, addpath, scac, tpath
cmpdata = companydata()

@app.route('/FileUpload', methods=['GET', 'POST'])
def FileUpload():
    err=[]
    uptype = request.values['uptype']
    print(uptype)
    oder = request.values['oid']
    oder = nonone(oder)
    print(oder)
    user = request.values['user']
    print(user)
    odat = Orders.query.get(oder)
    jo = odat.Jo
    pcache = odat.Pcache
    scache = odat.Scache
    fileob = request.files["file2upload"]
    name, ext = os.path.splitext(fileob.filename)
    if uptype == 'proof':
        filename1 = f'Proof_{jo}_c{str(pcache)}{ext}'
        filename2 = f'Proof_{jo}_c{str(pcache)}.pdf'
        output1 = addpath(tpath('poof', filename1))
        output2 = addpath(tpath('poof', filename2))
        odat.Pcache = pcache + 1
        db.session.commit()
    elif uptype == 'source':
        filename1 = f'Source_{jo}_c{str(scache)}{ext}'
        filename2 = f'Source_{jo}_c{str(scache)}.pdf'
        output1 = addpath(tpath('oder', filename1))
        output2 = addpath(tpath('oder', filename2))
        odat.Scache = scache + 1
        db.session.commit()
    if ext != '.pdf':
        try:
            fileob.save(output1)
            with open(output2, "wb") as f:
                f.write(img2pdf.convert(output1))
            os.remove(output1)
        except:
            filename2 = filename1
    else:
        fileob.save(output2)
    if uptype == 'proof':
        odat.Proof = filename2
    elif uptype == 'source':
        odat.Original = filename2
    db.session.commit()

    print(f'File {fileob.filename} uploaded as {filename2}')

    return "successful_upload"



@app.route('/Barcode', methods=['GET', 'POST'])
def Barcode():
    from vin import getvindata
    if request.method == 'POST':
        gd = request.values.get('txtBarcode')
        ld = len(gd)
        suc = False
        specs = 0

        # ld of length 17 and 18 reserved for automobile barcodes only
        if ld == 18:
            gd = gd[-17:]
            ld = len(gd)
        if ld<17:
            gd = f'VIN too short.  Need 17 char got {ld} in {gd}'
        if ld>17:
            gd = f'VIN too long.  Need 17 char got {ld} in {gd}'

        if len(gd) == 17:
            adat = Autos.query.filter(Autos.VIN == gd).first()
            if adat is not None:
                decodeheader = f'VIN:{gd} already in database'
            else:
                decodeheader = f'Decoded VIN:{gd}'
                suc, specs = getvindata(gd)
        else:
            decodeheader = f'{gd}'
    else:
        decodeheader = 'No Data Yet'
        suc = False
        specs = 0

    return render_template(f'Barcode.html',cmpdata=cmpdata, scac=scac, decodeheader=decodeheader, suc=suc, specs=specs)


@app.route('/')
def index():
    srcpath = statpath('')
    return render_template(f'companysite/{scac}/about.html',srcpath=srcpath, cmpdata=cmpdata, scac=scac)

@app.route('/About')
def About():
    lang = 'English'
    srcpath = statpath('')
    return render_template(f'companysite/{scac}/about.html',srcpath=srcpath,cmpdata=cmpdata, scac=scac, lang=lang)

@app.route('/Whatapp', methods=['GET', 'POST'])
def Whatapp():
    token = os.environ['TWILIO_AUTH_TOKEN']
    print('token=',token)
    msg = request.form.get('Body')
    msg = msg.strip()
    sessionph = request.form.get('From')
    print('sessionph =',sessionph)
    media_files = []
    num_media = int(request.values.get("NumMedia"))
    if num_media > 0:
        for idx in range(num_media):
            media_url = request.values.get(f'MediaUrl{idx}')
            mime_type = request.values.get(f'MediaContentType{idx}')
            req = requests.get(media_url)
            file_extension = mimetypes.guess_extension(mime_type)
            file_extension = file_extension.replace('.jpe', '.jpg')
            file_extension = file_extension.replace('.jpeg', '.jpg')
            media_sid = os.path.basename(urlparse(media_url).path)
            media_files.append(media_sid+file_extension)
            media_path = addpath('tmp/data/processing/whatsapp/')
            with open(f"{media_path}{media_sid}{file_extension}", 'wb') as f:
                f.write(req.content)
        print(media_files)

    respmsg = msg_analysis(msg, sessionph, media_files)

    resp = MessagingResponse()
    msg = resp.message("{}".format(respmsg))

    lines = respmsg.splitlines()
    line1 = lines[0]

    if 'Attachment' in line1 and len(lines)>1:
        file1 = lines[1].strip()
        my_path = 'https://www.onestoplogisticsco.com/'
        #my_path = 'http://12c157d5.ngrok.io/'
        my_url = my_path + file1
        print('myurl = ',my_url)
        msg.media(my_url)
    return str(resp)


@app.route('/AutoScanner', methods=['GET', 'POST'])
def AutoScanner():
    from isoM_autoscanner import isoMautoscanner
    vinlist = isoMautoscanner()
    return render_template('Avinlister.html', cmpdata=cmpdata, scac=scac, vinlist=vinlist)

@app.route('/QuoteMaker', methods=['GET', 'POST'])
def QuoteMaker():
    from iso_Q import isoQuote
    bidname, costdata, biddata, expdata, timedata, distdata, emaildata, locto, locfrom, dirdata, qdata, bidthis, taskbox, thismuch, quot, qdat = isoQuote()
    return render_template('Aquotemaker.html', cmpdata=cmpdata, scac=scac, costdata = costdata, biddata=biddata, expdata = expdata, timedata = timedata, distdata = distdata, locto=locto, locfrom=locfrom, emaildata = emaildata, dirdata=dirdata, qdata = qdata, bidthis=bidthis, taskbox = taskbox, thismuch=thismuch, quot=quot, qdat=qdat, bidname=bidname)


@app.route('/InvoiceMaint', methods=['GET', 'POST'])
def InvoiceMaint():

    from iso_InvM import isoInvM
    odata, oder, err, modata, modlink, leftscreen, leftsize, today, now, docref = isoInvM()
    rightsize = 12-leftsize
    return render_template('Ainvoicemaint.html',cmpdata=cmpdata, scac=scac,  data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, docref=docref)



@app.route('/Banking', methods=['GET', 'POST'])
def Banking():

    from iso_Bank import isoBank
    odata, oder, err, modata, modlink, leftscreen, leftsize, today, now, docref, cache, acdata, thismuch, acctinfo = isoBank()
    rightsize = 12-leftsize
    return render_template('Abanking.html', cmpdata=cmpdata, scac=scac, data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, docref=docref, cache = cache, acdata=acdata, thismuch=thismuch, acctinfo = acctinfo)

@app.route('/DriverMaint', methods=['GET', 'POST'])
def DriverMaint():

    from iso_Driver import isoDriver
    odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,docref,cache,thismuch = isoDriver()
    rightsize = 12-leftsize
    return render_template('Adriver.html', cmpdata=cmpdata, scac=scac, data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, docref=docref, cache = cache, thismuch=thismuch)

@app.route('/VehicleMaint', methods=['GET', 'POST'])
def VehicleMaint():

    from iso_Vehicle import isoTruck
    odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,docref,cache,thismuch = isoTruck()
    rightsize = 12-leftsize
    return render_template('Avehicle.html', cmpdata=cmpdata, scac=scac, data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, docref=docref, cache = cache, thismuch=thismuch)

@app.route('/IncomeMaint', methods=['GET', 'POST'])
def IncomeMaint():

    from iso_IncM import isoIncM
    odata, oder, err, modata, modlink, leftscreen, leftsize, today, now, docref, cache, acdata, thismuch, depdata = isoIncM()
    rightsize = 12-leftsize
    return render_template('Aincomemaint.html', cmpdata=cmpdata, scac=scac, data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, docref=docref, cache = cache, acdata=acdata, thismuch=thismuch, depdata=depdata)


@app.route('/AccountMaint', methods=['GET', 'POST'])
def AccountMaint():

    from iso_AM import isoAM
    odata, oder, err, modata, modlink, leftscreen, leftsize, today, now, scdata, companyon = isoAM()
    rightsize = 12-leftsize
    return render_template('Aaccountmaint.html', cmpdata=cmpdata, scac=scac, data1=odata, err=err, oder=oder, modata=modata, modlink=modlink, leftscreen=leftscreen,
                           leftsize=leftsize, rightsize=rightsize, scdata=scdata, companyon=companyon)


@app.route('/General', methods=['GET', 'POST'])
def General():

    from iso_G import isoG
    odata, oder, err, modata, modlink, leftscreen, docref, leftsize, fdata, filesel, today, now, doctxt, longs = isoG()
    rightsize = 12-leftsize
    return render_template('Ageneral.html', cmpdata=cmpdata, scac=scac, data1=odata, fdata=fdata, err=err, oder=oder, modata=modata, doctxt=doctxt, modlink=modlink, filesel=filesel, leftscreen=leftscreen,
                           docref=docref, leftsize=leftsize, rightsize=rightsize, longs=longs)

@app.route('/Compliance', methods=['GET', 'POST'])
def Compliance():

    from iso_C import isoC
    odata, oder, err, modata, modlink, leftscreen, docref, leftsize, fdata, filesel, today, now, doctxt, longs, acdata, actype = isoC()
    rightsize = 12-leftsize
    return render_template('Acompliance.html', cmpdata=cmpdata, scac=scac, data1=odata, fdata=fdata, err=err, oder=oder, modata=modata, doctxt=doctxt, modlink=modlink, filesel=filesel, leftscreen=leftscreen,
                           docref=docref, leftsize=leftsize, rightsize=rightsize, longs=longs, acdata=acdata, actype = actype)

@app.route('/EasyStart', methods=['GET', 'POST'])
def EasyStart():
    calbut=request.values.get('calbut')
    if calbut is not None:
        return redirect(url_for('CalendarBig'))

    srcpath = statpath('')
    return render_template('easystart.html', srcpath=srcpath, cmpdata=cmpdata, scac=scac)


@app.route('/Reports', methods=['GET', 'POST'])
def Reports():

    from iso_R import isoR
    cache, err, leftscreen, docref, leftsize, today, now, doctxt, sdate, fdate, fyear, customerlist, thiscomp, clist = isoR()
    rightsize = 12-leftsize
    return render_template('Areports.html', cmpdata=cmpdata, scac=scac, clist=clist, thiscomp=thiscomp, customerlist=customerlist, fyear=fyear, cache=cache, sdate=sdate, fdate=fdate, err=err, doctxt=doctxt, leftscreen=leftscreen, docref=docref, leftsize=leftsize, rightsize=rightsize)


@app.route('/CalendarBig', methods=['GET', 'POST'])
def CalendarBig():
    from viewfuncs import containersout, nonone
    from func_cal import calendar7_weeks_all

    if request.method == 'POST':
        calupdate = request.values.get('calupdate')
        today = datetime.datetime.today()
        datecut = today - datetime.timedelta(days=14)
        newc = containersout(datecut)
        if calupdate is not None:
            waft = request.values.get('waft')
            wbef = request.values.get('wbef')
            waft = nonone(waft)
            wbef = nonone(wbef)
            nweeks = [wbef, waft]
        else:
            nweeks = [2, 3]

    else:
        nweeks = [2, 3]

    caldays, daylist, weeksum, shlst = calendar7_weeks_all(nweeks)
    alltdata = Drivers.query.all()
    tdata = Vehicles.query.all()

    return render_template('AcalendarBIG.html', cmpdata=cmpdata, scac=scac, caldays=caldays, daylist=daylist, nweeks=nweeks, shlst=shlst, tdata=tdata, alltdata=alltdata)


@app.route('/CalendarBigV', methods=['GET'])
def CalendarBigV():
    from viewfuncs import containersout, nonone
    from func_cal import calendar7_weeks_all

    nweeks = [2, 2]

    caldays, daylist, weeksum, shlst = calendar7_weeks_all(nweeks)

    return render_template('AcalendarBIG.html', cmpdata=cmpdata, scac=scac, caldays=caldays, daylist=daylist, nweeks=nweeks, shlst=shlst)


@app.route('/People_Forms', methods=['GET', 'POST'])
def People_Forms():
    if request.method == 'POST':
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        appnum = 0
        vals = ['fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3',
                'idtype', 'tid', 'tel', 'email', 'assoc1', 'assoc2', 'date1', 'yrs']
        a = list(range(len(vals)))
        i = 0
        for v in vals:
            a[i] = request.values.get(v)
            i = i+1
        exporter = request.values.get('exporter')
        consignee = request.values.get('consignee')
        notify = request.values.get('notify')
        driver = request.values.get('driver')
        if exporter is not None:
            ptype = "exporter"
        if consignee is not None:
            ptype = "consignee"
        if notify is not None:
            ptype = "notify"
        if driver is not None:
            ptype = "applicant"
        try:
            company = a[0] + ' ' + a[2]
        except:
            company = a[0]

        input = People(Ptype=ptype, Company=company, First=a[0], Middle=a[1], Last=a[2], Addr1=a[3], Addr2=a[4], Addr3=a[5], Temp1=a[13], Temp2='NewApp',
                       Idtype=a[6], Idnumber=a[7], Telephone=a[8], Email=a[9], Associate1=a[10], Associate2=a[11], Date1=today, Date2=None, Original=None, Accountid=None)
        db.session.add(input)
        db.session.commit()

        if exporter is not None:
            ptype = "consignee"
        if consignee is not None:
            ptype = "notify"
        if notify is not None:
            ptype = "completed"
            pdata = People.query.filter(People.Temp2 == 'NewApp').all()
            for pdat in pdata:
                pdat.Temp2 = '2'
                db.session.commit()
            from email_appl import email_app_exporter
            email_app_exporter(pdata)

        if driver is not None:

            pdat = People.query.filter((People.Ptype == 'applicant') &
                                       (People.Company == company)).first()
            appnum = 'Fapp'+str(pdat.id)
            ptype = "completed"
            from email_appl import email_app
            email_app(pdat)

            return render_template('employment.html', cmpdata=cmpdata, scac=scac, ptype=ptype, appnum=appnum, phone=phone, today=today)
    else:
        ptype = "exporter"

    srcpath = statpath('')
    return render_template(f'companysite/{scac}/pforms.html', cmpdata=cmpdata, scac=scac, ptype=ptype, srcpath=srcpath)


@app.route('/Employment')
def Employment():
    ptype = 'driver'
    srcpath = statpath('')
    return render_template('employment.html', srcpath=srcpath, cmpdata=cmpdata, scac=scac, ptype=ptype, today=today.date(), phone=cmpdata[7],email=cmpdata[8])


@app.route('/Emailview', methods=['GET', 'POST'])
def EmailView():
    if request.method == 'POST':
        JO = request.values.get('jo')
        username = session['username'].capitalize()
        oc = Overseas.query.filter(Overseas.Jo == JO).first()
        oc.Status = 'LN'
        db.session.commit()
        text1 = 'Container Type: ' + oc.ContainerType + '\n' + 'Commodity: ' + \
            oc.Commodity + '\n' + 'Port of Destination: ' + oc.Pod + '\n'
        text2 = 'Port of Loading: ' + oc.Pol + '\n' + 'On or About Date: ' + str(oc.ApptDate) + '\n'
        text3 = 'Hazardous: No\n\nThank you in advance,\n'+username
        text4 = '\n\nThis quote is requested by ' + username + \
            ' at\nFirst Eagle Logistics\n505 Hampton Park Blvd Unit O\nCapitol Heights, MD  20743\n301-516-3000'
        texttable = text1 + text2 + text3 + text4
        destination = oc.Pod
        vcdata = Vocc.query.all()
        esent = 1
        for data in vcdata:
            sendthis = request.values.get(data.Name)
            if sendthis:
                agent = data.B_First
                emailto = data.B_Email
                esent = 0
                import emailquote
                emailquote.main(JO, texttable, agent, emailto, destination)

    return render_template('emailview.html', cmpdata=cmpdata, scac=scac, JO=JO, texttable=texttable, vcdata=vcdata, esent=esent)


@app.route('/MakeManifest', methods=['GET', 'POST'])
def MakeManifest():
    from iso_L import isoL
    odata, jtype, cdata1, cdata2, tdata, pdata, pval, alltdata, allvdata, description, location, docref, bol, time, time2, date2, retval = isoL()
    pval = 1
    print('jtype=', jtype, retval)
    if retval == 'O':
        return redirect('/OverseasV')
    if retval == 'T':
        return redirect('/Trucking')

    if jtype == 'Trucking' or jtype == 'Moving':
        return render_template('makemanifest.html', cmpdata=cmpdata, scac=scac, odata=odata, jtype=jtype, cdata1=cdata1, cdata2=cdata2, tdata=tdata, pdata=pdata, pval=pval,
                               alltdata=alltdata, allvdata=allvdata, description=description, location=location, docref=docref)
    else:
        return render_template('makemanifestO.html', cmpdata=cmpdata, scac=scac, odata=odata, jtype=jtype, cdata1=cdata1, cdata2=cdata2, tdata=tdata, pdata=pdata, pval=pval,
                               alltdata=alltdata, allvdata=allvdata, description=description, location=location, docref=docref, bol=bol, time=time, time2=time2, date2=date2)

# ____________________________________________________________________________________________________________________E.MANIFEST
# ____________________________________________________________________________________________________________________E.MANIFEST
# ____________________________________________________________________________________________________________________E.MANIFEST
# ____________________________________________________________________________________________________________________B.HORIZON
# ____________________________________________________________________________________________________________________B.HORIZON
# ____________________________________________________________________________________________________________________B.HORIZON


@app.route('/Dealer', methods=['GET', 'POST'])
def Dealer():
    from iso_H import isoH
    hdata, adata, pdata, idata, fdata, displdata, cars, invooder, auto, peep, err, modata, caldays, daylist, nweeks, invodate, doctxt, sdata, dlist, modlink, inco, invo, cache, filesel, leftscreen, docref, leftsize, jobdate = isoH()
    rightsize = 12-leftsize
    pdata1 = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
    return render_template('dealer.html', cmpdata=cmpdata, scac=scac, data1=hdata, data2=adata, data3=pdata, idata=idata, fdata=fdata, pdata1=pdata1, cars=cars,
                           invooder=invooder, auto=auto, peep=peep, err=err, modata=modata, caldays=caldays, daylist=daylist, nweeks=nweeks, invodate=invodate,
                           doctxt=doctxt, sdata=sdata, dlist=dlist, modlink=modlink, inco=inco, invo=invo, cache=cache, filesel=filesel, leftscreen=leftscreen,
                           docref=docref, leftsize=leftsize, rightsize=rightsize, jobdate=jobdate, displdata=displdata)
# ____________________________________________________________________________________________________________________E.HORIZON
# ____________________________________________________________________________________________________________________E.HORIZON
# ____________________________________________________________________________________________________________________E.HORIZON
# ____________________________________________________________________________________________________________________B.OVERSEAS
# ____________________________________________________________________________________________________________________B.OVERSEAS
# ____________________________________________________________________________________________________________________B.OVERSEAS


@app.route('/OverseasV', methods=['GET', 'POST'])
def OverseasV():

    from iso_O import isoO
    etitle, ebody, emaildata, thismuch, redir, odata, bdata, pdata, adata, idata, sdata, ship, keepship, book, auto, peep, tick, err, modata, caldays, daylist, nweeks, dlist, modlink, leftscreen, docref, stayslim, doctxt, leftsize, rightsize, ldata, invodate, inco, invo, invooder, cache, newc, alltdata, fdata, tdata, today, modal, ondock = isoO()

    if redir != 'stay':
        from iso_B import isoB
        bdata, cdata, bill, peep, err, modata, adata, acdata, expdata, modlink, caldays, daylist, weeksum, nweeks, addjobselect, jobdata, modal, dlist, fdata, today, cdat, pb, critday, vdata, leftscreen, docref, doctxt, leftsize, cache, filesel = isoB(
            redir)
        rightsize = 12-leftsize
        return render_template('Abilling.html', cmpdata=cmpdata, scac=scac, data1=bdata, data2=cdata, bill=bill, peep=peep, err=err, modata=modata, acdata=acdata, modlink=modlink,
                               caldays=caldays, daylist=daylist, weeksum=weeksum, nweeks=nweeks, addjobselect=addjobselect, jobdata=jobdata, modal=modal, dlist=dlist,
                               fdata=fdata, today=today, cdat=cdat, pb=pb, critday=critday, vdata=vdata, expdata=expdata,
                               leftscreen=leftscreen, docref=docref, doctxt=doctxt, leftsize=leftsize, rightsize=rightsize, cache=cache, filesel=filesel)

    else:
        pdata1 = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
        return render_template('Aoverseas.html', cmpdata=cmpdata, scac=scac, data1=odata, data2=bdata, data3=pdata, data4=adata, data5=idata, sdata=sdata, pdata1=pdata1, ship=ship, book=book,
                               auto=auto, peep=peep, tick=tick, err=err, modata=modata, caldays=caldays, daylist=daylist, nweeks=nweeks, dlist=dlist,
                               modlink=modlink, leftscreen=leftscreen, docref=docref, stayslim=stayslim, doctxt=doctxt, keepship=keepship,
                               leftsize=leftsize, rightsize=rightsize, ldata=ldata, invodate=invodate, inco=inco, invo=invo, invooder=invooder, cache=cache,
                               newc=newc, alltdata=alltdata, fdata=fdata, tdata=tdata, today=today, modal=modal, ondock=ondock, thismuch=thismuch, etitle=etitle, ebody=ebody,
                               emaildata=emaildata)

# ____________________________________________________________________________________________________________________E.OVERSEAS
# ____________________________________________________________________________________________________________________E.OVERSEAS
# ____________________________________________________________________________________________________________________E.OVERSEAS
@app.route('/MovingV', methods=['GET', 'POST'])
def MovingV():
    from iso_M import isoM
    odata, sdata, cdata, oder, sdata2, serv, peep, err, modata, caldays, daylist, nweeks, howapp, modlink, leftscreen, docref, stayslim, leftsize, newc, tdata, dlist, rightsize, ldata, invodate, inco, invo, invooder, cache, alltdata, fdata, filesel, today, now, doctxt, holdvec, pfdata = isoM()

    return render_template('Amoving.html', cmpdata=cmpdata, scac=scac, data1=odata, data4=sdata, data5=cdata, oder=oder, sdata=sdata2,
                           serv=serv, peep=peep, err=err, modata=modata, caldays=caldays, daylist=daylist, nweeks=nweeks, howapp=howapp,
                           modlink=modlink, leftscreen=leftscreen, docref=docref, stayslim=stayslim, leftsize=leftsize, newc=newc, tdata=tdata, dlist=dlist,
                           rightsize=rightsize, ldata=ldata, invodate=invodate, inco=inco, invo=invo, invooder=invooder, cache=cache, alltdata=alltdata,
                           fdata=fdata, filesel=filesel, today=today, now=now, doctxt=doctxt, holdvec=holdvec, pfdata=pfdata)


@app.route('/Trucking', methods=['GET', 'POST'])
def Trucking():
    from iso_T import isoT
    lbox, doclist, username, bklist, lastpr, thismuch, etitle, ebody, emaildata, odata, pdata, idata, sdata, cdata, oder, poof, sdata2, tick, serv, peep, err, modata, caldays, daylist, nweeks, howapp, modlink, leftscreen, docref, stayslim, leftsize, newc, tdata, drvdata,dlist, rightsize, ldata, invodate, inco, invo, quot, invooder, cache, stamp, alltdata, allvdata, stampdata, fdata, filesel, today, now, doctxt, holdvec, mm1, viewtype = isoT()

    return render_template('Atrucking.html', cmpdata=cmpdata, scac=scac, data1=odata, data2=pdata, data3=idata, data4=sdata, data5=cdata, oder=oder, poof=poof, sdata=sdata2,
                           tick=tick, serv=serv, peep=peep, err=err, modata=modata, caldays=caldays, daylist=daylist, nweeks=nweeks, howapp=howapp, doclist=doclist,
                           modlink=modlink, leftscreen=leftscreen, docref=docref, stayslim=stayslim, leftsize=leftsize, newc=newc, tdata=tdata, dlist=dlist,
                           rightsize=rightsize, ldata=ldata, invodate=invodate, inco=inco, invo=invo, invooder=invooder, cache=cache, stamp=stamp, alltdata=alltdata,
                           stampdata=stampdata, fdata=fdata, filesel=filesel, today=today, now=now, doctxt=doctxt, holdvec=holdvec, etitle=etitle, ebody=ebody, lbox=lbox,
                           emaildata=emaildata, thismuch=thismuch, mm1=mm1, allvdata=allvdata,drvdata=drvdata, bklist = bklist, lastpr = lastpr, quot = quot, username = username, viewtype=viewtype)

# ____________________________________________________________________________________________________________________B.STORAGE
# ____________________________________________________________________________________________________________________B.STORAGE
# ____________________________________________________________________________________________________________________B.STORAGE
@app.route('/StorageC', methods=['GET', 'POST'])
def StorageC():
    from iso_S import isoS
    odata, cdata, sdata, oder, peep, serv, err, modata, modlink, fdata, today, inco, leftscreen, docref, leftsize, ldata, monsel, monvec, invo, invooder, invojo, cache, filesel, bm, cm, invodate = isoS()
    rightsize = 12-leftsize
    return render_template('Astorage.html', cmpdata=cmpdata, scac=scac, data1=odata, data2=cdata, sdata=sdata, oder=oder, peep=peep, serv=serv, err=err, modata=modata,
                           modlink=modlink, fdata=fdata, today=today, inco=inco,
                           leftscreen=leftscreen, docref=docref, leftsize=leftsize, rightsize=rightsize, ldata=ldata, monsel=monsel, monvec=monvec,
                           invo=invo, invooder=invooder, invojo=invojo, cache=cache, filesel=filesel, bm=bm, cm=cm, invodate=invodate)


@app.route('/Calculator', methods=['GET', 'POST'])
def Calculator():
    import ast
    from viewfuncs import d2s
    if request.method == 'POST':
        alldata = request.values.get('alldata')
        alldata = ast.literal_eval(alldata)
        print(alldata)
        l = len(alldata)
        print(l)
        a1 = request.form['len']
        a2 = request.form['wid']
        a3 = request.form['hei']
        a4 = float(a1)*float(a2)*float(a3)
        a6 = request.form['unt']
        a7 = request.form['wtunt']
        b1 = request.form['cst']
        b1 = Decimal(b1.strip('$'))
        a6 = int(a6)
        a7 = int(a7)
        if a6 == 1:
            a4 = a4/61023.7
        if a6 == 2:
            a4 = a4/35.3147
        if a6 == 3:
            a4 = a4/1000000.
        wtkg = a4*166.67
        wtlb = wtkg*2.20462
        wtkgstr = d2s(str(wtkg))
        wtlbstr = d2s(str(wtlb))
        a5 = math.ceil(a4)
        a4 = round(a4, 2)
        b2 = a5*float(b1)
        if a7 == 1:
            wt = wtlbstr
        else:
            wt = wtkgstr
        total = float(wt)
        for data in alldata:
            total = total+float(data[3])

        alldata.append([a1, a2, a3, wt])

        # Recalculate all in case units have changed
        newalldata = []
        total = 0
        for data in alldata:
            a1 = data[0]
            a2 = data[1]
            a3 = data[2]
            a4 = float(a1)*float(a2)*float(a3)
            if a6 == 1:
                a4 = a4/61023.7
            if a6 == 2:
                a4 = a4/35.3147
            if a6 == 3:
                a4 = a4/1000000.
            if a7 == 2:
                wt = a4*166.67
            if a7 == 1:
                wt = a4*166.67*2.20462
            total = total+float(wt)
            newalldata.append([a1, a2, a3, d2s(wt)])
        a4 = round(a4, 2)
        finalcost = total*float(b1)
        finalwt = d2s(total)
        finalcost = d2s(finalcost)

    else:
        a1 = 1
        a2 = 1
        a3 = 1
        a4 = 1
        a5 = 1
        a6 = 1
        a7 = 1
        b1 = 25
        b2 = 1
        wtkgstr = ''
        wtlbstr = ''
        alldata = []
        fdata = []
        newalldata = []
        finalwt = ''
        finalcost = ''
    srcpath = statpath('')
    return render_template('calculator.html', srcpath=srcpath,cmpdata=cmpdata, scac=scac, finalcost=finalcost, a1=a1, a2=a2, a3=a3, a4=a4, a5=a5, a6=a6, a7=a7, b1=b1, b2=b2, wtkg=wtkgstr, wtlb=wtlbstr, alldata=newalldata, finalwt=finalwt)


# ____________________________________________________________________________________________________________________B.Billing
@app.route('/Billing', methods=['GET', 'POST'])
def Billing():
    from iso_B import isoB
    #from CCC_system_setup import klist
    username, divdat, hv, bdata, cdata, bill, peep, err, modata, adata, acdata, expdata, modlink, caldays, daylist, weeksum, nweeks, addjobselect, jobdata, modal, dlist, fdata, today, cdat, pb, critday, vdata, leftscreen, docref, doctxt, leftsize, cache, filesel = isoB(0)
    rightsize = 12-leftsize
    return render_template('Abilling.html', cmpdata=cmpdata, scac=scac, data1=bdata, data2=cdata, bill=bill, peep=peep, err=err, modata=modata, acdata=acdata, modlink=modlink,
                           caldays=caldays, daylist=daylist, weeksum=weeksum, nweeks=nweeks, cdata=cdata, addjobselect=addjobselect, jobdata=jobdata, modal=modal, dlist=dlist,
                           fdata=fdata, today=today, cdat=cdat, pb=pb, critday=critday, vdata=vdata, expdata=expdata, hv = hv, divdat=divdat, username=username,
                           leftscreen=leftscreen, docref=docref, doctxt=doctxt, leftsize=leftsize, rightsize=rightsize, cache=cache, filesel=filesel)
# ____________________________________________________________________________________________________________________E.Billing

# ____________________________________________________________________________________________________________________B.Login
# ____________________________________________________________________________________________________________________B.Login
# ____________________________________________________________________________________________________________________B.Login
# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username_input = request.form['username']
        password_candidate = request.form['password']

        # Get user by username
        result = users.query.filter_by(username=username_input).first()

        if result is not None:

            app.logger.info('USER FOUND')
            # This is temporary, need to encrypt data stored in database
            # before release
            passhash = result.password

            if password_candidate == passhash:
                session['logged_in'] = True
                session['username'] = username_input
                return redirect(url_for('EasyStart'))
            else:
                app.logger.info('PASSWORDS DO NOT MATCH')
                error = 'Passwords do not match'
                return render_template('login.html', error=error, cmpdata=cmpdata, scac=scac)

        else:
            error = 'Username not found'
            return render_template('login.html', error=error, cmpdata=cmpdata, scac=scac)

    return render_template('login.html',cmpdata=cmpdata, scac=scac)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
