from runmain import db
from models import DriverAssign, Gledger, Vehicles, Invoices, JO, Income, Orders, Accounts, LastMessage, People, Interchange, Drivers, ChalkBoard, Services, Drops
from flask import render_template, flash, redirect, url_for, session, logging, request
from CCC_system_setup import myoslist, addpath, tpath, companydata, scac
from InterchangeFuncs import Order_Container_Update, Match_Trucking_Now, Match_Ticket
from email_appl import etemplate_truck

import datetime
import os
import subprocess
from func_cal import calmodalupdate
import json

def isoT():

    from viewfuncs import erud, testdrop, make_new_order, driver_assignments, driver_payroll, container_list, get_invo_data, Orders_Form_Update, Orders_Drop_Update, loginvo_m
    from blend_pdf import blendticks

    if request.method == 'POST':
        # ____________________________________________________________________________________________________________________B.FormVariables.Trucking

        from viewfuncs import parseline, tabdata, tabdataR, popjo, jovec, newjo, timedata, nonone, nononef, init_truck_zero, dropupdate, dropupdate2, dropupdate3
        from viewfuncs import d2s, d2sa, stat_update, numcheck, numcheckv, sdiff, calendar7_weeks, viewbuttons, get_ints, containersout, numcheckvec
        from viewfuncs import txtfile, doctransfer, getexpimp, docuploader, dataget_T
        from InterchangeFuncs import InterStrip, InterMatchThis, InterDupThis, PushJobsThis
        from invoice_mimemail import invoice_mimemail
        from invoice_makers import multi_inv
        from gledger_write import gledger_write
        err=[]
        codata = companydata()
        jbcode = codata[10]+'T'

        # Zero and blank items for default
        username = session['username'].capitalize()
        pod_path, job_path, int_path = f'processing/pods/', f'processing/tjobs/', f'processing/interchange/'
        oder, poof, tick, serv, peep, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_truck_zero()
        filesel,docref,doctxt,etitle,ebody,emaildata,stampdata = '','','','','','',''
        drvdata, bklist, servid, howapp, viewm, viewg, viewip = 0, 0, 0, 0, 0, 0, 0
        lastpr = request.values.get('lastpr')

        today = datetime.date.today()
        today_dt = datetime.date.today()
        today_str = today_dt.strftime('%Y-%m-%d')
        now = datetime.datetime.now()
        now = now.time()
        newc = 'Not found at top'

        match, modify, vmod, minvo, mpack, viewo, viewi, viewp, printn, addE, addS, slim, stayslim, unslim, limitptype, returnhit, deletehit, update, invoupdate, emailnow, emailinvo, newjob, thisjob, recpay, hispay, recupdate, calendar, calupdate = viewbuttons()
        stampnow = request.values.get('stampnow')
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
        invoserv = request.values.get('invoserv')
        mm3 = nonone(request.values.get('passmanifest'))
        eprof = request.values.get('emlprofile')
        lbox = request.values.get('launchbox')
        lbox = nonone(lbox)
        passinvo = request.values.get('passinvo')
        passinvo = nonone(passinvo)
        print('passinvo=',passinvo)
        umi = request.values.get('UpdateMultiInvoice')
        umc = request.values.get('UpdateColumn')

        print('lbox=', lbox)
        viewtype = 0
        doclist = [0]*8
        holdvec = [0] * 20
        if dlist[1] == 'on':
            Services.query.filter((Services.Service == 'New') & (Services.Price == 0.00)).delete()

        oder, poof, tick, serv, peep, invo, invooder, cache, modlink = get_ints()
        quot = 0


        if invoserv is not None:
            invoupdate = '1'
            servid = nonone(invoserv)

        if umi is not None:
            #Redoing our multi-invoice with new values
            newbase = request.values.get('newbaseamount')
            newchas = request.values.get('newchasamount')
            newchas = d2s(newchas)
            newbase = d2s(newbase)
            holdvec[3] = newbase
            holdvec[4] = newchas
            minvo = 1
            oder = request.values.get('passoder')
            oder = nonone(oder)
            if oder == 0:
                oder = invooder
            print(oder,invooder)
            odat = Orders.query.get(oder)
            odervec = json.loads(odat.Links)
            print('UMI present',newbase,newchas,oder,odervec)

        if umc is not None:
            #Replacing text in columns
            colname = request.values.get('colname')
            coltext = request.values.get('coltext')
            holdvec[3] = colname
            holdvec[4] = coltext
            oder = request.values.get('passoder')
            oder = nonone(oder)
            if oder == 0:
                oder = invooder
            print(oder,invooder)
            odat = Orders.query.get(oder)
            odervec = json.loads(odat.Links)
            print('UMC present',colname,coltext,oder,odervec)
            for oder in odervec:
                od = Orders.query.get(oder)
                if colname == 'Chassis': od.Chassis = coltext
                if colname == 'Chassis': od.BOL = coltext
                if colname == 'Commodity': od.Commodity = coltext
                if colname == 'Packing': od.Packing = coltext
                db.session.commit()


        thisbox1 = request.values.get('addbox')
        if thisbox1 == '1':
            newjob = 1
        if thisbox1 == '2':
            addE = 1
        if thisbox1 == '3':
            addS = 1
        if thisbox1 == '4':
            copy = 1
        if thisbox1 == '5':
            mm2 = 1
            viewtype = 'manifest'
        if thisbox1 == '6':
            uploadS = 1
        if thisbox1 =='7':
            uploadP = 1

        thisbox2 = request.values.get('editbox')
        if thisbox2 == '1':
            vmod = 1
        if thisbox2 == '2':
            match = 1
        if thisbox2 == '3':
            acceptthese = 1
        if thisbox2 == '4':
            loadc = 1
        if thisbox2 == '5':
            viewtype = 'columnadd'

        thisbox3 = request.values.get('invobox')
        if thisbox3 == '1':
            minvo = 1
        if thisbox3 == '2':
            mquot = 1
        if thisbox3 == '3':
            mpack = 1
        if thisbox3 == '5':
            recpay = 1
        if thisbox3 == '4' or passinvo == 4:
            lbox = 0
            invo = 4
            invo, holdvec, err = get_invo_data(invo, holdvec)

        thisbox4 = request.values.get('viewbox')
        if thisbox4 == '1':
            viewo = 1
        if thisbox4 == '2':
            viewp = 1
        if thisbox4 == '3':
            viewm = 1
        if thisbox4 == '4':
            viewg = 1
        if thisbox4 == '5':
            viewi = 1
        if thisbox4 == '6':
            viewip = 1

        thisbox5 = request.values.get('xbox')
        if thisbox5 == '1':
            deletehit = 1
        if thisbox5 == '2':
            uninv = 1
        if thisbox5 == '3':
            unpay = 1

        thisbox6 = request.values.get('dispbox')
        if thisbox6 == '1':
            mm2 = 1
            #Signature date:
            holdvec[16] = today_str
        if thisbox6 == '2':
            lbox = 6
            lbox, holdvec, err = container_list(lbox, holdvec)
        if thisbox6 == '3':
            lbox = 1



        stamp = request.values.get('stamp')
        leftscreen = 1
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
            lbox=0
            eprof = None
            leftscreen = 1

        if lbox > 0:
            if lbox == 1:
                lbox,holdvec,err = driver_assignments(lbox,holdvec)
                print('h=',lbox,holdvec)
            if lbox == 2 and modlink==1:
                fdata = DriverAssign.query.filter(DriverAssign.Hours != None).all()
            if lbox == 3:
                lbox, holdvec, err = driver_payroll(lbox, holdvec)
            #if lbox == 6:
                #lbox, holdvec, err = container_list(lbox, holdvec)



        if modlink == 4 and (newjob is None and thisjob is None and update is None):
            upnow = request.values.get('uploadnow')
            if upnow is not None:
                err, oid = docuploader('oder')
                if modlink == 4:
                    oder = oid
                    odat = Orders.query.get(oder)
                    original = odat.Original
                    if original is not None:
                        docref = f'tmp/{scac}/data/vorders/' + original
                        print(oder,docref)
                    modlink = 1
                else:
                    modlink = 0

        if modlink == 70:
            err, oid = docuploader('oder')
            modlink = 0

        if modlink == 71:
            err, oid = docuploader('poof')
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
            err.append(f'Update Completed for Customer {a[0]}')
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


                delf = request.values.get('DELF')
                if delf is not None:
                    try:
                        os.remove(addpath(docref))
                        err.append(f'File {docref} deleted')
                    except:
                        err.append('File not deleted')
                    try:
                        os.remove(addpath(doctxt))
                        err.append('File deleted')
                    except:
                        err.append('File not deleted')
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
            err.append('New Service Added to Database.')
            modlink = 0

        if update is None and modlink == 1:
            if oder > 0:
                Orders_Form_Update(oder)
                shipper = request.values.get('shipper')

                holdvec[0], holdvec[1], holdvec[2] = shipper, 0, 0
                plist = []
                delist = []
                oshipper = Orders.query.filter(Orders.Shipper == shipper).all()
                for tship in oshipper:
                    pu = tship.Company.strip()
                    du = tship.Company2.strip()
                    if pu not in plist:
                        plist.append(pu)
                    if du not in delist:
                        delist.append(du)
                holdvec[4] = plist
                holdvec[5] = delist
                holdvec[6] = request.values.get('getpuloc')
                holdvec[7] = request.values.get('getduloc')
                if holdvec[6] is not None:
                    oship = Orders.query.filter((Orders.Shipper == shipper) & (Orders.Company == holdvec[6])).first()
                    if oship is not None:
                        holdvec[8] = oship.Dropblock1

                if holdvec[8] is not None:
                    oship = Orders.query.filter((Orders.Shipper == shipper) & (Orders.Company2 == holdvec[7])).first()
                    if oship is not None:
                        holdvec[9] = oship.Dropblock2
                leftsize = 8
                leftscreen = 0
                modata = Orders.query.get(oder)
                try:
                    docref = f'tmp/{scac}/data/vorders/{modata.Original}'
                except:
                    docref = ''

        if update is not None and modlink == 1:
            if oder > 0:
                Orders_Form_Update(oder)
                Orders_Drop_Update(oder)
                modata = Orders.query.get(oder)
                try:
                    docref = f'tmp/{scac}/data/vorders/{modata.Original}'
                except:
                    docref = ''
                err.append('Modification to Trucking JO ' + modata.Jo + ' completed.')
                modlink = 0
                Order_Container_Update(oder)

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

                err.append(f'Completed Modification of Interchange for {a[0]}')
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
                err.append('Modification to Services Data with ID ' + str(modata.id) + ' completed.')
                sdat = Services.query.filter(Services.Service == 'New').first()
                if sdat is not None:
                    Services.query.filter(Services.Service == 'New').delete()
                    db.session.commit()
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
                err.append(f'Update Complete for Customer: {a[0]}')
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

            db.session.commit()
