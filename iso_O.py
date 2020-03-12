from runmain import db
from models import Vehicles, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers
from models import ChalkBoard, Services
from flask import render_template, flash, redirect, url_for, session, logging, request
from CCC_system_setup import myoslist, addpath, usernames, passwords, tpath, companydata, scac

import math
from decimal import Decimal
import datetime
import calendar
import os
import subprocess
import shutil
import re
import pytz
from viewfuncs import d2s, stat_update, tabdataR, popjo, jovec, newjo, timedata, nonone, nononef, nodollar, init_ocean_zero, numcheck, sdiff, calendar7_weeks, containersout, numcheckvec
from InterchangeFuncs import InterStrip, InterMatchThis, InterDupThis, PushJobsThis, Check_Sailing
from func_cal import calmodalupdate
from dockmaker import dockm

cdata = companydata()
jbcode = cdata[10] + 'O'

def dataget_O(thismuch, dlist):
    # 0=order,#1=proofs,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    odata = 0  # dlist[0]
    adata = 0  # dlist[1]
    bdata = 0  # dlist[2]
    pdata = 0  # dlist[3]
    idata = 0  # dlist[4]
    if dlist[3] == 'on' or dlist[0] == 'on':
        pdata = People.query.filter(People.Ptype.contains('OverSeas')
                                    ).order_by(People.Company).all()
    if thismuch == '1':
        if dlist[0] == 'on':
            odata = OverSeas.query.filter(OverSeas.Status.contains('3')).all()
        if dlist[1] == 'on':
            adata = Autos.query.filter(Autos.Date1 > stopdate).all()
        if dlist[2] == 'on':
            bdata = Bookings.query.filter(Bookings.PortCut > stopdate).all()
        if dlist[4] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '2':
        stopdate = today-datetime.timedelta(days=45)
        if dlist[0] == 'on':
            odata = OverSeas.query.filter(OverSeas.PuDate > stopdate).all()
        if dlist[1] == 'on':
            adata = Autos.query.filter(Autos.Date1 > stopdate).all()
        if dlist[2] == 'on':
            bdata = Bookings.query.filter(Bookings.PortCut > stopdate).all()
        if dlist[4] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '3':
        stopdate = today-datetime.timedelta(days=27)
        if dlist[0] == 'on':
            odata = OverSeas.query.filter(OverSeas.PuDate > stopdate).all()
        if dlist[1] == 'on':
            adata = Autos.query.filter(Autos.Date1 > stopdate).all()
        if dlist[2] == 'on':
            bdata = Bookings.query.filter(Bookings.PortCut > stopdate).all()
        if dlist[4] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    else:
        if dlist[0] == 'on':
            odata = OverSeas.query.all()
        if dlist[1] == 'on':
            adata = Autos.query.all()
        if dlist[2] == 'on':
            bdata = Bookings.query.all()
        if dlist[4] == 'on':
            idata = Interchange.query.all()
    return odata, adata, bdata, pdata, idata


def isoO():

    from viewfuncs import erud

    if request.method == 'POST':
        from viewfuncs import init_ocean_zero, nonone, nononef
        from invoice_mimemail import invoice_mimemail
        from vin import getvindata
        from invoice_makers import multi_inv
        ship, book, auto, peep, comm, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_ocean_zero()
        username = session['username'].capitalize()
        filesel = ''
        docref = ''
        doctxt = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        addA = None
        modal = 0
        tick = 0
        redir = 'stay'
        err = ['All is well', ' ']

