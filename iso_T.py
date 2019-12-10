from runmain import db
from models import Gledger, Vehicles, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Proofs, Services, Drops
from flask import render_template, flash, redirect, url_for, session, logging, request
from CCC_system_setup import myoslist, addpath, tpath, companydata, scac
from InterchangeFuncs import Order_Container_Update, Matched_Now
from iso_InvM import updateinvo
from email_appl import etemplate_truck

import math
from decimal import Decimal
import datetime
import calendar
import os
import subprocess
import shutil
import re
from func_cal import calmodalupdate
from PyPDF2 import PdfFileReader
import json


def dataget_T(thismuch, dlist):
    # 0=order,#1=proofs,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    odata = 0
    pdata = 0
    idata = 0
    if thismuch == '1':
        stopdate = today-datetime.timedelta(days=60)
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Date > stopdate).all()
        if dlist[1] == 'on':
            pdata = Proofs.query.filter(Proofs.Date > stopdate).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '2':
        stopdate = today-datetime.timedelta(days=120)
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Date > stopdate).all()
        if dlist[1] == 'on':
            pdata = Proofs.query.filter(Proofs.Date > stopdate).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '3':
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Istat<2).all()
        if dlist[1] == 'on':
            pdata = Proofs.query.filter(Proofs.Status != 'Paid').all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '4':
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Istat<4).all()
        if dlist[1] == 'on':
            pdata = Proofs.query.filter(Proofs.Status != 'Paid').all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    else:
        if dlist[0] == 'on':
            odata = Orders.query.all()
        if dlist[1] == 'on':
            pdata = Proofs.query.all()
        if dlist[2] == 'on':
            idata = Interchange.query.all()
    return odata, pdata, idata

def erud(err):
    errup = ''
    for e in err:
        if len(e) > 0:
            errup = errup + e.strip() + '\n'
    return errup


def isoT():

    if request.method == 'POST':
        # ____________________________________________________________________________________________________________________B.FormVariables.Trucking

        from viewfuncs import parseline, tabdata, tabdataR, popjo, jovec, newjo, timedata, nonone, nononef, init_truck_zero, dropupdate, dropupdate2, dropupdate3
        from viewfuncs import d2s, stat_update, numcheck, numcheckv, sdiff, calendar7_weeks, viewbuttons, get_ints, containersout, numcheckvec
        from viewfuncs import txtfile, doctransfer, getexpimp, docuploader
        from InterchangeFuncs import InterStrip, InterMatchThis, InterDupThis, PushJobsThis
        from invoice_mimemail import invoice_mimemail
        from invoice_makers import multi_inv
        from gledger_write import gledger_write

        # Zero and blank items for default
        username = session['username'].capitalize()
        pod_path = f'processing/pods/'
        job_path = f'processing/tjobs/'
        int_path = f'processing/interchange/'
        oder, poof, tick, serv, peep, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_truck_zero()
        filesel = ''
        docref = ''
        doctxt = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        stampdata = ''
        drvdata=0
        reorder=0
        bklist = 0
        lastpr = request.values.get('lastpr')



        today = datetime.date.today()
        today_dt = datetime.date.today()
        today_str = today_dt.strftime('%Y-%m-%d')
        now = datetime.datetime.now()
        now = now.time()
        now_str24 = now.strftime('%H:%M')
        now_str12 = now.strftime('%I:%M %p')

        leftsize = 10
        howapp = 0
        newc = 'Not found at top'

        match, modify, vmod, minvo, mpack, viewo, viewi, viewp, printn, addE, addS, slim, stayslim, unslim, limitptype, returnhit, deletehit, update, invoupdate, emailnow, emailinvo, newjob, thisjob, recpay, hispay, recupdate, calendar, calupdate = viewbuttons()
        stampnow = request.values.get('stampnow')
        #emailnow2 = request.values.get('emailnow2')
        #emailinvo2 = request.values.get('emailInvo2')
        loginvo = request.values.get('logInvo')
        logrec = request.values.get('logRec')
        reorder = request.values.get('reorder')
        unpay = request.values.get('Unpay')
        uninv = request.values.get('Uninv')
        addI = request.values.get('addinterchange')
        copy = request.values.get('copy')
        datatable1 = request.values.get('datatable1')
        datatable2 = request.values.get('datatable2')
        datatable3 = request.values.get('datatable3')
        datatable4 = request.values.get('datatable4')
        dlist = [datatable1, datatable2, datatable3, datatable4]
        addP = request.values.get('addproof')
        loadc = request.values.get('loadc')
        thismuch = request.values.get('thismuch')
        acceptthese = request.values.get('accept')
        payview = request.values.get('payview')
        mm2 = request.values.get('manifest')
        mquot = request.values.get('MakeQ')
        quotupdate = request.values.get('quotUpdate')
        uploadS = request.values.get('UploadS')
        uploadP = request.values.get('UploadP')



        if mm2 is not None:
            mm1 = 1
        else:
            mm1 = request.values.get('passmanifest')
            mm1=nonone(mm1)

        holdvec = [0]*3
        oder, poof, tick, serv, peep, invo, invooder, cache, modlink = get_ints()
        quot = 0

        stamp = request.values.get('stamp')
        leftscreen = 1
        err = ['All is well', ' ', ' ', ' ', ' ']
        ldata = None
        stamp = nonone(stamp)
        tdata = 0

        if returnhit is not None:
            modlink = 0
            invo = 0
            invooder = 0
            stamp = 0
            inco = 0
            oder = 0
            quot = 0
            mm1 = 0

        if modlink == 70:
            err = docuploader('oder')
            modlink = 0