# ____________________________________________________________________________________________________________________E.InvoiceUpdate.Trucking

# ____________________________________________________________________________________________________________________B.GetData.Trucking
        odata, idata, fdata = dataget_T(thismuch, dlist, lbox)
        sdata = Services.query.order_by(Services.Price.desc()).all()
        cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
# ____________________________________________________________________________________________________________________E.GetData.Trucking
# ____________________________________________________________________________________________________________________B.Search.Trucking

        if (modlink < 10 and (update is not None or vmod is not None)) or modlink == 0 or match is not None:
            oder, tick, serv, peep, numchecked = numcheck(4, odata, idata, sdata, cdata, 0, ['oder',  'tick', 'serv', 'peep'])
        else:
            numchecked = 0

        if uploadS is not None:
            if oder > 0  and numchecked == 1:
                odat = Orders.query.get(oder)
                jo = odat.Jo
                scache = odat.Scache
                filename2 = f'Source_{jo}_c{str(scache)}.pdf'
                err.append(f'File uploaded as {filename2}')
                #Provide a file name for the upload and store message:
                edat = LastMessage.query.filter(LastMessage.User == username).first()
                if edat is not None:
                    edat.Err = json.dumps(err)
                    db.session.commit()
                else:
                    input = LastMessage(User=username, Err=json.dumps(err))
                    db.session.add(input)
                    db.session.commit()

                modlink = 70
                leftscreen = 1
                mm3 = 0
            else:
                err.append('No Job Selected for Source Upload')
                err.append('Select One Box')

        if uploadP is not None:
            if oder > 0  and numchecked == 1:
                odat = Orders.query.get(oder)
                jo = odat.Jo
                pcache = odat.Pcache
                filename2 = f'Proof_{jo}_c{str(pcache)}.pdf'
                err.append(f'File uploaded as {filename2}')
                #Provide a file name for the upload and store message:
                edat = LastMessage.query.filter(LastMessage.User == username).first()
                if edat is not None:
                    edat.Err = json.dumps(err)
                    db.session.commit()
                else:
                    input = LastMessage(User=username, Err=json.dumps(err))
                    db.session.add(input)
                    db.session.commit()
                leftscreen = 1
                modlink = 71
                mm3 = 0
            else:
                err.append('No Job Selected for Proof Upload')
                err.append('Select One Box')


        if mm2 is not None or mm3 == 1:
            if returnhit is None:
                passoder=request.values.get('passoder')
                passoder=nonone(passoder)
                mm2 = 1
            else:
                mm2, mm3 = 0, 0
                oder = 0
                passoder = 0
            print('manifest',mm2,oder,passoder,mm3)
            if (oder > 0 and numchecked == 1) or passoder > 0:
                truck='111'
                if oder == 0:
                    oder = passoder
                if update is not None or passoder > 0:
                    modata = Orders.query.get(oder)
                    vals = ['driver', 'truck', 'commodity', 'packing', 'pickup', 'seal', 'date1',
                            'time1', 'date2','time2', 'desc', 'sigdate']
                    a = list(range(len(vals)))
                    i = 0
                    for v in vals:
                        a[i] = request.values.get(v)
                        print(a[i])
                        i = i+1
                    truck=a[1]
                    # Check dates:
                    if a[6] is None:
                        a[6] = today_str
                    if a[8] is None:
                        a[8] = today_str
                    if a[11] is None:
                        a[11] = today_str
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
                    holdvec[16] = a[11]

                leftscreen=0



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
                fname = os.path.basename(docref)
                modata.Delivery = fname
                viewtype = 'manifest'
                doclist[3] = docref
                doclist[0] = f'tmp/{scac}/data/vorders/{modata.Original}'
                modata.Manifest = os.path.basename(docref)
                db.session.commit()

            else:
                err.append('Must Check One Box in Job Table')
                mm2 = 0

        # Need this comment
        if unpay == 1:
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
        def packmake(odat, eprof):
            idata = Interchange.query.filter(Interchange.CONTAINER == odat.Container).all()
            packitems = []
            if eprof == '1':
                dockind = ['Source', 'none', 'none', 'none']
            if eprof == '2':
                dockind = ['Ticks', 'none', 'none', 'none']
            elif eprof == '3':
                dockind = ['Invoice', 'none', 'none', 'none']
            elif eprof == '4':
                dockind = ['Proofs', 'none', 'none', 'none']
            elif eprof == '5':
                dockind = ['Invoice', 'Proofs', 'none', 'none']
            stampdata = [0] * 9
            for i in range(9):
                stampdata[i] = request.values.get('stampdata' + str(i))
            for i in range(4):
                if eprof is None or eprof == '6':
                    packname = 'section' + str(i + 1)
                    test = request.values.get(packname)
                else:
                    test = dockind[i]

                if test != 'none':
                    if test == 'Source':
                        fa = addpath(f'tmp/{scac}/data/vorders/{odat.Original}')
                        if os.path.isfile(fa):
                            packitems.append(fa)
                            stampdata.append('Source')
                        else:
                            err.append('No Source Document')
                    if test == 'Invoice':
                        fa = addpath(f'tmp/{scac}/data/vinvoice/{odat.Invoice}')
                        if os.path.isfile(fa):
                            packitems.append(fa)
                            stampdata.append('Invoice')
                        else:
                            err.append('No Invoice')
                    if test == 'Proofs':
                        fa = addpath(f'tmp/{scac}/data/vproofs/{odat.Proof}')
                        if os.path.isfile(fa):
                            packitems.append(fa)
                            stampdata.append('Proofs')
                        else:
                            err.append('No proof file exists')
                    if test == 'Ticks':
                        fa = addpath(f'tmp/{scac}/data/vinterchange/{odat.Gate}')
                        if os.path.isfile(fa):
                            packitems.append(fa)
                            stampdata.append('Ticks')
                        elif idata is not None:
                            stampdata.append('Ticks')
                            if len(idata) > 1:
                                # Get a blended ticket
                                con = idata[0].CONTAINER
                                newdoc = f'tmp/{scac}/data/vinterchange/{con}_Blended.pdf'
                                if os.path.isfile(addpath(newdoc)):
                                    print(f'{newdoc} exists already')
                                else:
                                    g1 = f'tmp/{scac}/data/vinterchange/{idata[0].Original}'
                                    g2 = f'tmp/{scac}/data/vinterchange/{idata[1].Original}'
                                    blendticks(addpath(g1), addpath(g2), addpath(newdoc))
                                    odat.Gate = f'{con}_Blended.pdf'
                                    db.session.commit()
                                packitems.append(addpath(newdoc))
                            else:
                                packitems.append(addpath(f'tmp/{scac}/data/vinterchange/{idata[0].Original}'))
                else:
                    stampdata.append('none')

            if len(stampdata) < 13:
                for ix in range(len(stampdata), 13):
                    stampdata.append('none')

            return packitems, stampdata, err