# ____________________________________________________________________________________________________________________B.FormVariables.Overseas
        leftsize = 10
        newc = 'In the post'

        my_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
        today = my_datetime.date()
        now = my_datetime.time()

        match = request.values.get('Match')
        unmatch = request.values.get('UnMatch')
        modify = request.values.get('Modify')
        vmod = request.values.get('Vmod')
        minvo = request.values.get('MakeI')
        viewo = request.values.get('ViewO')
        viewi = request.values.get('ViewI')
        dockr = request.values.get('Dockr')
        dockupdate = request.values.get('DockUp')
        viewd = request.values.get('ViewD')
        addE = request.values.get('addentity')
        addC = request.values.get('addcommo')
        copy = request.values.get('copy')
        slim = request.values.get('Slim')
        stayslim = request.values.get('stayslim')
        keepship = request.values.get('keepship')
        release = request.values.get('Release')
        onway = request.values.get('Onway')
        rtog = request.values.get('Rtog')
        thismuch = request.values.get('thismuch')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        datatable1 = request.values.get('datatable1')
        datatable2 = request.values.get('datatable2')
        datatable3 = request.values.get('datatable3')
        datatable4 = request.values.get('datatable4')
        datatable5 = request.values.get('datatable5')
        dlist = [datatable1, datatable2, datatable3, datatable4, datatable5]

        # hidden values
        update = request.values.get('Update')
        invoupdate = request.values.get('invoUpdate')
        modlink = request.values.get('passmodlink')
        emailnow = request.values.get('emailnow')
        emailnow2 = request.values.get('emailnow2')
        emailinvo2 = request.values.get('emailInvo2')
        emailinvo = request.values.get('emailInvo')
        efile = request.values.get('Efile')
        newjob = request.values.get('NewJ')
        thisjob = request.values.get('ThisJob')
        recpay = request.values.get('RecPay')
        hispay = request.values.get('HisPay')
        recupdate = request.values.get('recUpdate')
        unpay = request.values.get('UnPay')
        uninv = request.values.get('UnInv')
        acceptthese = request.values.get('accept')
        payview = request.values.get('payview')

        calendar = request.values.get('Calendar')
        calupdate = request.values.get('calupdate')
        incoming_O = request.values.get('incoming_O')
        ondock = 0

        ship = request.values.get('ship')
        book = request.values.get('book')
        peep = request.values.get('peep')
        auto = request.values.get('auto')
        tick = request.values.get('tick')

        invo = request.values.get('invo')
        invooder = request.values.get('invooder')
        cache = request.values.get('cache')

        modata = 0
        leftscreen = 1
        doctxt = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        docref = ''
        ldata = None

        modlink = nonone(modlink)
        ship = nonone(ship)
        book = nonone(book)
        peep = nonone(peep)
        auto = nonone(auto)
        keepship = nonone(keepship)
        tick = nonone(tick)

        invo = nonone(invo)
        invooder = nonone(invooder)
        cache = nonone(cache)
        stayslim = nonone(stayslim)

        thisbox = request.values.get('addbox')
        if thisbox == '1':
            newjob = 1
        if thisbox == '2':
            addE = 1
        if thisbox == '3':
            addA = 1
        if thisbox == '4':
            copy = 1
        if thisbox == '5':
            dockr = 1
        if thisbox == '6':
            uploadS = 1
        if thisbox =='7':
            uploadP = 1

        thisbox = request.values.get('editbox')
        if thisbox == '1':
            vmod = 1
        if thisbox == '2':
            match = 1
        if thisbox == '3':
            acceptthese = 1
        if thisbox == '4':
            loadc = 1

        thisbox = request.values.get('invobox')
        if thisbox == '1':
            minvo = 1
        if thisbox == '2':
            mquot = 1
        if thisbox == '3':
            mpack = 1

        thisbox = request.values.get('xbox')
        if thisbox == '1':
            deletehit = 1
        if thisbox == '2':
            uninv = 1
        if thisbox == '3':
            unpay = 1

        if returnhit is not None:
            modlink = 0
            invo = 0
            invooder = 0

        if incoming_O is not None:

            odata = OverSeas.query.all()
            billvec = numcheckvec(odata, 'ship')
            beprob = 0
            comvec = []
            for bill in billvec:
                bill = nonone(bill)
                odat = OverSeas.query.get(bill)
                company = odat.FrFor
                comvec.append(company)
                cdat = People.query.get(odat.FrForID)
                if cdat is None:
                    beprob = beprob+1
            # Check to Make Sure we Have a FrFor to Bill
            comck = comvec[0]
            for com in comvec:
                if com != comck:
                    beprob = beprob+1

            if beprob > 0:
                err[0] = 'No Freight Fwd Recorded'
                err[1] = 'or FrFwd not Same on All'
            else:

                total = 0.00
                nbill = len(billvec)
                if nbill > 1:
                    pstamp = 'Paid-M'
                else:
                    pstamp = 'Paid'
                jobvec = []
                for bill in billvec:
                    bill = nonone(bill)
                    odat = OverSeas.query.get(bill)
                    jobvec.append(odat.Jo)
                    bdesc = odat.Booking
                    newstatus = stat_update(odat.Status, '3', 2)
                    if newstatus == '833':
                        newstatus = '999'
                    odat.Status = newstatus
                    company = odat.FrFor
                    cdat = People.query.get(odat.FrForID)
                    btype = 'JobSp'
                    bcat = 'Container'
                    jobcat = 'Overseas'
                    if cdat is not None:
                        cdat.Associate1 = 'JobSp'
                        cdat.Associate2 = 'Ocean Container'
                        db.session.commit()
                    # Create the new database entry(s) for the source document
                    billno = odat.Jo
                    if nbill == 1:
                        ckmemo = 'For booking '+odat.Booking
                    else:
                        ckmemo = odat.Booking
                    bamt = odat.Estimate
                    bcomp = request.values.get('bcomp')
                    bref = ''
                    cco = cdata[10]
                    account = cdata[9]
                    baccount = 'Containers/Overseas Shipments'
                    try:
                        bamt = float(bamt)
                        total = total+bamt
                    except:
                        bamt = 0.00
                    db.session.commit()

                    input = Bills(Jo=billno, Pid=cdat.id, Company=company, Memo=ckmemo, Description=bdesc, bAmount=bamt, Status=pstamp, Cache=0, Original='',
                                     Ref=bref, bDate=today, pDate=today, pAmount=bamt, pMulti=None, pAccount=account, bType=btype, bAccount=baccount,
                                     bCat=bcat, bSubcat=None, Link=None, User=username, Co='F', Temp1=jobcat, Temp2=str(bill), Recurring=0, dDate=today, pAmount2='0.00', pDate2=None,
                                     Code1 = None, Code2=None, CkCache=0, QBi=0, iflag = 0, PmtList=None,
                             PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None)

                    db.session.add(input)
                    db.session.commit()

                masterjo = jobvec[0]
                myb = Bills.query.filter(Bills.Jo == masterjo).first()
                masterref = myb.Ref
                masteracct = myb.pAccount
                masterdesc = ''
                masterpid = myb.Pid
                masterpayee = myb.Company
                masterbacct = myb.bAccount
                if masteracct is None or len(masteracct) < 4:
                    masteracct = 'Industrial Bank'

                linkcode = 'Link'
                for thisjo in jobvec:
                    myb = Bills.query.filter(Bills.Jo == thisjo).first()
                    bill = myb.id
                    linkcode = linkcode+'+'+str(bill)

                    try:
                        descline = thisjo + ' ' + myb.Memo + ' ' + d2s(str(myb.bAmount)) + '\n'
                    except:
                        descline = thisjo
                    masterdesc = masterdesc+descline

                for thisjo in jobvec:
                    myb = Bills.query.filter(Bills.Jo == thisjo).order_by(
                        Bills.pAmount).first()
                    myb.Status = pstamp
                    myb.Link = linkcode
                    myb.pDate = today
                    myb.pAmount = myb.bAmount
                    myb.pMulti = "{:.2f}".format(total)
                    myb.Ref = masterref
                    myb.pAccount = masteracct
                    myb.Description = masterdesc
                    myb.Pid = masterpid
                    myb.Company = masterpayee
                    myb.bAccount = masterbacct
                    db.session.commit()
                redir = masterjo

        if slim is not None:
            if stayslim == 0:
                stayslim = 1
            else:
                stayslim = 0