# ____________________________________________________________________________________________________________________E.FormVariables.Trucking
# ____________________________________________________________________________________________________________________B.DataUpdates.Trucking
        if update is not None and modlink == 4 and peep > 0:
            modata = People.query.get(peep)
            vals = ['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3',
                    'idtype', 'tid', 'tel', 'email', 'assoc1', 'assoc2', 'date1']
            a = list(range(len(vals)))
            i = 0
            for v in vals:
                a[i] = request.values.get(v)
                i = i+1
            modata.Company = a[0]
            modata.First = a[1]
            modata.Middle = a[2]
            modata.Last = a[3]
            modata.Addr1 = a[4]
            modata.Addr2 = a[5]
            modata.Addr3 = a[6]
            modata.Idtype = a[7]
            modata.Idnumber = a[8]
            modata.Telephone = a[9]
            modata.Email = a[10]
            modata.Associate1 = a[11]
            modata.Associate2 = a[12]
            modata.Date1 = a[13]
            err = [' ', ' ', 'Modification to Entity ID ' +
                   str(modata.id) + ' completed.', ' ',  ' ']
            db.session.commit()
            peep = 0

        if modlink == 20 or modlink == 21:
            if modlink == 20:
                fpath = f'tmp/{scac}/{int_path}'
            else:
                fpath = f'tmp/{scac}/{pod_path}'

            if update is None:
                leftscreen = 0
                leftsize = 8
                filesel = request.values.get('FileSel')

                base = os.path.splitext(filesel)[0]
                docref = fpath + filesel
                doctxt = fpath + base + '.txt'

                if modlink == 21:
                    modata = Proofs.query.get(poof)
                    #Save values placed in table thus far:
                    vals = ['order', 'bol', 'container', 'booking',
                            'shipper', 'location', 'proofdate', 'prooftime']
                    a = list(range(len(vals)))
                    i = 0
                    for v in vals:
                        a[i] = request.values.get(v)
                        i = i + 1
                    modata.Order = a[0]
                    modata.BOL = a[1]
                    modata.Container = a[2]
                    modata.Booking = a[3]
                    modata.Company = a[4]
                    modata.Location = a[5]
                    modata.Date = a[6]
                    modata.Time = a[7]
                    db.session.commit()

                delf = request.values.get('DELF')
                if delf is not None:
                    try:
                        os.remove(addpath(docref))
                        err[1] = 'File deleted'
                    except:
                        err[1] = 'File not deleted'
                    try:
                        os.remove(addpath(doctxt))
                        err[1] = 'File deleted'
                    except:
                        err[1] = 'File not deleted'
                    docref = f'tmp/{scac}/data/vunknown/NewJob.pdf'

            if update is not None:
                filesel = request.values.get('FileSel')
                if modlink == 20:
                    docref, doctxt = doctransfer('interchange', 'vinterchange', filesel)
                    myt = Interchange.query.get(tick)
                    myt.Original = docref
                    db.session.commit()
                    modlink = 1
                    InterStrip(tick)
                    InterMatchThis(tick)
                    InterDupThis(tick)
                    PushJobsThis(tick)

                if modlink == 21:
                    docref, doctxt = doctransfer('pods', 'vproofs', filesel)
                    myt = Proofs.query.get(poof)
                    myt.Original = docref
                    db.session.commit()
                    modlink = 1

        if update is not None and modlink == 2:
            modata = Services.query.get(serv)
            vals = ['service', 'price']
            a = list(range(len(vals)))
            i = 0
            for v in vals:
                a[i] = request.values.get(v)
                i = i+1
            input = Services(Service=a[0], Price=a[1])
            db.session.add(input)
            db.session.commit()
            err = [' ', ' ', 'New Service Added to Database.', ' ',  ' ']
            modlink = 0

        if update is None and modlink == 1:
            if oder > 0:
                fdata = myoslist(job_path)
                fdata.sort()
                filesel = request.values.get('FileSel')
                cdata = People.query.filter(
                    People.Ptype == 'Trucking').order_by(People.Company).all()
                leftsize = 8
                leftscreen = 0
                docref = f'tmp/{scac}/processing/tjobs/'+filesel
                doctxt = docref.split('.', 1)[0]+'.txt'
                modata = Orders.query.get(oder)

        if update is not None and modlink == 1:
            if oder > 0:
                fdata = myoslist(job_path)
                filesel = request.values.get('FileSel')
                modata = Orders.query.get(oder)
                if filesel in fdata and filesel != 1:
                    modata.Original = filesel
                    docold = f'tmp/{scac}/processing/tjobs/'+filesel
                    docref = f'tmp/{scac}/data/vorders/'+filesel
                    oldtxt = docold.split('.', 1)[0]+'.txt'
                    doctxt = docref.split('.', 1)[0]+'.txt'
                    if 1 == 1:  # try:
                        shutil.move(addpath(docold), addpath(docref))
                        shutil.move(addpath(oldtxt), addpath(doctxt))
                    if 1 == 2:  # except:
                        err[4] = 'File has been moved already'
                hstat = modata.Hstat
                if hstat == -1:
                    modata.Hstat = 0
                vals = ['load', 'order', 'bol', 'booking', 'container', 'pickup',
                        'date', 'time', 'date2', 'time2', 'amount', 'ctype']
                a = list(range(len(vals)))
                for i, v in enumerate(vals):
                    a[i] = request.values.get(v)

                shipper = request.values.get('shipper')
                modata.Shipper = shipper

                dropblock1 = request.values.get('dropblock1')
                dropblock2 = request.values.get('dropblock2')

                idl = 0
                idd = 0

                print('291:',dropblock1)
                print('292:',dropblock2)
                print('293:',len(dropblock1.strip()),len(dropblock2.strip()))

                if len(dropblock1.strip())<7:
                    sfind = dropblock1.strip()
                    sfind = sfind[0:2]
                    print(sfind)
                    sfind = sfind.lower()
                    ddata = Drops.query.all()
                    for ddat in ddata:
                        entity=ddat.Entity
                        scomp = entity[0:2]
                        scomp = scomp.lower()
                        if sfind == scomp:
                            idl = ddat.id
                            newdrop1 = ddat.Entity + '\n' + ddat.Addr1 + '\n' + ddat.Addr2 + '\n' + ddat.Phone + '\n' + ddat.Email
                            company = ddat.Entity
                            break

                if len(dropblock2.strip())<7:
                    sfind = dropblock2.strip()
                    sfind = sfind[0:2]
                    sfind = sfind.lower()
                    ddata = Drops.query.all()
                    for ddat in ddata:
                        entity=ddat.Entity
                        entity = entity.strip()
                        scomp = entity[0:2]
                        scomp = scomp.lower()
                        if sfind == scomp:
                            idd = ddat.id
                            newdrop2 = ddat.Entity + '\n' + ddat.Addr1 + '\n' + ddat.Addr2 + '\n' + ddat.Phone + '\n' + ddat.Email
                            company2 = ddat.Entity
                            break

                if idl == 0:
                    company = dropupdate(dropblock1)
                    newdrop1 = dropblock1
                    lid = Drops.query.filter(Drops.Entity == company).first()
                    idl = lid.id

                if idd == 0:
                    company2 = dropupdate(dropblock2)
                    newdrop2 = dropblock2
                    did = Drops.query.filter(Drops.Entity == company2).first()
                    idd = did.id

                modata.Company2 = company2
                modata.Company = company
                modata.Dropblock2 = newdrop2
                modata.Dropblock1 = newdrop1
                bid = People.query.filter(People.Company == shipper).first()
                if bid is not None:
                    modata.Bid = bid.id
                modata.Lid = idl
                modata.Did = idd
                modata.Load = a[0]
                modata.Order = a[1]
                modata.BOL = a[2]
                modata.Booking = a[3]
                modata.Container = a[4]
                modata.Pickup = a[5]
                modata.Type = a[11]
                try:
                    modata.Date = a[6]
                except:
                    modata.Date = None
                    err[5] = 'Bad Date Value'
                modata.Time = a[7]
                try:
                    modata.Date2 = a[8]
                except:
                    modata.Date2 = None
                    err[5] = 'Bad Date Value'
                modata.Time2 = a[9]
                modata.Amount = d2s(a[10])
                try:
                    modata.Label = modata.Jo+' '+a[1]+' '+shipper+' ' + a[10]
                except:
                    modata.Label = modata.Jo+' '+shipper

                db.session.commit()
                err[3] = 'Modification to Trucking JO ' + modata.Jo + ' completed.'
                modlink = 0
                Order_Container_Update(oder)

            if poof > 0:
                modata = Proofs.query.get(poof)
                vals = ['order', 'bol', 'container', 'booking',
                        'shipper', 'location', 'proofdate', 'prooftime']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                filesel = request.values.get('FileSel')
                modata.Order = a[0]
                modata.BOL = a[1]
                modata.Container = a[2]
                modata.Booking = a[3]
                modata.Company = a[4]
                modata.Location = a[5]
                modata.Date = a[6]
                modata.Time = a[7]
                db.session.commit()
                err = [' ', ' ', 'Modification to Proof ' +
                       str(modata.id) + ' completed.', ' ',  ' ']

            if tick > 0:
                modata = Interchange.query.get(tick)
                vals = ['intcontainer', 'intdate', 'inttime', 'chassis', 'release',
                        'truck', 'grosswt', 'driver', 'type', 'cargowt', 'contype']
                a = list(range(len(vals)))
                for i, v in enumerate(vals):
                    a[i] = request.values.get(v)
                modata.CONTAINER = a[0]
                modata.Date = a[1]
                modata.Time = a[2]
                modata.CHASSIS = a[3]
                modata.RELEASE = a[4]
                modata.TRUCK_NUMBER = a[5]
                modata.GROSS_WT = a[6]
                modata.DRIVER = a[7]
                modata.TYPE = a[8]
                modata.CARGO_WT = a[9]
                modata.CONTYPE = a[10]

                modata.Status = 'BBBBBB'

                db.session.commit()

                err = [' ', ' ', 'Modification to Interchange Ticket with ID ' +
                       str(modata.id) + ' completed.', ' ',  ' ']
                modlink = 0
                # db.session.close()
                InterStrip(tick)
                InterMatchThis(tick)
                InterDupThis(tick)
                PushJobsThis(tick)
                idata = Interchange.query.order_by(
                    Interchange.Date.desc()).order_by(Interchange.Time.desc()).all()

            if serv > 0:
                modata = Services.query.get(serv)
                vals = ['service', 'price']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.Service = a[0]
                modata.Price = a[1]
                db.session.commit()
                err = [' ', ' ', 'Modification to Services Data with ID ' +
                       str(modata.id) + ' completed.', ' ',  ' ']
                modlink = 0

            if peep > 0:
                modata = People.query.get(peep)
                vals = ['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3',
                        'idtype', 'tid', 'tel', 'email', 'assoc1', 'assoc2', 'date1']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.Company = a[0]
                modata.First = a[1]
                modata.Middle = a[2]
                modata.Last = a[3]
                modata.Addr1 = a[4]
                modata.Addr2 = a[5]
                modata.Addr3 = a[6]
                modata.Idtype = a[7]
                modata.Idnumber = a[8]
                modata.Telephone = a[9]
                modata.Email = a[10]
                modata.Associate1 = a[11]
                modata.Associate2 = a[12]
                modata.Date1 = a[13]
                err = [' ', ' ', 'Modification to Entity ID ' +
                       str(modata.id) + ' completed.', ' ',  ' ']
                modlink = 0
                db.session.commit()
# ____________________________________________________________________________________________________________________E.DataUpdates.Trucking
# ____________________________________________________________________________________________________________________B.InvoiceUpdate.Trucking
        if invoupdate is not None or quotupdate is not None:
            print('invoupdate')
            if quotupdate is not None:
                quot = 1
                invo = 1
            leftsize = 8
            odata1 = Orders.query.get(invooder)

            invodate = request.values.get('invodate')
            if invodate is None:
                invodate = today
            if isinstance(invodate, str):
                invodate = datetime.datetime.strptime(invodate, '%Y-%m-%d')
            ldata = Invoices.query.filter(Invoices.Jo == odata1.Jo).all()
            itotal = 0
            icode = ''
            for data in ldata:
                iqty = request.values.get('qty'+str(data.id))
                iqty = nononef(iqty)
                data.Description = request.values.get('desc'+str(data.id))
                deach = request.values.get('cost'+str(data.id))
                if deach is not None:
                    damount = float(iqty)*float(deach)
                    itotal = itotal+damount
                    deach = "{:.2f}".format(float(deach))
                    damount = "{:.2f}".format(damount)
                else:
                    damount = "{:.2f}".format(0.00)
                    deach = "{:.2f}".format(0.00)
                print('iqtyhere=',iqty)
                data.Qty = iqty
                data.Ea = deach
                icode = icode+'+'+str(data.Qty)+'*'+str(data.Ea)
                data.Amount = damount
                data.Date = invodate
                db.session.commit()

            for data in ldata:
                data.Total = itotal
                db.session.commit()

            # Remove zeros from invoice in case a zero was the mod
            Invoices.query.filter(Invoices.Qty == 0).delete()
            db.session.commit()
            # Create invoice code for order
            odata1.Istat = 1
            myp = Proofs.query.filter(Proofs.Order == odata1.Order).first()
            if myp is not None:
                myp.Status = 'Invoiced'

            db.session.commit()