# ____________________________________________________________________________________________________________________B.Package.Trucking
        if (reorder is not None or stampnow is not None or eprof is not None) and emailnow is None:

            oder=request.values.get('passoder')
            oder=nonone(oder)
            odat=Orders.query.get(oder)
            viewtype = 'packages'
            print('packages with eprof',eprof)

            packitems, stampdata, err = packmake(odat, eprof)
            print('My stampdata is', stampdata)

            cache2 = int(odat.Pkcache)
            odat.Pkcache = cache2 + 1
            docref = f'tmp/{scac}/data/vpackages/P_c{cache2}_{odat.Jo}.pdf'
            odat.Package = f'P_c{cache2}_{odat.Jo}.pdf'
            db.session.commit()
            try:
                pdflist=['pdfunite']+packitems+[addpath(docref)]
                tes = subprocess.check_output(pdflist)
                leftscreen = 0
                stampstring = json.dumps(stampdata)
                print('stampstring=', stampstring)
                odat.Status = stampstring
                db.session.commit()
            except:
                print('The File Does Not Exist')
                leftscreen = 0

            #Get the email data also in case changes occur there

            if eprof is not None:
                holdvec[0] = eprof
                thisprofile = 'eprof' + eprof
                kind = 0
                emaildata = etemplate_truck('package', thisprofile, odat)
                print('myemaildata:', thisprofile,emaildata)
            else:
                emaildata = [0] * 7
                for i in range(7):
                    emaildata[i] = request.values.get('edat' + str(i))

        if (mpack is not None and numchecked == 0):
            err.append('Must Select at Least One Job for this Option')
        if (mpack is not None and numchecked == 1) and emailnow is None:
            if eprof is not None:
                oder = request.values.get('passoder')
                oder = nonone(oder)
            if oder > 0:
                fexist = [0] * 5
                dockind = ['Source', 'Proofs', 'Invoice', 'Gate']
                viewtype = 'packages'
                leftscreen = 0
                stamp = 1
                odat = Orders.query.get(oder)
                company = odat.Shipper
                jo = odat.Jo
                order = odat.Order
                cache2 = int(odat.Pkcache)
                cache2 = cache2 + 1
                docref = f'tmp/{scac}/data/vpackages/P_c{cache2}_{odat.Jo}.pdf'
                doclist[7] = f'tmp/{scac}/data/vpackages/P_c{cache2}_{odat.Jo}.pdf'
                odat.Pkcache = cache2
                db.session.commit()

                stampstring = odat.Status
                try:
                    stampdata = json.loads(stampstring)
                    if isinstance(stampdata, list):
                        print('stampdata is',stampdata)
                    else:
                        stampdata = None
                except:
                    stampdata = None

                if stampdata is None:
                    packitems = []
                    stampdata = [3, 35, 35, 5, 120, 100, 5, 477, 350]
                    doclist[0] = f'tmp/{scac}/data/vorders/{odat.Original}'
                    doclist[1] = f'tmp/{scac}/data/vproofs/{odat.Proof}'
                    doclist[2] = f'tmp/{scac}/data/vinvoice/{odat.Invoice}'
                    doclist[3] = f'tmp/{scac}/data/vinterchange/{odat.Gate}'

                    #Package output file

                    odat.Package = f'P_c{cache2}_{odat.Jo}.pdf'
                    db.session.commit()

                    for ix in range(4):
                        if dockind[ix] != 'none':
                            fexist[ix] = os.path.isfile(addpath(doclist[ix]))
                            if fexist[ix] == 0:
                                print(f'{addpath(doclist[ix])} does not exist')
                                err.append(f'No {dockind[ix]} Document Exists')
                            else:
                                packitems.append(addpath(doclist[ix]))
                                stampdata.append(dockind[ix])

                    if len(stampdata)<13:
                        for ix in range(len(stampdata),13):
                            stampdata.append('none')

                    print('packitems final:', packitems)
                    print('stampdata final:', stampdata)
                    stampstring = json.dumps(stampdata)
                    print(len(stampstring))
                    print(stampstring)
                    odat.Status = stampstring
                    db.session.commit()
                else:
                    packitems = []
                    subdata = stampdata[9:13]
                    stampdata = stampdata[0:9]
                    print('subdata is ',subdata)
                    for test in subdata:
                        if test != 'none':
                            if test == 'Source':
                                fa = addpath(f'tmp/{scac}/data/vorders/{odat.Original}')
                                if os.path.isfile(fa):
                                    packitems.append(fa)
                                    stampdata.append(test)
                            if test == 'Invoice':
                                fa = addpath(f'tmp/{scac}/data/vinvoice/{odat.Invoice}')
                                if os.path.isfile(fa):
                                    packitems.append(fa)
                                    stampdata.append(test)
                            if test == 'Proofs':
                                fa = addpath(f'tmp/{scac}/data/vproofs/{odat.Proof}')
                                if os.path.isfile(fa):
                                    packitems.append(fa)
                                    stampdata.append(test)
                            if test == 'Ticks':
                                idata = Interchange.query.filter(Interchange.CONTAINER == odat.Container).all()
                                if idata is not None:
                                    if len(idata) > 1:
                                        # Get a blended ticket
                                        con = idata[0].CONTAINER
                                        newdoc = f'tmp/{scac}/data/vinterchange/{con}_Blended.pdf'
                                        if os.path.isfile(addpath(newdoc)):
                                            print(f'{newdoc} exists already')
                                        else:
                                            g1 = f'tmp/{scac}/data/vinterchange/{idata[0].Original}'
                                            g2 = f'tmp/{scac}/data/vinterchange/{idata[1].Original}'
                                            blendticks(addpath(g1), addpath(g2), addpath(newdoc))
                                        packitems.append(addpath(newdoc))
                                        stampdata.append(test)
                                    else:
                                        packitems.append(addpath(f'tmp/{scac}/data/vinterchange/{idata[0].Original}'))
                                        stampdata.append(test)

                    if len(stampdata)<13:
                        for ix in range(len(stampdata),13):
                            stampdata.append('none')

                    # Get the email data also in case changes occur there
                    emaildata = [0] * 7
                    for i in range(7):
                        emaildata[i] = request.values.get('edat' + str(i))

                print('packitems final:', packitems)
                print('stampdata final:', stampdata)

                if len(packitems) >= 1:
                    pdflist = ['pdfunite'] + packitems + [addpath(docref)]
                    tes = subprocess.check_output(pdflist)

                    if eprof is not None:
                        thisprofile = 'eprof'+eprof
                        viewtype = 'packages'
                    else:
                        viewtype = 'packages'
                        thisprofile = 0
                    emaildata = etemplate_truck(viewtype, thisprofile, odat)
                    invo = 3
                    doclist[0] = docref
                else:
                    err.append('No documents available for this selection')
                    viewtype, mpack, stamp, leftscreen = 0, 0, 0, 1


            else:
                err.append('Must Select One Job to Use this Function')
                viewtype, mpack, stamp, leftscreen = 0, 0, 0, 1

            print("on exit docref is ", docref)

        if stampnow is not None:
            # if stampnow is called the document will already be recreated as a blank for here
            # and the information includes odat, pdat, idata
            err.append('Review Signed Package')
            stamp = 1
            leftscreen = 0
            leftsize = 8
            modlink = 0
            cache2 = int(odat.Pkcache)
            docin = f'tmp/{scac}/data/vpackages/{odat.Package}'
            docref = f'tmp/{scac}/data/vpackages/P_c{cache2}_{odat.Jo}.pdf'
            odat.Package = f'P_c{cache2}_{odat.Jo}.pdf'
            db.session.commit()
            from sigdoc import sigdoc
            sigdoc(stampdata, docin, docref)
            odat.Pkcache = cache2 + 1
            db.session.commit()
            # Already have email data from previous area
            invo = 3
            viewtype = 'packages'