# ____________________________________________________________________________________________________________________E.FormVariables.Overseas
# ____________________________________________________________________________________________________________________B.DataModifications.Overseas
        if update is not None and modlink == 80:
            vintoget = request.values.get('vintoget')
            vinoutput = getvindata(vintoget)
            print(vinoutput)
            modlink = 0


        if update is not None and modlink == 2:
            modata = People.query.get(peep)
            vals = ['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3',
                    'idtype', 'tid', 'tel', 'email', 'assoc1', 'assoc2', 'date1', 'ptype']
            a = list(range(len(vals)))
            i = 0
            for v in vals:
                a[i] = request.values.get(v)
                i = i+1
            input = People(Company=a[0], First=a[1], Middle=a[2], Last=a[3], Addr1=a[4], Addr2=a[5], Addr3=a[6], Idtype=a[7], Idnumber=a[8],
                           Telephone=a[9], Email=a[10], Associate1=a[11], Associate2=a[12], Date1=a[13], Ptype=a[14], Date2=None, Original=None, Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            err = ['New Entity Added to Database', ' ']
            modlink = 0

        if update is not None and modlink == 1:
            if ship > 0:
                modata = OverSeas.query.get(ship)
                vals = ['movetype', 'direction', 'commodity', 'pod', 'pol', 'origin', 'pudate', 'ctype', 'booking', 'commolist', 'estimate',
                        'charge', 'billto', 'exporter', 'consignee', 'notify', 'frfor', 'precarry', 'container', 'driver', 'seal', 'description', 'retdate']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.MoveType = a[0]
                modata.Direction = a[1]
                modata.Commodity = a[2]
                modata.Pod = a[3]
                modata.Pol = a[4]
                modata.Origin = a[5]
                modata.PuDate = a[6]
                modata.RetDate = a[22]
                modata.ContainerType = a[7]
                modata.Booking = a[8]
                modata.Estimate = a[10]
                modata.Charge = a[11]

                status = modata.Status
                if status == '777':
                    modata.Status = '000'

                cid1 = a[12]
                cid1 = nonone(cid1)
                modata.Pid = cid1
                pdat = People.query.get(cid1)
                modata.BillTo = pdat.Company

                cid2 = a[13]
                cid2 = nonone(cid2)
                modata.ExportID = cid2
                pdat = People.query.get(cid2)
                modata.Exporter = pdat.Company

                cid3 = a[14]
                cid3 = nonone(cid3)
                modata.ConsigID = cid3
                pdat = People.query.get(cid3)
                modata.Consignee = pdat.Company

                cid4 = a[15]
                cid4 = nonone(cid4)
                modata.NotifyID = cid4
                pdat = People.query.get(cid4)
                modata.Notify = pdat.Company

                cid5 = a[16]
                cid5 = nonone(cid5)
                modata.FrForID = cid5
                pdat = People.query.get(cid5)
                modata.FrFor = pdat.Company

                cid6 = a[17]
                cid6 = nonone(cid6)
                modata.PreCarryID = cid6
                pdat = People.query.get(cid6)
                modata.PreCarry = pdat.Company

                modata.Container = a[18]
                modata.Driver = a[19]
                modata.Seal = a[20]
                modata.Description = a[21]
                modata.Label = modata.Jo+' '+a[8]+modata.Charge
                db.session.commit()
                err = ['Modification to Shipping JO ' + modata.Jo + ' completed.', ' ']
                modlink = 0

            if book > 0:
                modata = Bookings.query.get(book)
                vals = ['booking', 'exportref', 'vessel', 'portcut', 'doccut', 'saildate',
                        'estarr', 'reltype', 'aes', 'amount', 'load', 'dest', 'joborder', 'shipline']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.Booking = a[0]
                modata.Jo = a[12]
                modata.ExportRef = a[1]
                modata.Vessel = a[2]
                modata.Line = a[13]
                modata.PortCut = a[3]
                modata.DocCut = a[4]
                modata.SailDate = a[5]
                modata.EstArr = a[6]
                modata.RelType = a[7]
                modata.AES = a[8]
                modata.Amount = a[9]
                modata.LoadPort = a[10]
                modata.Dest = a[11]
                status = modata.Status
                if status == 'New':
                    modata.Status = 'Unmatched'

                db.session.commit()
                err = ['Modification to Booking ' + modata.Booking + ' completed.', ' ']
                modlink = 0

            if peep > 0:
                modata = People.query.get(peep)
                vals = ['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3',
                        'idtype', 'tid', 'tel', 'email', 'assoc1', 'assoc2', 'date1', 'ptype']
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
                modata.Ptype = a[14]
                status = modata.Temp2
                if status == 'New':
                    modata.Temp2 = ''
                db.session.commit()
                err = ['Modification to Entity ID ' + str(modata.id) + ' completed.', ' ']
                modlink = 0

            if auto > 0:
                modata = Autos.query.get(auto)
                vals = ['modelyear', 'make', 'model', 'color', 'vin', 'title', 'state', 'empweight', 'dispatched', 'owner',
                        'towcompany', 'towcost', 'delto', 'orderid', 'newtowcompany', 'towcostea', 'pufrom', 'cvalue', 'ncars']
                a = list(range(len(vals)))
                for i, v in enumerate(vals):
                    a[i] = request.values.get(v)
                modata.Year = a[0]
                modata.Make = a[1]
                modata.Model = a[2]
                modata.Color = a[3]
                modata.VIN = a[4]
                modata.Title = a[5]
                modata.State = a[6]

                modata.EmpWeight = a[7]
                modata.Dispatched = a[8]
                modata.Owner = a[9]

                company = a[10]
                if company == '1':
                    modata.TowCompany = a[14]
                    input = People(Company=a[14], First='', Middle='', Last='', Addr1='', Addr2='', Addr3='', Idtype='', Idnumber='', Telephone='',
                                   Email='', Associate1='', Associate2='', Date1=today, Date2=None, Original='', Ptype='TowCo', Temp1='', Temp2='', Accountid='')
                    db.session.add(input)
                    modata.TowCompany = a[14]
                else:
                    modata.TowCompany = company

                modata.TowCost = d2s(a[11])
                modata.Delto = a[12]
                modata.Pufrom = a[16]
                modata.Value = d2s(a[17])
                ncars = a[18]
                try:
                    ncars = int(a[18])
                    towcost = float(d2s(a[11]))
                    towcostea = towcost/float(ncars)
                    towcostea = str(towcostea)
                    towcostea = d2s(towcostea)
                    modata.TowCostEa = towcostea
                except:
                    modata.TowCostEa = a[15]
                    ncars = 0
                modata.Ncars = ncars
                sdate1 = request.values.get('date1')
                try:
                    sdate1dt = datetime.datetime.strptime(sdate1, "%Y-%m-%d")
                except:
                    sdate1 = today.strftime('%Y-%m-%d')

                sdate2 = request.values.get('date2')
                try:
                    sdate2dt = datetime.datetime.strptime(sdate2, "%Y-%m-%d")
                except:
                    sdate2 = today.strftime('%Y-%m-%d')
                modata.Date1 = sdate1
                modata.Date2 = sdate2
                modata.Orderid = a[13]
                modata.Status = 'Novo'

                db.session.commit()
                err = [' ', ' ', 'Modification to Auto Data ' +
                       str(modata.id) + ' completed.', ' ',  ' ']
                modlink = 0

            if tick > 0:
                modata = Interchange.query.get(tick)
                vals = ['intcontainer', 'intdate', 'inttime', 'chassis',
                        'release', 'truck', 'grosswt', 'driver', 'type']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.Container = a[0]
                modata.Date = a[1]
                modata.Time = a[2]
                modata.Chassis = a[3]
                modata.Release = a[4]
                modata.TruckNumber = a[5]
                modata.GrossWt = a[6]
                modata.Driver = a[7]
                modata.Type = a[8]
                status = modata.Status
                if status == 'AAAAAA':
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
                Check_Sailing()

# ____________________________________________________________________________________________________________________E.DataModifications.Overseas
# ____________________________________________________________________________________________________________________B.InvoiceUpdate.Overseas

        if invoupdate is not None:
            leftsize = 8
            odata1 = OverSeas.query.get(invooder)
            invodate = request.values.get('invodate')
            if invodate is None:
                invodate = today

            ldata = Invoices.query.filter(Invoices.Jo == odata1.Jo).all()
            total = 0.0
            for data in ldata:
                try:
                    iqty = request.values.get('qty'+str(data.id))
                    iqty = nononef(iqty)
                except:
                    iqty = 1.0

                if iqty == 0:
                    try:
                        autoid = nonone(data.SubJo)
                        adat = Autos.query.get(autoid)
                        adat.TowCost = 'NoTow'
                        db.session.commit()
                    except:
                        err[0] = 'error'
                data.Description = request.values.get('desc'+str(data.id))
                deach = request.values.get('cost'+str(data.id))
                if deach is not None:
                    deach = "{:.2f}".format(float(deach))
                else:
                    deach = "{:.2f}".format(0.00)
                data.Qty = iqty
                data.Ea = deach
                amount = float(iqty)*float(deach)
                total = total+amount
                data.Amount = d2s(amount)
                data.Date = invodate
                db.session.commit()
            # Remove zeros from invoice in case a zero was the mod
            Invoices.query.filter(Invoices.Qty == 0).delete()
            db.session.commit()
            # Create invoice code for order
            err = ['Invoice created for JO: '+odata1.Jo, ' ']
            # ldata=Invoices.query.filter(Invoices.Jo==odata1.Jo).all()
            # for data in ldata:
            # data.Total=d2s(total)
            # db.session.commit()
            #odata1.Itotal="%0.2f" % total
            odata1.Status = stat_update(odata1.Status, '1', 1)
            db.session.commit()
# ____________________________________________________________________________________________________________________E.InvoiceUpdate.Overseas
# ____________________________________________________________________________________________________________________B.SetBaseData.Overseas
        odata, adata, bdata, pdata, idata = dataget_O(thismuch, dlist)
# ____________________________________________________________________________________________________________________E.SetBaseData.Overseas

# ____________________________________________________________________________________________________________________B.Numcheck.Overseas
        if dockupdate is None and efile is None:
            ship, auto, book, peep, tick, numchecked = numcheck(5, odata, adata, bdata, pdata, idata, [
                                                                'ship', 'auto', 'book', 'peep', 'tick'])
# ____________________________________________________________________________________________________________________E.Numcheck.Overseas
        if release is not None:
            err[0] = 'Must check job to be released'
            if ship > 0:
                odat = OverSeas.query.get(ship)
                status = odat.Status
                booking = odat.Booking
                newstatus = stat_update(status, '8', 0)
                if newstatus == '833':
                    newstatus = '999'
                odat.Status = newstatus
                db.session.commit()
                err[0] = 'Booking '+booking+' released'

        if onway is not None:
            err[0] = 'Must check job to assign'
            if ship > 0:
                odat = OverSeas.query.get(ship)
                status = odat.Status
                newstatus = stat_update(status, '3', 0)
                odat.Status = newstatus
                db.session.commit()
                err[0] = 'Job updated to shipped'

# ____________________________________________________________________________________________________________________B.Views.Overseas

        if (viewo is not None or viewi is not None or viewd is not None) and numchecked == 1:
            err = ['No document is available', ' ']

            if ship > 0 and viewd is not None:
                modata = OverSeas.query.get(ship)
                if modata.Dpath is not None:
                    docref = f'tmp/{scac}/data/vdockr/' + modata.Dpath

            if ship > 0 and viewi is not None:
                modata = OverSeas.query.get(ship)
                if modata.Ipath is not None:
                    docref = modata.Ipath
                    if 'data' not in docref:
                        docref = docref.replace('tmp/', f'tmp/{scac}/data/')

            if ship > 0 and viewo is not None:
                modata = OverSeas.query.get(ship)
                if modata.Apath is not None:
                    docref = modata.Apath
                    if 'data' not in docref:
                        docref = docref.replace('tmp/', f'tmp/{scac}/data/')

            if book > 0:
                modata = Bookings.query.get(book)
                if modata.Original is not None:
                    docref = f'tmp/{scac}/data/vbookings/' + modata.Original

            if auto > 0:
                modata = Autos.query.get(auto)
                if modata.Original is not None:
                    docref = modata.Original
                    if 'data' not in docref:
                        docref = docref.replace('tmp/', f'tmp/{scac}/data/')

            if tick > 0:
                modata = Interchange.query.get(tick)
                if modata.Original is not None:
                    docref = f'tmp/{scac}/data/vinterchange/' + modata.Original

            if (auto > 0 or book > 0 or ship > 0 or tick > 0) and docref:
                if len(docref) > 5:
                    leftscreen = 0
                    leftsize = 8
                    modlink = 0
                    err = ['All is well', ' ']

        if (viewo is not None or viewi is not None or viewd is not None) and numchecked != 1:
            err = ['Must check one box.', ' ']

        if (modify is not None or vmod is not None) and numchecked == 1:
            modlink = 1
            leftsize = 8
            if ship > 0:
                modata = OverSeas.query.get(ship)
                if vmod is not None:
                    err = ['No document is available', ' ']
                    if modata.Dpath is not None:
                        if len(modata.Dpath) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vdockr/' + modata.Dpath
                            err = ['All is well', ' ']

            if book > 0:
                modata = Bookings.query.get(book)
                if vmod is not None:
                    err = ['No document is available', ' ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vbookings/' + modata.Original
                            err = ['All is well', ' ']
            if peep > 0:
                modata = People.query.get(peep)
                if vmod is not None:
                    err = ['There is no document available', '  ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vpersons/' + modata.Original
                            err = ['All is well', ' ']
            if auto > 0:
                modata = Autos.query.get(auto)
                if vmod is not None:
                    err = ['There is no document available', '  ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = modata.Original
                            err = ['All is well', ' ']

            if tick > 0:
                modata = Interchange.query.get(tick)
                if vmod is not None:
                    err = ['There is no document available', '  ']
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vinterchange/' + modata.Original
                            err = ['All is well', ' ']
            doctxt = docref.split('.', 1)[0]+'.txt'

# ____________________________________________________________________________________________________________________E.Views.Overseas
# ____________________________________________________________________________________________________________________B.AddItems.Overseas

        if (modify is not None or vmod is not None) and numchecked != 1:
            modlink = 0
            err[1] = ' '
            err[0] = 'Must check one box'

        if addE is not None and numchecked == 0:
            leftsize = 8
            modlink = 1
            # We will create a blank line and simply modify that by updating:
            input = People(Company='New', First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None, Idtype=None, Idnumber=None, Telephone=None,
                           Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='Overseas', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter((People.Company == 'New') &
                                         (People.Ptype == 'Overseas')).first()
            peep = modata.id
            err = ['Enter Data for New Company', ' ']

        if addA is not None and numchecked == 0:
            leftsize = 8
            modlink = 80


        if addE is not None and numchecked > 1:
            modlink = 0
            err[0] = ' '
            err[1] = 'Must check one box'

        if addE is not None and peep > 0 and numchecked == 1:
            modlink = 2
            modata = People.query.get(peep)

        if addE is not None and numchecked > 1:
            modlink = 0
            err[1] = ' '
            err[0] = 'Must check no/one box'

# ____________________________________________________________________________________________________________________E.AddItems.Overseas
# ____________________________________________________________________________________________________________________B.Email.Overseas

        if emailnow is not None or emailnow2 is not None:
            stamp = 1
            leftscreen = 1
            leftsize = 10
            modlink = 0
            odata1 = OverSeas.query.get(invooder)
            jo = odata1.Jo
            docref = odata1.Ipath
            booking = odata1.Booking

            # If ready to email then we want a permanent copy and get rid of old:
            odata1.Status = stat_update(odata1.Status, '2', 1)
            db.session.commit()

            emailin1 = invoice_mimemail(jo, booking, docref, 5)
            invo = 0
            invooder = 0
            err[1] = 'Successful email to: ' + emailin1

        if efile is not None:
            stamp = 1
            leftscreen = 1
            leftsize = 10
            modlink = 0
            odata1 = OverSeas.query.get(ship)
            pdat = People.query.get(odata1.FrForID)
            if pdat is None:
                emailin = 'export@firsteaglelogistics.com'
            else:
                emailin = str(pdat.Email)

            from mailfiles import mail_efile
            mail_efile(odata1, emailin)
            err[0] = 'Successful email to: ' + emailin

        if emailinvo is not None or emailinvo2 is not None:
            leftsize = 10
            leftscreen = 1
            modlink = 0
            modata = OverSeas.query.get(invooder)
            ldata = Invoices.query.filter(
                Invoices.Jo == modata.Jo).order_by(Invoices.Ea.desc()).all()
            jo = modata.Jo
            booking = modata.Booking
            docref = modata.Ipath
            emailin1 = invoice_mimemail(jo, booking, docref, 5)
            err[1] = 'Successful email to: '+emailin1
            modata.Status = stat_update(modata.Status, '2', 1)
            db.session.commit()
            invo = 0
            invooder = 0
# ____________________________________________________________________________________________________________________E.Email.Trucking

# ____________________________________________________________________________________________________________________B.DockReceipt.Overseas

        if (dockr is not None and numchecked == 1 and ship > 0) or dockupdate is not None:
            modata = OverSeas.query.get(ship)
            cache = nonone(modata.Cache)+1
            ondock = 1
            if dockr is not None:
                fs = 12
                itt = ' '
                modata.CommoList = fs
                modata.itt = itt
                db.session.commit()
            else:
                fs = request.values.get('thisfont')
                fs = nonone(fs)
                itt = request.values.get('itt')
                vals = ['commodity', 'exporter', 'consignee', 'notify', 'frfor',
                        'seal', 'description', 'reltype', 'aes', 'expref', 'addnote']
                a = list(range(len(vals)))
                for i, v in enumerate(vals):
                    a[i] = request.values.get(v)

                modata.Commodity = a[0]

                cid = a[1]
                cid = nonone(cid)
                modata.ExportID = cid
                pdat = People.query.get(cid)
                modata.Exporter = pdat.Company

                cid = a[2]
                cid = nonone(cid)
                modata.ConsigID = cid
                pdat = People.query.get(cid)
                modata.Consignee = pdat.Company

                cid = a[3]
                cid = nonone(cid)
                modata.NotifyID = cid
                pdat = People.query.get(cid)
                modata.Notify = pdat.Company

                cid = a[4]
                cid = nonone(cid)
                modata.FrForID = cid
                pdat = People.query.get(cid)
                modata.FrFor = pdat.Company

                modata.Seal = a[5]
                modata.Description = a[6]
                modata.RelType = a[7]
                modata.AES = a[8]
                modata.ExpRef = a[9]
                modata.AddNote = a[10]

                modata.CommoList = fs
                modata.Tpath = itt

                db.session.commit()

            a = modata.Commodity
            if a == 'HHG':
                hscode = '9403.50.000'
            elif a == 'AutoParts':
                hscode = '8412.80.9000'
            elif a == 'ATV':
                hscode = '8711.90.0100'
            elif a == 'Medical':
                hscode = '9018.90.8000'
            else:
                hscode = '8703.90.0100'

            bdata = Bookings.query.filter(Bookings.Jo == modata.Jo).first()
            if bdata is not None:
                # pdata1=People.query.filter(People.Company==odata.BillTo).first()
                pdata1 = People.query.get(modata.ExportID)
                pdata2 = People.query.get(modata.ConsigID)
                pdata3 = People.query.get(modata.NotifyID)
                pdata5 = People.query.get(modata.FrForID)
                pdata4 = People.query.get(modata.PreCarryID)
                adata = Autos.query.filter(Autos.Jo == modata.Jo).all()
                err = ['Dock Receipt Creation Selected', ' ']

                newfile = 'DR'+bdata.Booking+'c'+str(cache)+'.pdf'
                docref = f'tmp/{scac}/data/vdockr/'+newfile
                absfile = addpath(docref)
                modata.Dpath = newfile
                modata.Cache = cache
                db.session.commit()

                dockm(modata, bdata, adata, pdata1, pdata2, pdata3,
                      pdata4, pdata5, absfile, fs, hscode, itt)

                leftscreen = 0
                leftsize = 8
                modlink = 0
                err = ['All is well', ' ']
            else:
                err = ['No Booking Matched to Job', ' ']
                modlink = 0
                ondock = 0

        if dockr is not None and (numchecked != 1 or ship == 0):
            err = ['Must check one Shipping Job', ' ']
# ____________________________________________________________________________________________________________________E.DockReceipt.Overseas
# ____________________________________________________________________________________________________________________B.Delete.Overseas

        if deletehit is not None and numchecked == 1:
            if ship > 0:
                odat = OverSeas.query.get(ship)
                killjo = odat.Jo
                OverSeas.query.filter(OverSeas.id == ship).delete()
                Invoices.query.filter(Invoices.Jo == killjo).delete()
                Income.query.filter(Income.Jo == killjo).delete()
            if book > 0:
                Bookings.query.filter(Bookings.id == book).delete()
            if peep > 0:
                People.query.filter(People.id == peep).delete()
            if auto > 0:
                Autos.query.filter(Autos.id == auto).delete()
            if tick > 0:
                Interchange.query.filter(Interchange.id == tick).delete()
            db.session.commit()

        if deletehit is not None and numchecked != 1:
            err = ['Must check one item', ' ']
# ____________________________________________________________________________________________________________________E.Delete.Overseas
# ____________________________________________________________________________________________________________________B.ReceivePayment.Overseas

        if (recpay is not None and ship > 0 and numchecked == 1) or recupdate is not None:
            leftsize = 8
            if recpay is not None:
                invooder = ship
            odat = OverSeas.query.get(invooder)

            invojo = odat.Jo
            ldat = Invoices.query.filter(Invoices.Jo == invojo).first()
            err = ['Have no Invoice to Receive Against', ' ']
            if ldat is not None:
                newstatus = stat_update(odat.Status, '3', 1)
                if newstatus == '833':
                    newstatus = '999'
                odat.Status = newstatus
                db.session.commit()

                idate = ldat.Date
                if ldat.Original is not None:
                    docref = ldat.Original
                    leftscreen = 0
                    leftsize = 8

                incdat = Income.query.filter(Income.Jo == invojo).first()
                if incdat is None:
                    err = ['Creating New Payment on Jo', ' ']
                    paydesc = 'Receive payment on Invoice ' + invojo
                    recamount = str(ldat.Total)
                    custref = 'ChkNo'
                    recdate = today
                    input = Income(Jo=odat.Jo, SubJo=None, Pid=odat.Pid, Description=paydesc,
                                   Amount=recamount, Ref=custref, Date=recdate, Original=None)
                    db.session.add(input)
                    payment = 0
                else:
                    recamount = request.values.get('recamount')
                    custref = request.values.get('custref')
                    desc = request.values.get('desc')
                    recdate = request.values.get('recdate')
                    incdat.Amount = recamount
                    incdat.Ref = custref
                    incdat.Description = desc
                    incdat.Date = recdate
                db.session.commit()
                payment = [recamount, custref, recdate]

                modata = Income.query.filter(Income.Jo == invojo).first()
                inco = modata.id
                err = ['Amend Payment for Invoice', ' ']

                ldata = Invoices.query.filter(
                    Invoices.Jo == invojo).order_by(Invoices.Ea.desc()).all()
                pdata1 = People.query.filter(People.id == odat.Pid).first()
                cache = nonone(odat.Cache)+1

                from invoices import invoiceO
                invo, err, leftscreen, leftsize, docref, invodate = invoiceO(invooder, payment)

                if cache > 1:
                    docref = f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                    # Store for future use
                else:
                    docref = f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'

                odat.Cache = cache
                idat = Invoices.query.filter(Invoices.Jo == invojo).first()
                idat.Original = docref
                db.session.commit()
                leftscreen = 0
                err[0] = 'Viewing '+docref

        if recpay is not None and (ship == 0 or numchecked != 1):
            err = ['Invalid selections:', '']
            if ship == 0:
                err[1] = 'Must select an Overseas Job'
            if numchecked != 1:
                err[1] = 'Must select one Overseas Job'
# ____________________________________________________________________________________________________________________E.Receive Payment.Overseas
# ____________________________________________________________________________________________________________________B.Payment History.Overseas
        if hispay is not None or modlink == 7:
            if ship == 0 and invooder == 0:
                err[1] = 'Must select an Overseas Job'
            else:
                if ship != 0:
                    invooder = ship
                modata = OverSeas.query.get(invooder)
                ldata0 = Invoices.query.filter(Invoices.Jo == modata.Jo).order_by(Invoices.Jo).all()
                ldata1 = Income.query.filter(Income.Jo == modata.Jo).order_by(Income.Jo).all()
                ldata2 = Bills.query.filter(Bills.Jo == modata.Jo).all()
                # Check to see if we need to delete anything from history
                killthis = request.values.get('killthis')
                if killthis is not None and modlink == 7:
                    for data in ldata0:
                        testone = request.values.get('invo'+str(data.id))
                        if testone:
                            kill = int(testone)
                            Invoices.query.filter(Invoices.id == kill).delete()
                            db.session.commit()
                    for data in ldata1:
                        testone = request.values.get('pay'+str(data.id))
                        if testone:
                            kill = int(testone)
                            Income.query.filter(Income.id == kill).delete()
                            db.session.commit()
                    for data in ldata2:
                        testone = request.values.get('bill'+str(data.id))
                        if testone:
                            kill = int(testone)
                            Bills.query.filter(Bills.id == kill).delete()
                            db.session.commit()
                    ldata0 = Invoices.query.filter(
                        Invoices.Jo == modata.Jo).order_by(Invoices.Jo).all()
                    ldata1 = Income.query.filter(Income.Jo == modata.Jo).order_by(Income.Jo).all()
                    ldata2 = Bills.query.filter(Bills.Jo == modata.Jo).all()

                ldata3 = 0.00
                for dat in ldata0:
                    amt = float(dat.Amount)
                    ldata3 = ldata3+amt
                ldata4 = 0.00
                for dat in ldata1:
                    amt = float(dat.Amount)
                    ldata4 = ldata4+amt
                ldata5 = 0.00
                for dat in ldata2:
                    amt = float(dat.bAmount)
                    ldata5 = ldata5+amt
                obal = ldata3-ldata4
                prof = ldata3-ldata5

                ldata = [ldata0, ldata1, ldata2, d2s(str(ldata3)), d2s(
                    str(ldata4)), d2s(str(ldata5)), d2s(str(obal)), d2s(str(prof))]

                leftsize = 8
                modlink = 7
# ____________________________________________________________________________________________________________________E.PaymentHistory.TOverseas


# ____________________________________________________________________________________________________________________B.Invoice.Overseas

        if (minvo is not None and ship > 0) or invoupdate is not None:
            err = ['Could not create invoice', ' ']
            # First time through: have an order to invoice
            if ship > 0:
                invooder = ship

            from invoices import invoiceO
            invo, err, leftscreen, leftsize, docref, invodate = invoiceO(invooder, 0)
            modata = OverSeas.query.get(invooder)
            jo = modata.Jo
            booking = modata.Booking
            ldata = Invoices.query.filter(Invoices.Jo == jo).order_by(Invoices.Jo).all()

            etitle = 'First Eagle Logistics Invoice: ' + jo + ' for Booking: ' + booking
            ebody = 'Dear Customer:\n\nYour invoice is attached. Please remit payment at your earliest convenience.\n\nThank you for your business- we appreciate it very much.\n\nSincerely,\n\nFIRST EAGLE LOGISTICS,INC.\n\n\nMark Nixon\nFirst Eagle Logistics, Inc.\n505 Hampton Park Blvd Unit O\nCapitol Heights,MD 20743\n301 516 3000'
            emails, passwds, ourserver = emailvals()
            try:
                pdat = People.query.get(modata.Pid)
                emailin1 = str(pdat.Email)
            except:
                emailin1 = emails[4]

            emailin2 = emails[4]
            emailcc1 = emails[0]
            emailcc2 = emails[1]
            emaildata = [emailin1, emailin2, emailcc1, emailcc2]

        elif minvo is not None:
            err = ['Must select a Job', ' ']
# ____________________________________________________________________________________________________________________E.Invoice.Overseas
# ____________________________________________________________________________________________________________________B.Newjob.Overseas
        if newjob is not None:
            err = ['Select Source Document from List', '']
            fdata = myoslist('data/vunknown')
            modlink = 4
            leftsize = 8
            leftscreen = 0
            docref = f'tmp/{scac}/data/vunknown/NewJob.pdf'

        if newjob is None and modlink == 4:
            filesel = request.values.get('FileSel')
            fdata = myoslist('data/vunknown')
            leftsize = 8
            leftscreen = 0
            try:
                docref = f'tmp/{scac}/data/vunknown/'+filesel
            except:
                err[0] = 'No File Found'

        if update is not None and modlink == 4:
            modlink = 0
            # Create the new database entry for the source document
            filesel = request.values.get('FileSel')
            if filesel != '1' and filesel is not None:
                docold = f'tmp/{scac}/data/vunknown/'+filesel
                docref = f'tmp/{scac}/data/vpersons/'+filesel
                # shutil.move(docold,docref)
            else:
                docref = ''

            sdate = request.values.get('dstart')
            if sdate is None:
                sdate = today.strftime('%Y-%m-%d')
            nextjo = newjo(jbcode, sdate)
            vals = ['movetype', 'direction', 'commodity', 'pod', 'pol', 'origin', 'pudate', 'ctype', 'booking', 'commolist', 'estimate',
                    'charge', 'billto', 'exporter', 'consignee', 'notify', 'frfor', 'precarry', 'container', 'driver', 'seal', 'description', 'retdate']
            a = list(range(len(vals)))
            for i, v in enumerate(vals):
                a[i] = request.values.get(v)

            cid1 = a[12]
            cid1 = nonone(cid1)
            pdat = People.query.get(cid1)
            billto = pdat.Company

            cid2 = a[13]
            cid2 = nonone(cid2)
            pdat = People.query.get(cid2)
            exporter = pdat.Company

            cid3 = a[14]
            cid3 = nonone(cid3)
            pdat = People.query.get(cid3)
            consignee = pdat.Company

            cid4 = a[15]
            cid4 = nonone(cid4)
            pdat = People.query.get(cid4)
            notify = pdat.Company

            cid5 = a[16]
            cid5 = nonone(cid5)
            pdat = People.query.get(cid5)
            frfor = pdat.Company

            cid6 = a[17]
            cid6 = nonone(cid6)
            pdat = People.query.get(cid6)
            precarry = pdat.Company

            label = nextjo+' '+a[8]

            sdate = a[6]
            if sdate is None:
                sdate = today.strftime('%Y-%m-%d')
            sdateret = a[22]
            if sdateret is None:
                sdateret = today.strftime('%Y-%m-%d')

            input = OverSeas(Jo=nextjo, Pid=cid1, MoveType=a[0], Direction=a[1], Commodity=a[2], Pod=a[3], Pol=a[4], Origin=a[5], PuDate=sdate, ContainerType=a[7],
                             Booking=a[8], CommoList=0, ExportID=cid2, ConsigID=cid3, NotifyID=cid4, FrForID=cid5, PreCarryID=cid6, Estimate=a[10], Charge=a[11], Container=a[18],
                             Dpath=None, Ipath=None, Apath=filesel, Cache=0, Status='000', Label=label, BillTo=billto, Exporter=exporter, Consignee=consignee, Notify=notify,
                             FrFor=frfor, PreCarry=precarry, Driver=a[19], Seal=a[20], Description=a[21], RetDate=sdateret, Tpath=None, Itotal='',
                             RelType='Seaway Bill', AES='', ExpRef='', AddNote='')

            db.session.add(input)
            db.session.commit()
            modata = OverSeas.query.filter(OverSeas.Jo == nextjo).first()
            ship = modata.id
            leftsize = 10
            leftscreen = 1
            err = ['All is well', ' ']
# ____________________________________________________________________________________________________________________E.Newjob.Overseas
        if copy is not None:

            if ship > 0 and numchecked == 1:
                sdate = today.strftime('%Y-%m-%d')
                nextjo = newjo(jbcode, sdate)
                mys = OverSeas.query.get(ship)
                input = OverSeas(Jo=nextjo, Pid=mys.Pid, MoveType=mys.MoveType, Direction=mys.Direction, Commodity=mys.Commodity, Pod=mys.Pod,
                                 Pol=mys.Pol, Origin=mys.Origin, PuDate=sdate, ContainerType=mys.ContainerType, Booking='', CommoList=0, ExportID=mys.ExportID,
                                 ConsigID=mys.ConsigID, NotifyID=mys.NotifyID, FrForID=mys.FrForID, PreCarryID=mys.PreCarryID, Estimate=mys.Estimate,
                                 Charge=mys.Charge, Container='TBD', Dpath=None, Ipath=None, Apath=None, Cache=0, Status='777', Label='', BillTo=mys.BillTo, Exporter=mys.Exporter,
                                 Consignee=mys.Consignee, Notify=mys.Notify, FrFor=mys.FrFor, PreCarry=mys.PreCarry, Driver='', Seal='', Description='', RetDate=sdate, Tpath='', Itotal='',
                                 RelType='Seaway Bill', AES='', ExpRef='', AddNote='')
                db.session.add(input)
                db.session.commit()

            if auto > 0 and numchecked == 1:
                mya = Autos.query.get(auto)
                input = Autos(Jo=None, Hjo=None, Year=mya.Year, Make=mya.Make, Model=mya.Model, Color=mya.Color, VIN='', Title='', State='', EmpWeight=mya.EmpWeight, Dispatched=None, Value=mya.Value,
                              TowCompany=mya.TowCompany, TowCost=mya.TowCost, TowCostEa=mya.TowCostEa, Original='', Status='New', Date1=today, Date2=today, Pufrom=None, Delto=None, Ncars=1, Orderid=mya.Orderid)
                db.session.add(input)
                db.session.commit()

            if book > 0 and numchecked == 1:
                myb = Bookings.query.get(book)
                input = Bookings(Jo=None, Booking='', ExportRef=myb.ExportRef, Line=myb.Line, Vessel=myb.Vessel, PortCut=myb.PortCut,
                                 DocCut=myb.DocCut, SailDate=myb.SailDate, EstArr=myb.EstArr,
                                 RelType=myb.RelType, AES=None, Original=None, Amount=myb.Amount,
                                 LoadPort=myb.LoadPort, Dest=myb.Dest, Status="New")
                db.session.add(input)
                db.session.commit()

            if peep > 0 and numchecked == 1:
                myp = People.query.get(peep)
                ptype = myp.Ptype
                if ptype == 'Overseas':
                    newptype = 'Overseas2'
                else:
                    newptype = 'Overseas'
                input = People(Company=myp.Company, First=myp.First, Middle=myp.Middle, Last=myp.Last, Addr1=myp.Addr1, Addr2=myp.Addr2, Addr3=myp.Addr3,
                               Idtype=myp.Idtype, Idnumber=myp.Idnumber, Telephone=myp.Telephone, Email=myp.Email, Associate1=myp.Associate1,
                               Associate2=myp.Associate2, Date1=today, Ptype=newptype, Date2=None, Original=None, Temp1=None, Temp2="New", Accountid=myp.Accountid)
                db.session.add(input)
                db.session.commit()

            if tick > 0 and numchecked == 1:
                myi = Interchange.query.get(tick)
                type = myi.Type
                if type == 'Load In':
                    newtype = 'Empty Out'
                if type == 'Empty Out':
                    newtype = 'Load In'
                if type == 'Empty In':
                    newtype = 'Load Out'
                if type == 'Load Out':
                    newtype = 'Empty In'

                input = Interchange(Container=myi.Container, TruckNumber=myi.TruckNumber, Driver=myi.Driver, Chassis=myi.Chassis,
                                    Date=myi.Date, Release=myi.Release, GrossWt=myi.GrossWt,
                                    Seals=myi.Seals, ConType=myi.ConType, CargoWt=myi.CargoWt,
                                    Time=myi.Time, Status='AAAAAA', Original=' ', Path=' ', Type=newtype, Jo=myi.Jo, Company=myi.Company, Other=None)
                db.session.add(input)
                db.session.commit()

            if numchecked < 2:
                err[1] = 'Must select 2 boxes or more.'
                err[0] = ' '

# ____________________________________________________________________________________________________________________E.Match.Overseas

# ____________________________________________________________________________________________________________________B.Match.Overseas

        if match is not None:

            if ship > 0 and book > 0 and numchecked == 2:
                mys = OverSeas.query.get(ship)
                myb = Bookings.query.get(book)
                mys.Booking = myb.Booking
                myb.Jo = mys.Jo
                myb.Status = 'Matched'
                db.session.commit()

            if ship > 0 and tick > 0 and numchecked == 2:
                myo = OverSeas.query.get(ship)
                myi = Interchange.query.get(tick)
                myo.Container = myi.Container
                myi.Company = myo.BillTo
                myi.Jo = myo.Jo
                db.session.commit()

            if numchecked < 2:
                err[0] = 'Must select 2 boxes or more.'
                err[1] = ' '

            if numchecked > 2:
                err[0] = 'Must check appropriate boxes'
                err[1] = ' '

            if ship > 0 and auto > 0 and numchecked > 1:
                mys = OverSeas.query.get(ship)

                for mya in adata:
                    testone = request.values.get('auto'+str(mya.id))
                    if testone:
                        mya.Jo = mys.Jo
                        mya.Status = 'Matched'
                        err[0] = 'Autos matched to Job'

                        # Update the tow cost each value
                        adat = Autos.query.filter(Autos.Orderid == mya.Orderid).all()
                        ncars = len(adat)
                        if ncars > 0:
                            try:
                                amt = mya.TowCost
                                amt = amt.replace('$', '').replace(',', '')
                                amt = float(amt)
                                amtea = amt/ncars
                                mya.TowCostEa = nodollar(amtea)
                            except:
                                amtea = 0.00

                        db.session.commit()
# ____________________________________________________________________________________________________________________E.Match.Overseas
# ____________________________________________________________________________________________________________________B.UnMatch.Overseas

        if unmatch is not None:

            if book > 0 and numchecked == 1:
                myb = Bookings.query.get(book)
                myb.Jo = 'TBD'
                myb.Status = 'Unmatched'
                db.session.commit()

            if auto > 0:
                for mya in adata:
                    testone = request.values.get('auto'+str(mya.id))
                    if testone:
                        mya.Jo = 'TBD'
                        mya.Status = 'Unmatched'

                        db.session.commit()

            if numchecked < 1:
                err[1] = 'Must select one box or more.'
                err[0] = ' '

# ____________________________________________________________________________________________________________________E.UnMatch.Overseas

        if uninv is not None:
            odat = OverSeas.query.get(ship)
            status = odat.Status
            newstatus = stat_update(status, '2', 1)
            odat.Status = newstatus
            idata = Invoices.query.filter(Invoices.Jo == odat.Jo).all()
            for data in idata:
                data.Status = 'New'
                db.session.commit()
            Income.query.filter(Income.Jo == odat.Jo).delete()
            db.session.commit()

        if unpay is not None:
            odata = OverSeas.query.all()
            billvec = numcheckvec(odata, 'ship')
            for bill in billvec:
                bill = nonone(bill)
                odat = OverSeas.query.get(bill)
                status = odat.Status
                newstatus = stat_update(status, '2', 2)
                odat.Status = newstatus
                Bills.query.filter(Bills.Jo == odat.Jo).delete()
                db.session.commit()

# ____________________________________________________________________________________________________________________B.Calendar.Overseas
        if calendar is not None or calupdate is not None:
            leftscreen = 2
            modal = 1
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

            caldays, daylist, weeksum = calendar7_weeks('Overseas', nweeks)

            if calupdate is not None:
                err = calmodalupdate(daylist, username, 'Overseas')
                caldays, daylist, weeksum = calendar7_weeks('Overseas', nweeks)
# ____________________________________________________________________________________________________________________E.Calendar.Overseas

        if slim is not None:
            if ship > 0 and numchecked == 1:
                keepship = ship
            else:
                err[0] = 'Must check one Overseas Job'
                stayslim = 0

        if stayslim > 0:
            odat = OverSeas.query.get(keepship)
            booking = odat.Booking
            if len(booking) < 3:
                booking = 'TBD'
            odata = OverSeas.query.filter(OverSeas.Booking == booking).all()
            adata = Autos.query.filter(Autos.Jo == odat.Jo).all()
            bdata = Bookings.query.filter(Bookings.Booking == booking).all()
            pdata = People.query.filter((People.id == odat.Pid) | (People.id == odat.ExportID) | (People.id == odat.ConsigID) | (
                People.id == odat.NotifyID) | (People.id == odat.FrForID) | (People.id == odat.PreCarryID)).all()
            idata = Interchange.query.filter(Interchange.Release == booking).all()
        else:
            odata, adata, bdata, pdata, idata = dataget_O(thismuch, dlist)

        alltdata = Drivers.query.all()
        tdata = Vehicles.query.all()

    # This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_ocean_zero, init_ocean_blank
        my_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
        today = my_datetime.date()
        now = my_datetime.time()
        now = now.strftime('%I:%M %p')
        leftscreen = 1
        redir = 'stay'
        ship, book, auto, peep, comm, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_ocean_zero()
        leftscreen = 1
        ldata = 0
        thismuch = '2'
        ondock = 0
        keepship = 0
        modal = 0
        tick = 0
        alltdata = 0
        tdata = 0
        dlist = ['off']*5
        dlist[0] = 'on'

        filesel = ''
        docref = ''
        doctxt = ''
        etitle = ''
        ebody = ''
        emaildata = ''
        leftsize = 10
        newc = 'Initial'
        err = ['All is well', ' ']

        #odata = OverSeas.query.all()
        odata, adata, bdata, pdata, idata = dataget_O(thismuch, dlist)
    leftsize = 9
    rightsize = 12-leftsize
    fdata = myoslist('data/vunknown')
    fdata.sort()
    sdata = Services.query.order_by(Services.Service).all()
    err = erud(err)

    return etitle, ebody, emaildata, thismuch, redir, odata, bdata, pdata, adata, idata, sdata, ship, keepship, book, auto, peep, tick, err, modata, caldays, daylist, nweeks, dlist, modlink, leftscreen, docref, stayslim, doctxt, leftsize, rightsize, ldata, invodate, inco, invo, invooder, cache, newc, alltdata, fdata, tdata, today, modal, ondock