# ____________________________________________________________________________________________________________________E.InvoiceUpdate.Trucking

# ____________________________________________________________________________________________________________________B.GetData.Trucking
        odata, pdata, idata = dataget_T(thismuch, dlist)
        ##query.filter(or_(MyTable.info == None, ~MyTable.info.contains(['Recalled'])))
        #pdata = Proofs.query.order_by(Proofs.Date).all()
        #idata = Interchange.query.order_by(Interchange.Date.desc()).order_by(Interchange.Time.desc()).all()
        sdata = Services.query.order_by(Services.Price.desc()).all()
        cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
# ____________________________________________________________________________________________________________________E.GetData.Trucking
# ____________________________________________________________________________________________________________________B.Search.Trucking

        if (modlink < 10 and (update is not None or vmod is not None)) or modlink == 0:
            oder, poof, tick, serv, peep, numchecked = numcheck(5, odata, pdata, idata, sdata, cdata, [
                                                                'oder', 'poof', 'tick', 'serv', 'peep'])
        if match is not None or mm1 > 0:
            oder, poof, tick, serv, peep, numchecked = numcheck(5, odata, pdata, idata, sdata, cdata, [
                                                                'oder', 'poof', 'tick', 'serv', 'peep'])


        if uploadS is not None:
            err = ['No Job Selected for Source Upload']
            if oder > 0  and numchecked == 1:
                modlink = 70
                modata = Orders.query.get(oder)
                modata.Original = 'star'
                db.session.commit()
            else:
                err.append('Select One Box')

        if uploadP is not None:
            err = ['No Job Selected for Proof Upload']
            if oder > 0  and numchecked == 1:
                modlink = 70
                modata = Orders.query.get(oder)
                modata.Proof = 'star'
                db.session.commit()
            else:
                err.append('Select One Box')


        print('starting with mm1=',mm1)

        if mm1 == 1:

            truck='111'
            if oder == 0:
                oder=request.values.get('passoder')
                print('oderherenow is',oder)
                oder=nonone(oder)
            if update is not None:
                modata = Orders.query.get(oder)
                vals = ['driver', 'truck', 'commodity', 'packing', 'pickup', 'seal', 'date1',
                        'time1', 'date2','time2', 'desc']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    print(a[i])
                    i = i+1
                truck=a[1]
                modata.Driver=a[0]
                modata.Commodity = a[2]
                modata.Packing = a[3]
                modata.Pickup = a[4]
                modata.Seal = a[5]
                modata.Date = a[6]
                modata.Time = a[7]
                modata.Date2 = a[8]
                modata.Time2 = a[9]
                modata.Description = a[10]
                cache = int(modata.Detention)+1
                cache=cache+1
                modata.Detention=cache
                db.session.commit()



            leftscreen=0
            mm1=1
            print('oderhere is',oder)


            from makemanifest2 import makemanifestT
            modata = Orders.query.get(oder)
            pid = modata.Bid
            pdata1 = People.query.get(pid)
            jtype='Trucking'
            print('drv',modata.Driver)
            drvdata=Drivers.query.filter(Drivers.Name==modata.Driver).first()
            if drvdata is None:
                drvdata = Drivers.query.filter(Drivers.id > 1).first()
            cache = int(modata.Detention)
            time1=modata.Time
            time2=modata.Time2
            commodity=request.values.get('commodity')
            packing=request.values.get('packing')
            bol=request.values.get('bol')
            tdata=Vehicles.query.filter(Vehicles.Unit==truck).first()
            if tdata is None:
                tdata = Vehicles.query.filter(Vehicles.id > 1).first()
            docref=makemanifestT(modata, pdata1, None, None, tdata, drvdata, cache, jtype, time1, time2, commodity, packing, bol)

        # Need this comment
        if unpay is not None:
            odat = Orders.query.get(oder)
            odat.Istat = 3
            if odat.Hstat == 4:
                odat.Hstat = 3
            db.session.commit()
            idata = Invoices.query.filter(Invoices.Jo == odat.Jo).all()
            for data in idata:
                data.Status = 'New'
                db.session.commit()
            Income.query.filter(Income.Jo == odat.Jo).delete()
            Gledger.query.filter((Gledger.Tcode == odat.Jo) & (Gledger.Type == 'IC')).delete()
            db.session.commit()

        # Need this comment
        if uninv is not None:
            odat = Orders.query.get(oder)
            odat.Istat = 0
            odat.Links = None
            db.session.commit()
            Invoices.query.filter(Invoices.Jo == odat.Jo).delete()
            Income.query.filter(Income.Jo == odat.Jo).delete()
            Gledger.query.filter(Gledger.Tcode == odat.Jo).delete()
            db.session.commit()


# ____________________________________________________________________________________________________________________E.Search.Trucking
# ____________________________________________________________________________________________________________________B.Package.Trucking
        if reorder is not None or stampnow is not None:
            oder=request.values.get('passoder')
            oder=nonone(oder)
            odat=Orders.query.get(oder)
            pdat=Proofs.query.filter(Proofs.Order==odat.Order).first()
            idata=Interchange.query.filter(Interchange.CONTAINER==odat.Container).all()
            packitems=[]
            stampdata=[]
            stampdata = [0]*9
            for i in range(9):
                stampdata[i] = request.values.get('stampdata'+str(i))
            for i in range(4):
                packname='section'+str(i+1)
                print(packname)
                test=request.values.get(packname)
                if test != 'none':
                    if test == 'loadconfirm':
                        packitems.append(addpath(f'tmp/{scac}/data/vorders/'+odat.Original))
                        stampdata.append('loadconfirm')
                    if test == 'invoice':
                        packitems.append(addpath(odat.Path))
                        stampdata.append('invoice')
                    if test == 'proofs' and pdat is not None:
                        packitems.append(addpath(pdat.Original))
                        stampdata.append('proofs')
                    if test == 'ticks' and idata is not None:
                        stampdata.apend('ticks')
                        for idat in idata:
                            packitems.append(addpath(idat.Original))
                else:
                    stampdata.append('none')
                    print('packitems final:',packitems)
                    print('stampdata final:',stampdata)

            cache2 = int(odat.Detention)
            cache2 = cache2+1
            docref = f'tmp/{scac}/data/vorders/P_c'+str(cache2)+'_' + odat.Original
            docin = f'tmp/{scac}/data/vorders/P_c'+str(cache2)+'_' + odat.Original
            pdflist=['pdfunite']+packitems+[addpath(docref)]
            tes = subprocess.check_output(pdflist)
            odat.Location = docref
            odat.Detention = cache2
            db.session.commit()
            print('docref=',docref)
            leftscreen = 0
            stampstring = json.dumps(stampdata)
            cdat=People.query.get(int(odat.Bid))
            cdat.Original=stampstring
            db.session.commit()
            #Get the email data also in case changes occur there
            emaildata = [0]*6
            for i in range(6):
                emaildata[i] = request.values.get('edat'+str(i))

        if mpack is not None and numchecked == 1:
            err = ['Must have order, proof and invoice complete to make this selection', ' ', ' ', ' ',  ' ']
            if oder > 0:
                odata1 = Orders.query.get(oder)
                company = odata1.Shipper
                pdata1 = Proofs.query.filter(Proofs.Order == odata1.Order).first()
                ofile = odata1.Original
                cdat = People.query.get(int(odata1.Bid))

                jo = odata1.Jo
                order = odata1.Order
                stampstring = cdat.Original
                print('the stampstring=',stampstring)
                try:
                    stampdata = json.loads(stampstring)
                except:
                    stampdata = [3, 35, 35, 5, 120, 100, 5, 477, 350,'loadconfirmation','proofs','invoice','none']

                emaildata = etemplate_truck('invoice',1,data1.Bid,jo.order)
                invo = 3

                if ofile is None:
                    err[2] = 'No original order data'
                else:
                    docref1 = f'tmp/{scac}/data/vorders/' + odata1.Original
                docref3 = odata1.Path
                if pdata1 is None:
                    err[3] = 'No Proof data'
                else:
                    docref2 = pdata1.Original
                if docref3 is None:
                    err[4] = 'No Invoice data'
            else:
                err[1] = 'No Order data'

            if oder > 0 and pdata1 and docref3 and ofile:
                err = ['Sign the package', ' ', ' ', ' ',  ' ']
                stamp = 1
                invooder = oder
                leftscreen = 0
                leftsize = 8
                modlink = 0
                cache2 = int(odata1.Detention)
                cache2 = cache2+1
                # sandiwich it all together
                docref = f'tmp/{scac}/data/vorders/P_c'+'_' + odata1.Original
                if 'Knight' in company:
                    tes = subprocess.check_output(['pdfunite', addpath(
                        docref1), addpath(docref2), addpath(docref3), addpath(docref)])
                else:
                    try:
                        tes = subprocess.check_output(['pdfunite', addpath(
                            docref3), addpath(docref2), addpath(docref1), addpath(docref)])
                    except:
                        odata1.Original = 'temp.pdf'
                        docref = f'tmp/{scac}/data/vorders/P_c'+'_' + 'temp.pdf'
                        tes = subprocess.check_output(
                            ['pdfunite', addpath(docref3), addpath(docref2), addpath(docref)])

                odata1.Location = docref
                odata1.Detention = cache2
                db.session.commit()

            elif oder > 0 and pdata1 and docref3 and docref2:
                err = ['Sign the package', ' ', ' ', ' ',  ' ']
                stamp = 1
                invooder = oder
                leftscreen = 0
                leftsize = 8
                modlink = 0
                cache2 = int(odata1.Detention)
                cache2 = cache2+1
                # sandiwich it all together
                docref = f'tmp/{scac}/data/vorders/P_c'+'_' + odata1.Order + '.pdf'
                if 1 == 1:  # try:
                    tes = subprocess.check_output(
                        ['pdfunite', addpath(docref3), addpath(docref2), addpath(docref)])
                if 1 == 2:  # except:
                    odata1.Original = 'temp.pdf'
                    docref = f'tmp/{scac}/data/vorders/P_c'+'_' + 'temp.pdf'
                    tes = subprocess.check_output(
                        ['pdfunite', addpath(docref3), addpath(docref2), addpath(docref)])

                odata1.Location = docref
                odata1.Detention = cache2
                db.session.commit()

        if stampnow is not None:
            # if stampnow is called the document will already be recreated as a blank for here
            # and the information includes odat, pdat, idata
            err = ['Review Signed Package', ' ', ' ', ' ',  ' ']
            stamp = 1
            leftscreen = 0
            leftsize = 8
            modlink = 0
            cache2 = int(odat.Detention)
            #docin already set in previous area
            docref = f'tmp/{scac}/data/vorders/P_s' + str(cache2) + '_' + odat.Original
            odat.Location = docref
            db.session.commit()
            #stampdata already set in previous area
            from sigdoc import sigdoc
            sigdoc(stampdata, docin, docref)
            cache2 = cache2+1
            odat.Detention = str(cache2)
            db.session.commit()
            # Already have email data from previous area
            invo = 3