# ____________________________________________________________________________________________________________________E.Package.Trucking
# ____________________________________________________________________________________________________________________B.Package2.Trucking

        if (mpack is not None and numchecked > 1) and emailnow is None:
            err.append('Combining Documents for Summary Invoice')
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
            #file1 = f'tmp/{scac}/data/vinvoice/P_' + 'test.pdf'
            print('file1here=',file1)
            cache2 = int(odat.Detention)
            cache2 = cache2+1
            docref = f'tmp/{scac}/data/vinvoice/P_c{cache2}_{order}.pdf'

            for j, i in enumerate(odervec):
                odat = Orders.query.get(i)
                odat.Package = docref
                db.session.commit()

            import make_TP_invoice
            make_TP_invoice.main(file1, keydata, grandtotal, pdata1, date1, date2)

            invooder = oder
            leftscreen = 0
            leftsize = 8
            modlink = 0

            filegather = ['pdfunite', addpath(file1)]
            codata = companydata()
            etitle = codata[2]+' Invoices:'
            #Prepare for email, but at this point only created invoice
            for i in odervec:
                odat = Orders.query.get(i)
                etitle = etitle+' '+odat.Jo
                filegather.append(addpath(odat.Invoice))
                odat.Istat = 1
                db.session.commit()

            filegather.append(addpath(docref))
            tes = subprocess.check_output(filegather)

            emaildata = etemplate_truck('invoice', 0 , odat)
            invo = 3
            viewtype = 'packages'