# ____________________________________________________________________________________________________________________E.Package.Trucking
# ____________________________________________________________________________________________________________________B.Package2.Trucking

        if mpack is not None and numchecked > 1:
            err = ['Combining Documents for Summary Invoice', ' ', ' ', ' ',  ' ']
            odervec = numcheckv(odata)
            keydata = [0]*len(odervec)
            grandtotal = 0
            for j, i in enumerate(odervec):
                odat = Orders.query.get(i)
                if j == 0:
                    pdata1 = People.query.filter(People.id == odat.Bid).first()
                    date1 = odat.Date
                    order = odat.Order
                date2 = odat.Date2
                idat = Invoices.query.filter(Invoices.Jo == odat.Jo).order_by(
                    Invoices.Ea.desc()).first()
                keydata[j] = [odat.Jo, odat.Booking, odat.Container, idat.Total, idat.Description]
                grandtotal = grandtotal+float(idat.Total)
                # put together the file paperwork
            print('scac', scac)
            file1 = f'tmp/{scac}/data/vinvoice/P_' + 'test.pdf'
            print('file1here=',file1)
            cache2 = int(odat.Detention)
            cache2 = cache2+1
            docref = f'tmp/{scac}/data/vinvoice/P_c{cache2}_{order}.pdf'

            for j, i in enumerate(odervec):
                odat = Orders.query.get(i)
                odat.Location = docref
                db.session.commit()

            import make_TP_invoice
            make_TP_invoice.main(file1, keydata, grandtotal, pdata1, date1, date2)

            invooder = oder
            leftscreen = 0
            leftsize = 8
            modlink = 0
            invo = 3

            filegather = ['pdfunite', addpath(file1)]
            cdata = companydata()
            etitle = cdata[2]+' Invoices:'
            #Prepare for email, but at this point only created invoice
            for i in odervec:
                odat = Orders.query.get(i)
                etitle = etitle+' '+odat.Jo
                filegather.append(addpath(odat.Path))
                odat.Istat = 1
                db.session.commit()

            filegather.append(addpath(docref))
            tes = subprocess.check_output(filegather)

            odat.Detention = cache2
            db.session.commit()
            emaildata = etemplate_truck2('invoice',2,odat.Bid,jo,order)
            invo = 3
# ____________________________________________________________________________________________________________________E.Package2.Trucking
# ____________________________________________________________________________________________________________________B.Email.Trucking
        # With loginvo we are recording invoice in ledger, but manually taking the invoice to customer
        if loginvo is not None:
            odat = Orders.query.get(invooder)
            alink = odat.Links
            if alink is not None:
                alist = json.loads(alink)
                print(alist)
                for aoder in alist:
                    thisodat = Orders.query.get(aoder)
                    jo = thisodat.Jo
                    gledger_write('invoice', jo, 0, 0)
                    thisodat.Istat = 2
                    db.session.commit()
                modlink = 0
                invo = 0
                invooder = 0
                stamp = 0
                inco = 0
                oder = 0
                mm1 = 0
            else:
                jo = odat.Jo
                gledger_write('invoice',jo,0,0)
                odat.Istat = 2
                db.session.commit()
                modlink = 0
                invo = 0
                invooder = 0
                stamp = 0
                inco = 0
                oder = 0
                mm1 = 0

        # This area for receiving money--cannot mass receive funds off the list
        if logrec is not None:
            odat = Orders.query.get(invooder)
            jo = odat.Jo
            inc = Income.query.filter(Income.Jo==jo).first()
            acctdb = inc.SubJo
            gledger_write('income',jo,acctdb,0)
            odat.Istat = 4
            db.session.commit()
            modlink = 0
            invo = 0
            invooder = 0
            stamp = 0
            inco = 0
            oder = 0
            mm1 = 0

        if emailnow is not None or emailinvo is not None:
            stamp = 1
            leftscreen = 1
            leftsize = 10
            modlink = 0
            odat = Orders.query.get(invooder)
            if emailnow is not None or invo > 1:
                docref = odat.Location
            else:
                docref = odat.Path
            jo = odat.Jo
            order = odat.Order
            alink = odat.Links
            if alink is not None:
                alist = json.loads(alink)
                for aoder in alist:
                    thisodat = Orders.query.get(aoder)
                    thisodat.Istat = 3
                    db.session.commit()
            else:
                odat.Istat = 3
                db.session.commit()
            emailin1 = invoice_mimemail(jo, order, docref, invo)
            gledger_write('invoice',jo,0,0)
            invo = 0
            invooder = 0
            stamp = 0
            err[0] = 'Successful email to: '
            err[1] = emailin1