# ____________________________________________________________________________________________________________________E.Package2.Trucking
# ____________________________________________________________________________________________________________________B.Email.Trucking
        # With loginvo we are recording invoice in ledger, but manually taking the invoice to customer
        if loginvo is not None:
            odat = Orders.query.get(invooder)
            loginvo_m(odat,2)
            modlink = 0
            invo = 0
            invooder = 0
            stamp = 0
            inco = 0
            oder = 0


        # This area for receiving money--cannot mass receive funds off the list
        if logrec is not None:
            odat = Orders.query.get(invooder)
            jo = odat.Jo
            inc = Income.query.filter(Income.Jo==jo).first()
            acctdb = inc.SubJo
            if acctdb is None:
                acctdb = 'Undeposited Funds'
            gledger_write('income',jo,acctdb,0)
            odat.Istat = 4
            db.session.commit()
            modlink, invo, invooder, oder, stamp, inco = 0, 0, 0, 0, 0, 0

        if emailnow is not None or emailinvo is not None:
            oder=request.values.get('passoder')
            oder = nonone(oder)
            if oder == 0:
                oder = request.values.get('invooder')
            print('oderhere=',oder,invooder)
            viewtype = request.values.get('viewtype')

            odat=Orders.query.get(oder)
            jo = odat.Jo
            order = odat.Order
            print('viewtype=',viewtype)

            if viewtype == 'packages' or viewtype == 'invopackage':
                docref = odat.Package

            elif viewtype == 'paidinvoice':
                incdat = Income.query.filter(Income.Jo == jo).first()
                if incdat is not None:
                    docref = incdat.Original
                    print(docref)
                    if docref is not None:
                        docref = os.path.basename(docref)
                        print(docref)

            elif viewtype == 'invoice':
                docref = odat.Invoice

            if viewtype == 'invopackage' or viewtype == 'invoice' or eprof == '3' or eprof == '5':
                loginvo_m(odat, 3)

            print('mydocref=',docref)
            emailin1 = invoice_mimemail(order, docref, eprof)
            invo, invooder, oder, stamp, modlink, viewtype, leftscreen= 0, 0, 0, 0, 0, 0, 1
            err.append(f'Successful email to: {emailin1}')
# ____________________________________________________________________________________________________________________E.Email.Trucking
# ____________________________________________________________________________________________________________________B.Views.Trucking

        if viewo == 1 and numchecked == 1:
            if oder > 0:
                modata = Orders.query.get(oder)
                if modata.Original is not None:
                    doclist[0] = f'tmp/{scac}/data/vorders/{modata.Original}'
                    err.append(f'Viewing document {modata.Original}')
                    viewtype = 'source'
                    leftscreen = 0
                else:
                    err.append('There is no source document available for this selection')
            if tick > 0:
                modata = Interchange.query.get(tick)
                if modata.Original is not None:
                    doclist[5] = f'tmp/{scac}/data/vinterchange/{modata.Original}'
                    viewtype = 'gate1'
                    leftscreen = 0
                    err.append(f'Viewing document {modata.Original}')
                else:
                    err.append('There is no source document available for this selection')

        if viewp == 1 and numchecked == 1:
            if oder > 0:
                modata = Orders.query.get(oder)
                if modata.Proof is not None:
                    viewtype = 'proof'
                    leftscreen = 0
                    doclist[2] = f'tmp/{scac}/data/vproofs/{modata.Proof}'
                    err.append(f'Viewing document {modata.Proof}')
                else:
                    err.append('There is no proof document available for this selection')
            else:
                err.append('Must select one job to use this function')

        if (viewo == 1 or viewp == 1 or viewi == 1 or viewip ==1) and numchecked != 1:
            err.append('Must check exactly one box to use this option')

        if viewi == 1 and numchecked == 1:
            if oder > 0:
                modata = Orders.query.get(oder)
                try:
                    docref = f'tmp/{scac}/data/vinvoice/{modata.Invoice}'
                    emaildata = etemplate_truck('invoice',0,modata)
                    leftscreen = 0
                    modlink = 0
                    invo = 1
                    invooder = oder
                    err.append(f'Viewing document {docref}')
                    viewtype = 'invoice'
                except:
                    err.append('There is no document available for this selection')

        if viewip == 1 and numchecked == 1:
            if oder > 0:
                modata = Orders.query.get(oder)
                jo = modata.Jo
                incdat = Income.query.filter(Income.Jo == jo).first()
                if incdat is not None:
                    fname = incdat.Original
                    if fname is None:
                        fexist=0
                    else:
                        fname = os.path.basename(fname)
                        docref = f'tmp/{scac}/data/vinvoice/{fname}'
                        fexist = os.path.isfile(addpath(docref))
                    if not fexist:
                        #Need to create the paid invoice
                        recamount = incdat.Amount
                        custref = incdat.Ref
                        recdate = incdat.Date
                        acctdb = incdat.SubJo
                        if acctdb is None:
                            acctdb = 'Undeposited Funds'

                        payment = [d2sa(recamount), custref, recdate, acctdb]

                        ldata = Invoices.query.filter(Invoices.Jo == jo).order_by(Invoices.Ea.desc()).all()
                        cache = modata.Storage + 1
                        modata.Storage = cache
                        db.session.commit()
                        pdata1 = People.query.filter(People.id == modata.Bid).first()
                        pdata2 = Drops.query.filter(Drops.id == modata.Lid).first()
                        pdata3 = Drops.query.filter(Drops.id == modata.Did).first()

                        print(payment)

                        from make_T_invoice import T_invoice
                        fname = T_invoice(modata, ldata, pdata1, pdata2, pdata3, cache, invodate, payment)
                        fname = os.path.basename(fname)
                        docref = f'tmp/{scac}/data/vinvoice/{fname}'

                        incdat.Original = fname
                        db.session.commit()

                    emaildata = etemplate_truck('paidinvoice',0,modata)
                    leftscreen = 0
                    err.append(f'Viewing document {docref}')
                    viewtype = 'paidinvoice'
                else:
                    err.append(f'No payments received against JO {jo}')


        if viewm == 1 and numchecked == 1:
            if oder > 0:
                modata = Orders.query.get(oder)
                if modata.Manifest is not None:
                    viewtype = 'manifest'
                    leftscreen = 0
                    doclist[3] = f'tmp/{scac}/data/vmanifest/{modata.Delivery}'
                    err.append(f'Viewing document {modata.Delivery}')
                else:
                    err.append('There is no manifest document available for this selection')
            else:
                err.append('Must select one job to use this function')

        if viewg ==1 and numchecked == 1:
            if oder > 0:
                odat = Orders.query.get(oder)
                base = odat.Gate
                newdoc = f'tmp/{scac}/data/vinterchange/{base}'
                if os.path.isfile(addpath(newdoc)):
                    doclist[6] = newdoc
                    doclist[5] = 0
                    doclist[4] = 0
                else:
                    jo = odat.Jo
                    idat = Interchange.query.filter( (Interchange.Jo == odat.Jo) & (Interchange.TYPE.contains('Out')) ).first()
                    if idat is not None:
                        viewtype = 'gate1'
                        leftscreen = 0
                        doclist[4] = f'tmp/{scac}/data/vinterchange/{idat.Original}'
                        err.append(f'Viewing document {idat.Original}')
                    else:
                        err.append('There is no gate OUT ticket available for this selection')

                    idat = Interchange.query.filter( (Interchange.Jo == odat.Jo) & (Interchange.TYPE.contains('In')) ).first()
                    if idat is not None:
                        viewtype = 'gate2'
                        leftscreen = 0
                        con = idat.CONTAINER
                        doclist[5] = f'tmp/{scac}/data/vinterchange/{idat.Original}'
                        err.append(f'Viewing document {idat.Original}')
                        if doclist[4] !=0 and doclist[5] != 0:
                            viewtype = 'gate3'
                            #Get a blended ticket
                            con = idat.CONTAINER
                            base = f'{jo}_{con}_blend.pdf'
                            newdoc = f'tmp/{scac}/data/vinterchange/{base}'
                            if os.path.isfile(addpath(newdoc)):
                                print(f'{newdoc} exists')
                            else:
                                blendticks(addpath(doclist[4]),addpath(doclist[5]),addpath(newdoc))
                            odat.Gate = base
                            doclist[6] = newdoc
                            doclist[5] = 0
                            doclist[4] = 0

                    else:
                        err.append('There is no gate IN ticket available for this selection')
            else:
                err.append('Must select one job to use this function')


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
                    err.append('Current Payment Invoice')
                    if docref is None:
                        docref = modata.Original
                        err.append('No Payment Invoice Yet')
            else:
                err.append('Must check one Job')