# ____________________________________________________________________________________________________________________E.Email.Trucking
# ____________________________________________________________________________________________________________________B.Views.Trucking

        if viewo is not None and numchecked == 1:
            err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder > 0:
                modata = Orders.query.get(oder)
                if modata.Original is not None:
                    dot = modata.Original
                    if 'sig' in dot:
                        dot = dot.replace('_sig', '')
                        modata.Original = dot
                        db.session.commit()
                    docref = f'tmp/{scac}/data/vorders/' + dot
            if poof > 0:
                modata = Proofs.query.get(poof)
                if modata.Original is not None:
                    docref = f'tmp/{scac}/data/vproofs/' + modata.Original
            if tick > 0:
                modata = Interchange.query.get(tick)
                if modata.Original is not None:
                    docref = f'tmp/{scac}/data/vinterchange/' + modata.Original
            if (oder > 0 or poof > 0 or tick > 0) and modata.Original is not None:
                if len(modata.Original) > 5:
                    leftscreen = 0
                    leftsize = 10
                    modlink = 0
                    err = [' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if (viewo is not None or viewi is not None or viewp is not None) and numchecked != 1:
            err = ['Must check exactly one box to use this option', ' ', ' ', ' ',  ' ']

        if viewi is not None and numchecked == 1:
            err = ['There is no document available for this selection']
            if oder > 0:
                modata = Orders.query.get(oder)
                try:
                    docref = modata.Path
                    # Need to check for number of pages as this will tell us if is is a package or an individual invoice
                    npages = PdfFileReader(open(modata.Path, "rb")).getNumPages()
                    if npages >= 3:
                        invo = 3
                    else:
                        invo = npages
                    print('This file has', npages)
                    jo = modata.Jo
                    order = modata.Order
                    emaildata = etemplate_truck('invoice',3,modata.Bid,jo,order)
                    # idat=Invoices.query.filter(Invoices.Jo==modata.Jo).first()
                    # if idat is not None:
                    #    docref=idat.Original
                    leftscreen = 0
                    leftsize = 8
                    modlink = 0
                    invo = 1
                    invooder = oder
                    err = [' ', ' ', 'Viewing document '+docref, ' ',  ' ']
                except:
                    err = ['No Document Found']

        if viewp is not None and numchecked == 1:
            err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder > 0:
                modata = Orders.query.get(oder)
                pfile = modata.Location
                if 'vorders' in pfile or 'vinvoice' in pfile:
                    docref = modata.Location
                    leftscreen = 0
                    leftsize = 6
                    modlink = 0
                    stamp = 1
                    invooder = oder
                    jo = modata.Jo
                    order = modata.Order
                    stampdata = [3, 35, 35, 5, 120, 100, 5, 477, 350]
                    emaildata = etemplate_truck('invoice',4,modata.Bid,jo,order)
                    invo = 3
                    err = [' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if payview is not None:
            if numchecked == 1 and oder > 0:
                leftscreen = 0
                leftsize = 8
                modlink = 0
                invo = 1
                modata = Orders.query.get(oder)
                idat = Income.query.filter(Income.Jo == modata.Jo).first()
                if idat is not None:
                    docref = idat.Original
                    err = ['Current Payment Invoice']
                    if docref is None:
                        docref = modata.Original
                        err = ['No Payment Invoice Yet']
            else:
                err = ['Must check one Job']


# ____________________________________________________________________________________________________________________E.Views.Trucking
# ____________________________________________________________________________________________________________________B.Modify.Trucking
        if (modify is not None or vmod is not None) and numchecked == 1:
            modlink = 1
            leftsize = 8

            if oder > 0:

                fdata = myoslist(job_path)
                fdata.sort()

                modata = Orders.query.get(oder)
                csize = People.query.filter(
                    People.Ptype == 'Trucking').order_by(People.Company).all()
                docref = ' '
                if vmod is not None:
                    err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vorders/' + modata.Original
                            doctxt = docref.split('.', 1)[0]+'.txt'
                            err = ['All is well', ' ', ' ', ' ',  ' ']
                            fdata.append(modata.Original)

            if poof > 0:
                modata = Proofs.query.get(poof)
                if vmod is not None:
                    err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = modata.Original
                            err = ['All is well', ' ', ' ', ' ',  ' ']
            if tick > 0:
                modata = Interchange.query.get(tick)
                if vmod is not None:
                    err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vinterchange/' + modata.Original
                            err = ['All is well', ' ', ' ', ' ',  ' ']

            if serv > 0:
                modata = Services.query.get(serv)
                if vmod is not None:
                    err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']

            if peep > 0:
                modata = People.query.get(peep)
                if vmod is not None:
                    err = [' ', ' ', 'There is no document available for this selection', ' ',  ' ']

        if (modify is not None or vmod is not None) and numchecked > 1:
            modlink = 0
            # Check to see if these are all new jobs ready to be updated to ready status
            odervec = numcheckv(odata)
            for i in odervec:
                odat = Orders.query.get(i)
                hstat = odat.Hstat
                if hstat < 0:
                    odat.Hstat = 0
                    db.session.commit()
                err[0] = 'Automated inputs accepted'

        if (modify is not None or vmod is not None) and numchecked == 0:
            modlink = 0
            err[0] = ' '
            err[2] = 'Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.Modify.Trucking
# ____________________________________________________________________________________________________________________B.AddItems.Trucking
        if addS is not None and serv > 0 and numchecked == 1:
            leftsize = 8
            modlink = 2
            modata = Services.query.get(serv)

        if addS is not None and numchecked == 0:
            leftsize = 8
            modlink = 1
            # We will create a blank line and simply modify that by updating:
            input = Services(Service='New', Price=0.00)
            db.session.add(input)
            db.session.commit()
            modata = Services.query.filter(Services.Service == 'New').first()
            serv = modata.id
            err = [' ', ' ', 'Enter Data for New Service', ' ',  ' ']

        if addS is not None and numchecked > 1:
            modlink = 0
            err[0] = ' '
            err[2] = 'Must check exactly one box to use this option'

        if addE is not None and serv > 0 and numchecked == 1:
            leftsize = 8
            modlink = 3
            modata = Services.query.get(peep)

        if addP is not None:
            leftscreen = 0
            leftsize = 8
            modlink = 21
            # We will create a blank line and simply modify that by updating:
            input = Proofs(Status='Unmatched', Original='', Path='', Company='', Location='', Booking='', Order='', BOL='NewBOL',
                           Container='', Driver='', Date=today_dt, Time=now)
            db.session.add(input)
            db.session.commit()
            fdata = myoslist(pod_path)
            fdata.sort()
            if len(fdata) > 0:
                docref = f'tmp/{scac}/processing/pods/{fdata[0]}'
                doctxt = txtfile(docref)
            else:
                docref = f'tmp/{scac}/data/vunknown/NewJob.pdf'
                doctxt = ''
            modata = Proofs.query.filter(Proofs.BOL == 'NewBOL').first()
            poof = modata.id
            err = [' ', ' ', 'Enter Data for New Proof', ' ',  ' ']

        if addE is not None and numchecked == 0:
            leftsize = 8
            modlink = 1
            # We will create a blank line and simply modify that by updating:
            input = People(Company='New', First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None, Idtype=None, Idnumber=None, Telephone=None,
                           Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='Trucking', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter((People.Company == 'New') &
                                         (People.Ptype == 'Trucking')).first()
            peep = modata.id
            err = [' ', ' ', 'Enter Data for New Company', ' ',  ' ']

        if addE is not None and numchecked > 1:
            modlink = 0
            err[0] = ' '
            err[2] = 'Must check exactly one box to use this option'

        if addI is not None and numchecked == 0:
            leftscreen = 0
            leftsize = 8
            modlink = 20
            # We will create a blank line and simply modify that by updating:
            input = Interchange(CONTAINER='New', TRUCK_NUMBER='', DRIVER='', CHASSIS='', Date=None, RELEASE='', GROSS_WT='',
                                SEALS='', SCALE_WT='', CARGO_WT='', Time=None, Status='Unmatched', Original='', Path='', TYPE='Empty Out', Jo='', Company='')
            db.session.add(input)
            db.session.commit()
            fdata = myoslist(int_path)
            fdata.sort()
            if len(fdata) > 0:
                docref = int_path+fdata[0]
            else:
                docref = f'tmp/{scac}/data/vunknown/NewJob.pdf'
            modata = Interchange.query.filter(Interchange.CONTAINER == 'New').first()
            tick = modata.id
            err = [' ', ' ', 'Enter Data for New Interchange Ticket', ' ',  ' ']

        if slim is not None and (numchecked != 1 or oder == 0):
            modlink = 0
            err = [' ', ' ', 'Must select exactly one box from Shipping Data to use this option', ' ',  ' ']

        if slim is not None and numchecked == 1 and oder > 0:
            odata1 = Orders.query.get(oder)
            stayslim = odata1.id
            err = [' ', ' ', 'Showing SLIM data around JO='+odata1.Jo, ' ',  ' ']
            modlink = 0

# ____________________________________________________________________________________________________________________E.AddItems.Trucking
# ____________________________________________________________________________________________________________________B.Delete.Trucking
        if deletehit is not None and numchecked == 1:
            if oder > 0:
                odat = Orders.query.get(oder)
                jo = odat.Jo
                Gledger.query.filter(Gledger.Tcode==jo).delete()
                Orders.query.filter(Orders.id == oder).delete()
            if poof > 0:
                Proofs.query.filter(Proofs.id == poof).delete()
            if tick > 0:
                Interchange.query.filter(Interchange.id == tick).delete()
            if peep > 0:
                People.query.filter(People.id == peep).delete()
            if serv > 0:
                Services.query.filter(Services.id == serv).delete()

            db.session.commit()

        if deletehit is not None and numchecked != 1:
            err = [' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.Trucking


# ____________________________________________________________________________________________________________________B.ReceivePayment.Trucking

        if (recpay is not None and oder > 0 and numchecked == 1) or recupdate is not None:
            leftsize = 8
            if recpay is not None:
                invooder = oder
            odat = Orders.query.get(invooder)
            invojo = odat.Jo
            co = invojo[0]
            acdata = Accounts.query.filter((Accounts.Type=='Bank') & (Accounts.Co == co)).all()
            bklist = ['Cash', 'Mcheck', 'Mremit']
            for adat in acdata:
                bklist.append(adat.Name)

            if recpay is not None:
                lastpr = request.values.get('lastpr')
                if lastpr is not None and lastpr != 0 and lastpr != '0':
                    ltext=lastpr.splitlines()
                    custref= ltext[0]
                    acctdb = ltext[1]
                else:
                    custref = 'ChkNo'
                    acctdb = request.values.get('acctto')



            ldat = Invoices.query.filter(Invoices.Jo == invojo).first()
            err = ['Have no Invoice to Receive Against', ' ', ' ', ' ', ' ']
            if ldat is not None:
                invodate = ldat.Date
                invoamt = ldat.Total
                if ldat.Original is not None:
                    docref = ldat.Original
                    leftscreen = 0
                    leftsize = 8

                incdat = Income.query.filter(Income.Jo == invojo).first()
                if incdat is None:
                    print('incdat is none"')
                    err = ['Creating New Payment on Jo', ' ', ' ', ' ', ' ']
                    paydesc = 'Receive payment on Invoice ' + invojo
                    recamount = ldat.Total

                    recdate = datetime.date.today()

                    print('acctdb=',acctdb)
                    input = Income(Jo=odat.Jo, SubJo=acctdb, Pid=odat.Bid, Description=paydesc,
                                   Amount=recamount, Ref=custref, Date=recdate, Original=docref)
                    db.session.add(input)
                    db.session.commit()

                else:
                    print('incdat is not none')
                    recamount = request.values.get('recamount')
                    custref = request.values.get('custref')
                    desc = request.values.get('desc')
                    recdate = request.values.get('recdate')
                    acctdb = request.values.get('acctto')
                    if acctdb is None:
                        acctdb = 'Cash'
                    if custref is None:
                        custref = 'ChkNo'
                    print('acctdb2=',acctdb)
                    if isinstance(invodate, str):
                        recdate = datetime.datetime.strptime(recdate, '%Y-%m-%d')
                    incdat.Amount = recamount
                    incdat.Ref = custref
                    incdat.Description = desc
                    incdat.Date = recdate
                    incdat.Original = docref
                    incdat.SubJo = acctdb
                    db.session.commit()

                #print('1332',err,custref,acctdb)
                try:
                    lastpr = custref + '\n' + acctdb
                except:
                    print('Could not create lastpr')
                incdat = Income.query.filter(Income.Jo == invojo).first()

                payment = [recamount, custref, recdate, acctdb]
                print('payment = ', payment)

                modata = Income.query.filter(Income.Jo == invojo).first()
                inco = modata.id
                err = [' ', ' ', 'Amend Payment for Invoice '+invojo, ' ',  ' ']

                ldata = Invoices.query.filter(
                    Invoices.Jo == invojo).order_by(Invoices.Ea.desc()).all()
                cache = odat.Storage+1
                pdata1 = People.query.filter(People.id == odat.Bid).first()
                pdata2 = Drops.query.filter(Drops.id == odat.Lid).first()
                pdata3 = Drops.query.filter(Drops.id == odat.Did).first()

                if recupdate is not None:
                    try:
                        rec = float(recamount)
                    except:
                        rec = 0.00
                    try:
                        owe = float(ldat.Total)
                    except:
                        owe = 0.00
                    if rec < owe:
                        # Need to determine what has been paid for and what has not
                        howapp = 1
                    else:
                        for data in ldata:
                            data.Status = 'P'

                    gledger_write('income',invojo,acctdb,0)

                from make_T_invoice import T_invoice
                T_invoice(odat, ldata, pdata1, pdata2, pdata3, cache, invodate, payment)

                if cache > 1:
                    docref = f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                    # Store for future use
                else:
                    docref = f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'

                odat.Storage = cache
                idat = Invoices.query.filter(Invoices.Jo == invojo).first()
                incdat.Original = docref
                hstat = odat.Hstat
                if hstat == 2 or hstat == 3:
                    odat.Hstat = 4
                myp = Proofs.query.filter(Proofs.Order == odat.Order).first()
                if myp is not None:
                    myp.Status = 'Paid'
                db.session.commit()
                leftscreen = 0
                err[4] = 'Viewing '+docref

        if recpay is not None and (oder == 0 or numchecked != 1):
            err = ['Invalid selections:', '', '', '', '']
            if oder == 0:
                err[1] = 'Must select a Trucking Job'
            if numchecked != 1:
                err[2] = 'Must select exactly one Trucking Job'
# ____________________________________________________________________________________________________________________E.Receive Payment.Trucking
# ____________________________________________________________________________________________________________________B.Payment History.Trucking
        if hispay is not None or modlink == 7:
            if oder == 0 and invooder == 0:
                err[1] = 'Must select a Trucking Job'
            else:
                if oder != 0:
                    invooder = oder
                modata = Storage.query.get(invooder)
                ldata = Invoices.query.filter(Invoices.Jo == modata.Jo).order_by(Invoices.Jo).all()
                fdata = Income.query.filter(Income.Jo == modata.Jo).order_by(Income.Jo).all()
                # Check to see if we need to delete anything from history
                killthis = request.values.get('killthis')
                if killthis is not None and modlink == 7:
                    for data in ldata:
                        testone = request.values.get('bill'+str(data.id))
                        if testone:
                            kill = int(testone)
                            Invoices.query.filter(Invoices.id == kill).delete()
                            db.session.commit()
                    for data in fdata:
                        testone = request.values.get('pay'+str(data.id))
                        if testone:
                            kill = int(testone)
                            Income.query.filter(Income.id == kill).delete()
                            db.session.commit()
                    ldata = Invoices.query.filter(
                        Invoices.Jo == modata.Jo).order_by(Invoices.Jo).all()
                    fdata = Income.query.filter(Income.Jo == modata.Jo).order_by(Income.Jo).all()

                leftsize = 8
                modlink = 7
# ____________________________________________________________________________________________________________________E.PaymentHistory.Trucking

# ____________________________________________________________________________________________________________________B.Invoice.Trucking and Quotes
        if (minvo is not None and oder > 0) and numchecked > 1:
            err = ['Could not create multi-job invoice', ' ']
            odata = Orders.query.all()
            odervec = numcheckv(odata)
            invooder = odervec[0]

            thesematch = 1
            for j, oder in enumerate(odervec):
                myo = Orders.query.get(oder)
                if j == 0:
                    shipco = myo.Shipper
                else:
                    shipper = myo.Shipper
                    if shipco != shipper:
                        thesematch = 0

            if thesematch == 1:
                print('Selections Matched')

                if 'Global' in shipco:
                    print('Selections are Global')
                    docref = multi_inv(odata, odervec, 1)
                else:
                    print('Multi-Invoice Requested')
                    docref = multi_inv(odata, odervec, 1)
            else:
                err[1] = 'Shippers Not Matched'

            if thesematch == 1:
                leftscreen = 0
                invo = 2
                leftsize = 8
                err = [f'Multi-Invoice:{json.dumps(odervec)}', 'Viewing '+docref]
                emaildata = etemplate_truck('invoice',5,myo.Bid,myo.Jo,myo.Order)
                invo = 2

        if ((minvo is not None and oder > 0 and numchecked == 1) or invoupdate is not None) or ((mquot is not None and oder > 0 and numchecked ==1 ) or quotupdate is not None):

            err = ['Cannot make invoice:', 'Billing ok', 'Load ok', 'Delivery ok']
            # First time through: have an order to invoice
            if oder > 0:
                invooder = oder
            myo = Orders.query.get(invooder)

            shipper = myo.Shipper
            jo = myo.Jo
            ldat = Invoices.query.filter(Invoices.Jo == jo).first()

            # Check to see if we have the required data to make an invoice or quote:
            bid = myo.Bid
            lid = myo.Lid
            did = myo.Did
            con = myo.Container
            print(bid, lid, did)
            if bid is None or bid == 0:
                err[1] = 'No Billing Data'
            if lid is None or lid == 0:
                expimp = getexpimp(con)
                if expimp == 'Export':
                    lid = dropupdate2(bid)
                if expimp == 'Import':
                    lid = dropupdate3('BAL')
                if lid is None or lid == 0:
                    myo.Company = 'NAY'
                else:
                    ddat = Drops.query.get(lid)
                    myo.Lid = lid
                    myo.Company = ddat.Entity
                db.session.commit()
                myo = Orders.query.get(invooder)

            if did is None or did == 0:
                expimp = getexpimp(con)
                if expimp == 'Export':
                    did = dropupdate3('BAL')
                if expimp == 'Import':
                    did = dropupdate2(bid)

                if did is None or did == 0:
                    myo.Company2 = 'NAY'
                else:
                    ddat = Drops.query.get(did)
                    myo.Did = did
                    myo.Company2 = ddat.Entity
                db.session.commit()
                myo = Orders.query.get(invooder)


            if bid or mquot is not None or quot > 0:
                err[0] = 'Have needed items to make invoice'
                invo = 1
                leftsize = 8
                cache = myo.Storage+1

                # These are the services we wish to add to the invoice
                sdata = Services.query.order_by(Services.Price.desc()).all()
                for data in sdata:
                    testone = request.values.get('serv'+str(data.id))
                    if testone:
                        servid = int(testone)
                        mys = Services.query.get(servid)
                        qty = 1
                        descript = ' '
                        if mys.Service == 'Line Haul':
                            try:
                                descript = 'Order ' + myo.Order + ' Line Haul ' + myo.Company + ' to ' + myo.Company2
                            except:
                                descript = 'Order, Load Comp, or Delv Comp Missing'
                        elif mys.Service == 'Detention':
                            descript = 'Actual Time of Load = '+str(2+qty) + ' Hours'
                        elif mys.Service == 'Storage':
                            descript = 'Days of Storage'
                        elif mys.Service == 'Chassis Fees':
                            descript = 'Days of Chassis'
                        amount = float(mys.Price)
                        input = Invoices(Jo=myo.Jo, SubJo=None, Pid=0, Service=mys.Service, Description=descript, Ea=d2s(
                            amount), Qty=qty, Amount=d2s(amount), Total=0.00, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()

                idat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
                if idat is None:
                    c1 = myo.Company
                    if c1 is None:
                        c1 = 'None Defined'
                    c1 = c1.strip()
                    c2 = myo.Company2
                    if c2 is None:
                        c2 = 'None Defined'
                    c2 = c2.strip()
                    descript = 'From ' + c1 + ' to ' + c2
                    amount = myo.Amount
                    try:
                        amount = d2s(myo.Amount)
                        amount = float(amount)
                    except:
                        amount = 0.00
                    input = Invoices(Jo=myo.Jo, SubJo=None, Pid=0, Service='Line Haul', Description=descript,
                                     Ea=amount, Qty=1, Amount=amount, Total=amount, Date=today, Original=None, Status='New')
                    db.session.add(input)
                    db.session.commit()

                # Now we have an invoice, and may have added parts so we need to update the totals for all the components of the invoice:
                #updateinvo(myo.Jo, myo.Date)

                total = 0.0
                idata = Invoices.query.filter(Invoices.Jo == jo).all()
                for idat in idata:
                    qty = float(idat.Qty)
                    each = float(idat.Ea)
                    amt = qty*each
                    total = total+amt
                for idat in idata:
                    idat.Total = d2s(total)
                    db.session.commit()

                ldat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
                if ldat is None:
                    invo = 0
                    leftsize = 10
                    err = [' ', ' ', 'No services on invoice yet and none selected', ' ',  ' ']
                else:
                    invo = 1
                    leftsize = 8
                    invodate = ldat.Date
                    err = [' ', ' ', 'Created invoice for JO= '+myo.Jo, ' ',  ' ']
                    ldata = Invoices.query.filter(
                        Invoices.Jo == myo.Jo).order_by(Invoices.Ea.desc()).all()
                    pdata1 = People.query.filter(People.id == myo.Bid).first()
                    pdata2 = Drops.query.filter(Drops.id == myo.Lid).first()
                    pdata3 = Drops.query.filter(Drops.id == myo.Did).first()

                    if (minvo is not None and oder > 0 and numchecked == 1) or invoupdate is not None:

                        from make_T_invoice import T_invoice
                        T_invoice(myo, ldata, pdata1, pdata2, pdata3, cache, invodate, 0)

                        if cache > 1:
                            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
                            # Store for future use
                        else:
                            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'.pdf'

                    else:

                        from make_T_quote import T_quote
                        docref = T_quote(myo, ldata, pdata1, pdata2, pdata3, cache, invodate)

                        if cache > 1:
                            docref = f'tmp/{scac}/data/vquote/Quote_' + myo.Jo + 'c' + str(cache) + '.pdf'
                            # Store for future use
                        else:
                            docref = f'tmp/{scac}/data/vquote/Quote_' + myo.Jo + '.pdf'

                        quot = 1
                        invo = 0



                    for ldatl in ldata:
                        ldatl.Pid = pdata1.id
                        ldatl.Original = docref
                        db.session.commit()

                    myo.Path = docref
                    myo.Storage = cache
                    myo.Amount = d2s(total)
                    db.session.commit()

                    leftscreen = 0
                    err[0] = 'Viewing '+docref
                    modata = Orders.query.get(invooder)
                    idata = Invoices.query.filter(Invoices.Jo == jo).all()
                    ldat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
                    jo = modata.Jo
                    order = modata.Order
                if (minvo is not None and oder > 0 and numchecked == 1) or invoupdate is not None:
                    emaildata = etemplate_truck('invoice',6,modata.Bid,jo,order)
                else:
                    emaildata = etemplate_truck('quote',6,modata.Bid,jo,order)
                #invo = 1

# ____________________________________________________________________________________________________________________E.Invoice.Trucking
# ____________________________________________________________________________________________________________________B.Newjob.Trucking
        if newjob is not None:
            err = ['Select Source Document from List']
            fdata = myoslist(job_path)
            fdata.sort()
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            modlink = 4
            leftsize = 8
            leftscreen = 0
            if len(fdata) > 0:
                docref = job_path+fdata[0]
                doctxt = docref.split('.', 1)[0]+'.txt'
            else:
                docref = f'tmp/{scac}/data/vunknown/NewJob.pdf'

        if newjob is None and modlink == 4:
            filesel = request.values.get('FileSel')
            fdata = myoslist(job_path)
            fdata.sort()
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            leftsize = 8
            leftscreen = 0
            docref = f'tmp/{scac}/processing/tjobs/'+filesel
            doctxt = docref.split('.', 1)[0]+'.txt'
            shipper = request.values.get('shipper')
            pufrom = request.values.get('thislcomp')
            deltoc = request.values.get('thisdcomp')

            if shipper == '0':
                shipper = a[0]
            if pufrom == '0':
                pufrom = a[0]
            if deltoc == '0':
                deltoc = a[0]

            if shipper == '2' or pufrom == '2' or deltoc == '2':
                input = People(Company='New', First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None, Idtype=None, Idnumber=None, Telephone=None,
                               Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='Trucking', Temp1=None, Temp2=None, Accountid=None)
                db.session.add(input)
                db.session.commit()
                modata = People.query.filter((People.Company == 'New')
                                             & (People.Ptype == 'Trucking')).first()
                peep = modata.id
            if shipper == '2':
                shipper = 0
            if pufrom == '2':
                pufrom = 0
            if deltoc == '2':
                deltoc = 0
            holdvec = [shipper, pufrom, deltoc]

        if thisjob is not None:
            modlink = 0
            # Create the new database entry for the source document
            filesel = request.values.get('FileSel')
            docref, doctxt = doctransfer('tjobs', 'vorders', filesel)
            sdate = request.values.get('dstart')
            if sdate is None:
                sdate = today.strftime('%Y-%m-%d')

            jtype = 'T'
            nextjo = newjo(jtype, sdate)

            vals = ['shipper', 'load', 'order', 'bol', 'booking', 'container', 'pickup',
                    'dropblock1', 'ldate', 'ltime', 'dropblock2', 'ddate', 'dtime', 'thisamt', 'seal', 'ctype']
            a = list(range(len(vals)))
            i = 0
            for v in vals:
                a[i] = request.values.get(v)
                i = i+1
            bid = People.query.filter(People.Company == a[0]).first()
            if bid is not None:
                idb = bid.id
            else:
                idb = 0

            dropblock1 = a[7]
            dropblock2 = a[10]
            print('1618',dropblock1,dropblock2)
            idl = 0
            idd = 0

            if len(dropblock1.strip())<7:
                sfind = dropblock1.strip()
                sfind = sfind[0:2]
                print(sfind)
                sfind = sfind.lower()
                ddata = Drops.query.all()
                for ddat in ddata:
                    entity=ddat.Entity
                    scomp = entity[0:2]
                    scomp = scomp.lower()
                    if sfind == scomp:
                        idl = ddat.id
                        newdrop1 = ddat.Entity + '\n' + ddat.Addr1 + '\n' + ddat.Addr2 + '\n' + ddat.Phone + '\n' + ddat.Email
                        company = ddat.Entity
                        break

            if len(dropblock2.strip())<7:
                sfind = dropblock2.strip()
                sfind = sfind[0:2]
                sfind = sfind.lower()
                ddata = Drops.query.all()
                for ddat in ddata:
                    entity=ddat.Entity
                    scomp = entity[0:2]
                    scomp = scomp.lower()
                    if sfind == scomp:
                        idd = ddat.id
                        newdrop2 = ddat.Entity + '\n' + ddat.Addr1 + '\n' + ddat.Addr2 + '\n' + ddat.Phone + '\n' + ddat.Email
                        company2 = ddat.Entity
                        break

            if idl == 0:
                company = dropupdate(dropblock1)
                newdrop1 = a[7]
                lid = Drops.query.filter(Drops.Entity == company).first()
                if lid is not None:
                    idl = lid.id
                else:
                    idl = 0

            if idd == 0:
                company2 = dropupdate(dropblock2)
                newdrop2 = a[10]
                did = Drops.query.filter(Drops.Entity == company2).first()
                if did is not None:
                    idd = did.id
                else:
                    idd = 0

            if a[13] is None:
                a[13] = '0.00'
            label = nextjo+' '+a[2]+' '+a[0]+' '+a[13]
            input = Orders(Status='00', Jo=nextjo, Load=a[1], Order=a[2], Company=company, Location=None, Booking=a[4], BOL=a[3], Container=a[5],
                           Date=a[8], Driver=None, Company2=company2, Time=a[9], Date2=a[11], Time2=a[12], Seal=a[14], Pickup=a[6], Delivery=None,
                           Amount=a[13], Path=None, Original=filesel, Description=None, Chassis=None, Detention='0', Storage='0',
                           Release=0, Shipper=a[0], Type=a[15], Time3=None, Bid=idb, Lid=idl, Did=idd, Label=label, Dropblock1=newdrop1, Dropblock2=newdrop2, Commodity=None, Packing=None, Links=None)
            db.session.add(input)
            db.session.commit()
            modata = Orders.query.filter(Orders.Jo == nextjo).first()
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            oder = modata.id
            leftscreen = 1
            err = ['All is well', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Newjob.Trucking
        if copy is not None:
            now = datetime.datetime.now().strftime('%I:%M %p')
            if oder > 0 and numchecked == 1:
                sdate = today.strftime('%Y-%m-%d')
                jtype = 'T'
                nextjo = newjo(jtype, sdate)
                myo = Orders.query.get(oder)
                load = myo.Company[0:1]+nextjo[-5:]
                order = myo.Company[0:1]+nextjo[-5:]
                original = myo.Original
                input = Orders(Status='A0', Jo=nextjo, Load=load, Order=order, Company=myo.Company, Location=None, Booking=myo.Booking, BOL=myo.BOL,
                               Container='TBD', Date=today, Driver=None, Company2=myo.Company2, Time=now, Date2=today, Time2=now,
                               Seal=myo.Seal, Pickup=myo.Pickup, Delivery=None, Amount=myo.Amount, Path=None, Original=original,
                               Description=myo.Description, Chassis=myo.Chassis, Detention='0', Storage='0', Release=0, Shipper=myo.Shipper,
                               Type=myo.Type, Time3=None, Bid=myo.Bid, Lid=myo.Lid, Did=myo.Did, Label=myo.Label, Dropblock1=myo.Dropblock1,
                               Dropblock2=myo.Dropblock2, Commodity=myo.Commodity,Packing=myo.Packing, Links=myo.Links)
                db.session.add(input)
                db.session.commit()

            if poof > 0 and numchecked == 1:
                myp = Proofs.query.get(poof)
                input = Proofs(Status='Unmatched', Original='', Path='',
                               Company=myp.Company, Location=myp.Location, Booking=myp.Booking,
                               Order=myp.Order, BOL=myp.BOL, Container=myp.Container, Driver=myp.Driver,
                               Date=today, Time=now)
                db.session.add(input)
                db.session.commit()

            if peep > 0 and numchecked == 1:
                myp = People.query.get(peep)
                input = People(Company='', First=myp.First, Middle=myp.Middle, Last=myp.Last, Addr1=myp.Addr1, Addr2=myp.Addr2, Addr3=myp.Addr3,
                               Idtype=myp.Idtype, Idnumber=myp.Idnumber, Telephone=myp.Telephone, Email=myp.Email, Associate1=myp.Associate1,
                               Associate2=myp.Associated2, Date1=today, Ptype='Overseas', Date2=None, Original=None, Temp1=None, Temp2=None, Accountid=None)
                db.session.add(input)
                db.session.commit()

            if tick > 0 and numchecked == 1:
                myi = Interchange.query.get(tick)
                type = myi.TYPE
                if type == 'Load In':
                    newtype = 'Empty Out'
                if type == 'Empty Out':
                    newtype = 'Load In'
                if type == 'Empty In':
                    newtype = 'Load Out'
                if type == 'Load Out':
                    newtype = 'Empty In'

                input = Interchange(CONTAINER=myi.CONTAINER, TRUCK_NUMBER=myi.TRUCK_NUMBER, DRIVER=myi.DRIVER, CHASSIS=myi.CHASSIS,
                                    Date=myi.Date, RELEASE=myi.RELEASE, GROSS_WT=myi.GROSS_WT,
                                    SEALS=myi.SEALS, CONTYPE=myi.CONTYPE, CARGO_WT=myi.CARGO_WT,
                                    Time=myi.Time, Status='AAAAAA', Original=' ', Path=' ', TYPE=newtype, Jo=myi.Jo, Company=myi.Company)
                db.session.add(input)
                db.session.commit()

            if numchecked > 1:
                err[1] = 'Must select exactly one box to choose this option.'
                err[0] = ' '

# ____________________________________________________________________________________________________________________B.ManualUpdate.Trucking

        if loadc is not None:
            err[0] = 'Must check at least one box'
            err[1] = ''
            if oder > 0:
                err[0] = 'Load Completion Status Updated'
                myo = Orders.query.get(oder)
                hstat = myo.Hstat
                if hstat == 0 or hstat == 1:
                    myo.Hstat = 3
                    db.session.commit()
                else:
                    err[0] = 'Load already has a complete status'

        if acceptthese is not None:
            err[0] = 'Must check at least one box'
            err[1] = ''
            print('Accepting....',oder,tick)
            if oder > 0:
                modlink = 0
                # Check to see if these are all new jobs ready to be updated to ready status
                odervec = numcheckv(odata)
                agree = 1
                for i in odervec:
                    odat = Orders.query.get(i)
                    if odat.Hstat == -1:
                        odat.Hstat = 0
                        db.session.commit()
                        Order_Container_Update(i)
                else:
                    err[0] = 'All status must contain A'
                    err[2] = 'Must check exactly one box to use this option'

            if tick > 0:
                err[0] = 'Load Completion Status Updated'
                tickvec = numcheckvec(idata, 'tick')
                for tick in tickvec:
                    myi = Interchange.query.get(tick)
                    status = myi.Status
                    bit1 = status[0]
                    if bit1 == 'A':
                        myi.Status = 'BBBBBB'
                    db.session.commit()
                    InterStrip(tick)
                    InterMatchThis(tick)
                    InterDupThis(tick)
                    PushJobsThis(tick)


# ____________________________________________________________________________________________________________________E.ManualUpdate.Trucking


# ____________________________________________________________________________________________________________________B.Matching.Trucking
        if match is not None:

            if numchecked == 0:
                Matched_Now()

            if oder > 0 and poof > 0 and numchecked == 2:
                myo = Orders.query.get(oder)
                myp = Proofs.query.get(poof)
                myp.Order = myo.Order
                myp.Driver = myo.Driver
                myp.Container = myo.Container
                myp.Booking = myo.Booking
                myp.Date = myo.Date
                myp.Time = myo.Time
                myo.BOL = myp.BOL
                if myo.Status == '00':
                    myo.Status = '10'
                myp.Status = 'Matched'
                db.session.commit()

            if oder > 0 and tick > 0 and numchecked == 2:
                myo = Orders.query.get(oder)
                myi = Interchange.query.get(tick)
                myo.Container = myi.CONTAINER
                db.session.commit()

            if tick > 0 and numchecked == 1:
                myi = Interchange.query.get(tick)
                type = myi.TYPE
                if type == 'Load In':
                    newtype = 'Empty Out'
                if type == 'Empty Out':
                    newtype = 'Load In'

                input = Interchange(CONTAINER=myi.CONTAINER, TRUCK_NUMBER=myi.TRUCK_NUMBER, DRIVER=myi.DRIVER, CHASSIS=myi.CHASSIS,
                                    Date=myi.Date, RELEASE=myi.RELEASE, GROSS_WT=myi.GROSS_WT,
                                    SEALS=myi.SEALS, SCALE_WT=myi.SCALE_WT, CARGO_WT=myi.CARGO_WT,
                                    Time=myi.Time, Status='AAAAAA', Original=' ', Path=' ', TYPE=newtype, Jo=None, Company=None)
                db.session.add(input)
                db.session.commit()

            if numchecked != 2:
                err[1] = 'Must select exactly 2 boxes to use this option.'
                err[0] = ' '
# ____________________________________________________________________________________________________________________E.Matching.Trucking
# ____________________________________________________________________________________________________________________B.Calendar.Trucking
        if calendar is not None or calupdate is not None:
            leftscreen = 2
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

            caldays, daylist, weeksum = calendar7_weeks('Trucking', nweeks)

            if calupdate is not None:
                err = calmodalupdate(daylist, username, 'Trucking')
                caldays, daylist, weeksum = calendar7_weeks('Trucking', nweeks)

# ____________________________________________________________________________________________________________________E.Calendar.Trucking
    # This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        doctxt = ''
        filesel = ''
        docref = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        stampdata = ''
        mm1 = 0
        tdata=0
        drvdata=0
        bklist = 0
        lastpr = 0

        sdata = Services.query.order_by(Services.Price.desc()).all()
        cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
        ldata = None
        howapp = 0
        dlist = ['off']*4
        dlist[0] = 'on'
        newc = 'Not found'
        oder, poof, tick, serv, peep, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_truck_zero()
        leftscreen = 1
        holdvec = [0]*3
        quot = 0

        stampdata = [3, 35, 35, 5, 120, 100, 5, 477, 350]
        leftsize = 10
        err = ['All is well', ' ', ' ', ' ',  ' ']
        thismuch = '1'

    if modlink == 20:
        fdata = myoslist(int_path)
        fdata.sort()
    elif modlink == 21:
        fdata = myoslist(pod_path)
        fdata.sort()
    elif modlink == 4:
        fdata = myoslist(job_path)
        fdata.sort()

    odata, pdata, idata = dataget_T(thismuch, dlist)
    alltdata = Drivers.query.all()
    allvdata = Vehicles.query.all()
    leftsize=8
    rightsize = 12-leftsize
    sdata2 = Services.query.order_by(Services.Service).all()
    err = erud(err)

    return bklist, lastpr, thismuch, etitle, ebody, emaildata, odata, pdata, idata, sdata, cdata, oder, poof, sdata2, tick, serv, peep, err, modata, caldays, daylist, nweeks, howapp, modlink, leftscreen, docref, 0, leftsize, newc, tdata, drvdata, dlist, rightsize, ldata, invodate, inco, invo, quot, invooder, cache, stamp, alltdata, allvdata, stampdata, fdata, filesel, today, now, doctxt, holdvec, mm1