# ____________________________________________________________________________________________________________________E.Views.Trucking
# ____________________________________________________________________________________________________________________B.Modify.Trucking
        if (modify is not None or vmod is not None) and numchecked == 1:
            modlink = 1
            leftsize = 8

            if oder > 0:
                modata = Orders.query.get(oder)
                csize = People.query.filter(
                    People.Ptype == 'Trucking').order_by(People.Company).all()
                docref = ' '
                if vmod is not None:
                    err.append('There is no document available for this selection')
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vorders/' + modata.Original
                            doctxt = docref.split('.', 1)[0]+'.txt'
                            err.append('All is well')

            if poof > 0:
                modata = Proofs.query.get(poof)
                if vmod is not None:
                    err.append('There is no document available for this selection')
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = modata.Original
                            err.append('All is well' )
            if tick > 0:
                modata = Interchange.query.get(tick)
                if vmod is not None:
                    err.append('There is no document available for this selection')
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vinterchange/' + modata.Original
                            err.append('All is well')

            if serv > 0:
                modata = Services.query.get(serv)
                if vmod is not None:
                    err.append('There is no document available for this selection')

            if peep > 0:
                modata = People.query.get(peep)
                if vmod is not None:
                    err.append('There is no document available for this selection')

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
            err.append('Must check exactly one box to use this option')
# ____________________________________________________________________________________________________________________E.Modify.Trucking
# ____________________________________________________________________________________________________________________B.AddItems.Trucking
        if addS is not None and serv > 0 and numchecked == 1:
            leftsize = 8
            modlink = 2
            modata = Services.query.get(serv)

        if addS is not None and numchecked == 0:
            leftsize = 8
            modlink = 1
            Services.query.filter( (Services.Service == 'New') & ( Services.Price==0.00 )).delete()
            # We will create a blank line and simply modify that by updating:
            input = Services(Service='New', Price=0.00)
            db.session.add(input)
            db.session.commit()
            modata = Services.query.filter(Services.Service == 'New').first()
            serv = modata.id
            err.append('Enter Data for New Service')

        if addS is not None and numchecked > 1:
            modlink = 0
            err.append('Must check exactly one box to use this option')

        if addE is not None and serv > 0 and numchecked == 1:
            leftsize = 8
            modlink = 3
            modata = Services.query.get(peep)

        if addE is not None and numchecked == 0:
            leftsize = 8
            modlink = 1
            #Make sure there are no new iputs unused
            People.query.filter( (People.Company =='') & (People.Temp1 == 'New') & (People.Ptype == 'Trucking') ).delete()
            # We will create a blank line and simply modify that by updating:
            input = People(Company='New', First=None, Middle=None, Last=None, Addr1='', Addr2='', Addr3='', Idtype=None, Idnumber=None, Telephone='',
                           Email='', Associate1='', Associate2='', Date1=today, Date2=None, Original=None, Ptype='Trucking', Temp1='New', Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter((People.Company == 'New') & (People.Temp1 == 'New') & (People.Ptype == 'Trucking') ).first()
            peep = modata.id
            modata.Company = ''
            db.session.commit()
            modata = People.query.get(peep)
            err.append('Enter Data for New Company')

        if addE is not None and numchecked > 1:
            modlink = 0
            err.append('Must check exactly one box to use this option')

        if addI is not None and numchecked == 0:
            leftscreen = 0
            leftsize = 8
            modlink = 20
            # We will create a blank line and simply modify that by updating:
            input = Interchange(CONTAINER='New', TRUCK_NUMBER='', DRIVER='', CHASSIS='', Date=None, RELEASE='', GROSS_WT='',
                                SEALS='', CONTYPE='', CARGO_WT='', Time=None, Status='Unmatched', Original='', Path='', TYPE='Empty Out', Jo='', Company='')

            db.session.add(input)
            db.session.commit()
            modata = Interchange.query.filter(Interchange.CONTAINER == 'New').first()
            tick = modata.id
            err.append('Enter Data for New Interchange Ticket')

        if slim is not None and (numchecked != 1 or oder == 0):
            modlink = 0
            err.append('Must select exactly one box from Shipping Data to use this option')

        if slim is not None and numchecked == 1 and oder > 0:
            odata1 = Orders.query.get(oder)
            stayslim = odata1.id
            err.append('Showing SLIM data around JO='+odata1.Jo)
            modlink = 0

# ____________________________________________________________________________________________________________________E.AddItems.Trucking
# ____________________________________________________________________________________________________________________B.Delete.Trucking
        if deletehit is not None and numchecked == 1:
            if oder > 0:
                odat = Orders.query.get(oder)
                jo = odat.Jo
                Gledger.query.filter(Gledger.Tcode==jo).delete()
                Orders.query.filter(Orders.id == oder).delete()
            if tick > 0:
                Interchange.query.filter(Interchange.id == tick).delete()
            if peep > 0:
                People.query.filter(People.id == peep).delete()
            if serv > 0:
                Services.query.filter(Services.id == serv).delete()
                sdata = Services.query.order_by(Services.Price.desc()).all()

            db.session.commit()

        if deletehit is not None and numchecked != 1:
            err.append('Must have exactly one item checked to use this option')
# ____________________________________________________________________________________________________________________E.Delete.Trucking


# ____________________________________________________________________________________________________________________B.ReceivePayment.Trucking

        if (recpay is not None and oder > 0 and numchecked == 1) or recupdate is not None:
            leftsize = 8
            if recpay is not None:
                invooder = oder
            odat = Orders.query.get(invooder)



            invojo = odat.Jo
            co = invojo[0]
            acdata = Accounts.query.filter((Accounts.Type=='Bank') & (Accounts.Co == co)).order_by(Accounts.Name).all()
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
            err.append('Have no Invoice to Receive Against')
            if ldat is not None:
                invodate = ldat.Date
                invoamt = ldat.Total
                if ldat.Original is not None:
                    docref = ldat.Original
                    leftscreen = 0
                    leftsize = 8

                incdat = Income.query.filter(Income.Jo == invojo).first()
                if incdat is None:
                    print('incdat is none')
                    err.append('Creating New Payment on Jo')
                    paydesc = 'Receive payment on Invoice ' + invojo
                    recamount = ldat.Total

                    recdate = datetime.date.today()
                    acctdb = 'Undeposited Funds'

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

                try:
                    lastpr = custref + '\n' + acctdb
                except:
                    print('Could not create lastpr')
                incdat = Income.query.filter(Income.Jo == invojo).first()

                payment = [recamount, custref, recdate, acctdb]
                print('payment = ', payment)

                modata = Income.query.filter(Income.Jo == invojo).first()
                inco = modata.id
                err.append('Amend Payment for Invoice '+invojo)

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
                incdat.Original = os.path.basename(docref)
                hstat = odat.Hstat
                if hstat == 2 or hstat == 3:
                    odat.Hstat = 4
                odat.Istat = 4
                db.session.commit()
                leftscreen = 0
                err.append('Viewing '+docref)
                emaildata = etemplate_truck('paidinvoice', 0, odat)
                viewtype = 'paidinvoice'

        if recpay is not None and (oder == 0 or numchecked != 1):
            err.append('Invalid selections')
            if oder == 0:
                err.append('Must select a Trucking Job')
            if numchecked != 1:
                err.append('Must select exactly one Trucking Job')
# ____________________________________________________________________________________________________________________E.Receive Payment.Trucking
# ____________________________________________________________________________________________________________________B.Payment History.Trucking
        if hispay is not None or modlink == 7:
            if oder == 0 and invooder == 0:
                err.append('Must select a Trucking Job')
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

        if viewtype == 'columnadd' or umc is not None:
            if oder > 0 and numchecked >= 1:
                odata = Orders.query.all()
                odervec = numcheckv(odata)
                for oder in odervec:
                    myo = Orders.query.get(oder)
                    myo.Links = json.dumps(odervec)
                    db.session.commit()

            else:
                err.append('Must select one or more jobs for this function')
                viewtype = 0



# ____________________________________________________________________________________________________________________B.Invoice.Trucking and Quotes
        if ((minvo is not None and oder > 0) and numchecked > 1) or umi is not None:
            err.append('Creating Multi-Job Invoice')

            if umi is None:
                odata = Orders.query.all()
                odervec = numcheckv(odata)

            invooder = odervec[0]

            thesematch = 1
            for j, oder in enumerate(odervec):
                myo = Orders.query.get(oder)
                if umi is not None:
                    myo.Amount = newbase
                    db.session.commit()
                if j == 0:
                    shipco = myo.Shipper
                else:
                    shipper = myo.Shipper
                    if shipco != shipper:
                        thesematch = 0

            if thesematch == 1:
                print('l_Invoice Selections Matched')
                ichas = 1
                if umi is not None:
                    if newchas == '0.00':
                        ichas = 0
                else:
                    newchas = 0
                docref = multi_inv(odata, odervec, ichas, newchas)
            else:
                err.append('Shippers Not Matched')

            if thesematch == 1:
                leftscreen = 0
                invo = 2
                leftsize = 8
                for oder in odervec:
                    myo = Orders.query.get(oder)
                    myo.Links = json.dumps(odervec)
                    db.session.commit()
                err.append(f'Multi-Invoice:{json.dumps(odervec)}')
                err.append(f'Viewing {docref}')
                emaildata = etemplate_truck('invopackage',0,myo)
                invo = 2
                viewtype = 'invopackage'

        if ((minvo is not None and oder > 0 and numchecked == 1) or invoupdate is not None) or ((mquot is not None and oder > 0 and numchecked ==1 ) or quotupdate is not None):

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
                err.append('No Billing Data')
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
                err.append('Have needed items to make invoice')
                invo = 1
                leftsize = 8
                cache = myo.Storage+1

                # These are the services we wish to add to the invoice
                print('servid=',servid)
                if servid > 0:
                    mys = Services.query.get(servid)
                    if mys is not None:
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
                    err.append('No services on invoice yet and none selected')
                else:
                    invo = 1
                    leftsize = 8
                    invodate = ldat.Date
                    err.append('Created invoice for JO= '+myo.Jo)
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
                        ldatl.Original = os.path.basename(docref)
                        db.session.commit()

                    myo.Invoice = os.path.basename(docref)
                    myo.Storage = cache
                    myo.Amount = d2s(total)
                    db.session.commit()

                    leftscreen = 0
                    err.append('Viewing '+docref)
                    modata = Orders.query.get(invooder)
                    idata = Invoices.query.filter(Invoices.Jo == jo).all()
                    ldat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
                    jo = modata.Jo
                    order = modata.Order
                if (minvo is not None and oder > 0 and numchecked == 1) or invoupdate is not None:
                    emaildata = etemplate_truck('invoice',0,modata)
                    viewtype = 'invoice'
                else:
                    emaildata = etemplate_truck('quote',0,modata)
                #invo = 1
        if minvo is not None and oder == 0:
            err.append('Must select a job to create/edit invoice')
# ____________________________________________________________________________________________________________________E.Invoice.Trucking
# ____________________________________________________________________________________________________________________B.Newjob.Trucking
        if newjob is not None:
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            modlink = 4
            leftsize = 8
            leftscreen = 0
            docref = None
            holdvec=['']*20
            holdvec[16] = today_str
            holdvec[17] = today_str
            holdvec[18] = '500.00'

        if newjob is None and modlink == 4:
            holdvec = [''] * 20
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            leftscreen = 0
            shipper = request.values.get('shipper')
            pufrom = request.values.get('thislcomp')
            deltoc = request.values.get('thisdcomp')
            holdvec[0], holdvec[1], holdvec[2] = shipper, pufrom, deltoc
            plist=[]
            delist=[]
            oshipper = Orders.query.filter(Orders.Shipper == shipper).all()
            for tship in oshipper:
                try:
                    pu = tship.Company.strip()
                except:
                    pu = tship.Company
                try:
                    du = tship.Company2.strip()
                except:
                    du = tship.Company2
                if pu not in plist:
                    plist.append(pu)
                if du not in delist:
                    delist.append(du)
            holdvec[4]=plist
            holdvec[5]=delist
            holdvec[6] = request.values.get('getpuloc')
            holdvec[7] = request.values.get('getduloc')
            if holdvec[6] is not None:
                oship = Orders.query.filter( (Orders.Shipper == shipper) & (Orders.Company == holdvec[6]) ).first()
                if oship is not None:
                    holdvec[8] = oship.Dropblock1
            if holdvec[8] is not None:
                oship = Orders.query.filter( (Orders.Shipper == shipper) & (Orders.Company2 == holdvec[7]) ).first()
                if oship is not None:
                    holdvec[9] = oship.Dropblock2
            vals = ['order', 'bol', 'booking', 'container', 'ctype', 'pickup',
                    'date', 'date2', 'amount']
            a = list(range(len(vals)))
            for i, v in enumerate(vals):
                a[i] = request.values.get(v)
                if a[i]:
                    a[i] = a[i].strip()
                    itap = i+10
                    holdvec[itap] = a[i]
            amt = request.values.get('amount')
            holdvec[18] = d2sa(amt)



        if thisjob is not None:
            modlink = 0
            # Create the new database entry for the source document
            oid, nextjo = make_new_order()
            modata = Orders.query.filter(Orders.Jo == nextjo).first()
            cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
            oder = modata.id
            Order_Container_Update(oder)
            leftscreen = 1
# ____________________________________________________________________________________________________________________E.Newjob.Trucking
        if copy is not None:
            now = datetime.datetime.now().strftime('%I:%M %p')
            if oder > 0 and numchecked == 1:
                sdate = today.strftime('%Y-%m-%d')
                nextjo = newjo(jbcode, sdate)
                myo = Orders.query.get(oder)
                load = myo.Company[0:1]+nextjo[-5:]
                order = myo.Company[0:1]+nextjo[-5:]
                original = myo.Original
                input = Orders(Status='A0', Jo=nextjo, Load=load, Order=order, Company=myo.Company, Location=None, Booking=myo.Booking, BOL=myo.BOL,
                               Container='TBD', Date=today, Driver=None, Company2=myo.Company2, Time=now, Date2=today, Time2=now,
                               Seal=myo.Seal, Pickup=myo.Pickup, Delivery=None, Amount=myo.Amount, Path=None, Original=original,
                               Description=myo.Description, Chassis=myo.Chassis, Detention='0', Storage='0', Release=0, Shipper=myo.Shipper,
                               Type=myo.Type, Time3=None, Bid=myo.Bid, Lid=myo.Lid, Did=myo.Did, Label=myo.Label, Dropblock1=myo.Dropblock1,
                               Dropblock2=myo.Dropblock2, Commodity=myo.Commodity,Packing=myo.Packing, Links=myo.Links, Hstat=-1,
                               Istat=-1,Proof=None,Invoice=None,Gate=None,Package=None,Manifest=None,Scache=0,Pcache=0,
                               Icache=0,Mcache=0,Pkcache=0, QBi=0)
                db.session.add(input)
                db.session.commit()
                err.append(f'Added new Order for {myo.Shipper} with JO {nextjo}')
            else:
                err.append('Must check one box for this function to work')

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
                err.append('Must select exactly one box to choose this option.')

# ____________________________________________________________________________________________________________________B.ManualUpdate.Trucking

        if loadc == 1:
            if oder > 0:
                odervec = numcheckv(odata)
                for oder in odervec:
                    myo = Orders.query.get(oder)
                    hstat = myo.Hstat
                    istat = myo.Istat
                    if hstat != 4:
                        if istat == 4:
                            myo.Hstat = 4
                            err.append(f'Invoice Status for {myo.Jo} Updated to Paid Complete')
                        else:
                            myo.Hstat = 3
                            err.append(f'Haul Status for {myo.Jo} Updated to Complete')
                        db.session.commit()
                    else:
                        err.append(f'Load {myo.Jo} already has paid & complete status')
            else:
                err.append('Must check at least one box')

        if acceptthese is not None:
            err.append('Must check at least one box')
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
                    if odat.Istat == -1:
                        odat.Istat = 0
                        db.session.commit()
                else:
                    err.append('All status must contain A')
                    err.append('Must check exactly one box to use this option')

            if tick > 0:
                err.append('Load Completion Status Updated')
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
                Match_Trucking_Now()
                err.append('Ran Global Truck to Interchange Matcher')

            elif oder > 0 and tick > 0 and numchecked == 2:
                Match_Ticket(oder,tick)
                err.append(f'Ran Matcher for Truck ID {oder} and Interchange ID {tick}')

            else:
                err.append('Must check one Truck Job and one Interchange Ticket to Match')
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
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero, dataget_T
        username = session['username'].capitalize()
        try:
            edat = LastMessage.query.filter(LastMessage.User==username).first()
        except:
            input = LastMessage(User = username, Err='No Message')
        if edat is not None:
            try:
                err = json.loads(edat.Err)
            except:
                err=['Problem with Json Loads']
            # Got the past message now set it back to default
            edat.Err = json.dumps(['All is Well from Previous'])
            db.session.commit()
        else:
            err = []
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        doclist = [0]*8
        filesel = ''
        docref = ''
        doctxt = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        stampdata = ''
        tdata=0
        drvdata=0
        bklist = 0
        lastpr = 0
        mm2=0
        viewtype = 0

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
        lbox = 0

        stampdata = [3, 35, 35, 5, 120, 100, 5, 477, 350]
        leftsize = 10
        thismuch = '1'

    odata, idata, fdata = dataget_T(thismuch, dlist, lbox)
    alltdata = Drivers.query.all()
    allvdata = Vehicles.query.all()
    if invo is not None:
        leftsize = 8
    else:
        leftsize=9
    rightsize = 12-leftsize
    sdata2 = Services.query.order_by(Services.Service).all()
    err = erud(err)
    pdata = 0
    if doclist[0] == 0:
        doclist = [docref] + doclist[1:]

    print(viewtype,doclist,lbox)
    return lbox, doclist, username, bklist, lastpr, thismuch, etitle, ebody, emaildata, odata, pdata, idata, sdata, cdata, oder, poof, sdata2, tick, serv, peep, err, modata, caldays, daylist, nweeks, howapp, modlink, leftscreen, docref, 0, leftsize, newc, tdata, drvdata, dlist, rightsize, ldata, invodate, inco, invo, quot, invooder, cache, stamp, alltdata, allvdata, stampdata, fdata, filesel, today, now, doctxt, holdvec, mm2, viewtype
