from runmain import app, db
from models import Vehicles, Invoices, JO, Income, Bills, Accounts, OverSeas, Orders, Gledger, Adjusting
from models import Autos, People, Interchange, Drivers, ChalkBoard, Services, Drops, Divisions, LastMessage
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import json
from CCC_system_setup import myoslist, addpath, addtxt, scac, companydata
from iso_B_worker import var_start, var_request, get_selections, cleanup, alterations, incoming_setup, modbill, \
    run_paybill, run_xfer, uploadsource, modpeeps, pay_init, multi_pay_init, install_pay_init, mod_init, newbill_init,\
    newbill_passthru, newbill_update, undolastpayment

compdata = companydata()
billexpcode = compdata[10]+'B'
billxfrcode = compdata[10]+'X'
print(billexpcode)

def isoB(indat):

    if request.method == 'POST':

        from viewfuncs import nonone, numcheck, newjo
        from viewfuncs import calendar7_weeks, txtfile, numcheckvec, d2s, erud, dataget_B, hv_capture, docuploader, get_def_bank
        from gledger_write import gledger_write, gledger_app_write

        # Initialize variables used in the python code that require a value
        username, bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist,\
        weeksum, nweeks, filesel, docref, doctxt, bType, bClass, expdata, addjobselect, jobdata, modal, viewck, acceptthese,\
        assdata, monlvec = var_start()

        divdat = Divisions.query.all()

        todaydt = datetime.datetime.today()
        today = todaydt.strftime('%Y-%m-%d')
        docref = ' '
        doctxt = ' '
        if indat == 'stay' or indat == 0: indat = '0'

        # Get all the variables appearing on the html page including button pushes
        match, vmod, modify2, viewo, addE, addE2, paybill, paybill2, unpay, printck, returnhit, deletehit, \
        update, modlink, newbill, thisbill, newxfer, thisxfer, calendar, calupdate, incoming, datatable1, \
        datatable2, copy, copy12, qpay, bill, cache, peep, uploadS, thismuch, vendmuch, thisbox0, thisbox1, thisbox2, \
        thisbox3, thisbox4, thisbox5, thisbox6 = var_request()

        modlink, bill, peep = nonone(modlink), nonone(bill), nonone(peep)
        dlist = [datatable1, datatable2]
        leftscreen = 0
        oid = 0

        # Get varibles that may be selected from the selection boxes and dont override the button pushes
        hv, newbill, addE, copy, copy12, UploadS, newxfer, vmod, match, acceptthese, qpay, paybill, paybill2, printck, \
        viewo, viewbill, viewck, deletehit, unpay, lbox, holdvec, err \
        = get_selections(thismuch, vendmuch, thisbox0, thisbox1, thisbox2, thisbox3, thisbox4, thisbox5, thisbox6,
                         newbill, vmod, paybill, printck)

        #Key variables may need to be altered based on the type of selection container in modlink:

        #modlink = 1 initial selection of an item to modify with update

        #modlink = 4 part of sequence in creating a new bill
        #modlink = 8 creating a new vendor during new bill process

        #modlink = 6 paying multiple bills with one check
        #modlink = 14 paying one bill with one check

        #after modification is started, if it is a bill and selection boxes are updated with onchange:
        #modlink = 7 modification to a bill for continuous modification until update button is used

        #modlink = 11 paying a bill
        #modlink = 12 quickpay (pay using default values)

        #modlink = 70 controls process of document uploading to establish a bill

        leftscreen = alterations(modlink, leftscreen)

        if returnhit is not None: modlink, leftscreen, indat = cleanup()
# ____________________________________________________________________________________________________________________B.QuickBillPayTowing
        if incoming is not None: incoming_setup()
# ____________________________________________________________________________________________________________________E.QuickBillPayTowing
# ____________________________________________________________________________________________________________________B.Uploading

        if modlink == 4 and (newbill is None and thisbill is None and update is None):
            modlink, err, bill, docref = uploadsource(modlink,err,oid,docref,username)

        if modlink == 70:
            err, oid = docuploader('bill')
            modlink = 0
# ____________________________________________________________________________________________________________________E.Uploading
# ____________________________________________________________________________________________________________________B.UpdateDatabasesSection
        if (update is not None and modlink == 1) or modlink == 8 or modlink == 7 or modlink == 6 or modlink == 11 or modlink == 12 or modlink == 14:
            success = 1
            if bill > 0:
                modata = Bills.query.get(bill)
                # if paying a bill there could be multiple link items to capture
                if modlink == 6:
                    try:
                        links = json.loads(modata.Link)
                    except:
                        links = 0
                    if links != 0:
                        bill = links[0]
                        modata = Bills.query.get(bill)

                #Modifying only the billing information (but getting the billing information if paying the bill
                if modlink == 7:
                    err, docref, expdata, assdata, leftscreen, modlink, hv = modbill(bill, update, err, docref, expdata, assdata, leftscreen, modlink, hv)


                cdat = People.query.filter(People.Company==modata.Company).first()
                if cdat is not None:
                    if cdat.Ptype == 'TowCo': hv[3] = '2'
                ifxfer = modata.bType

                if ifxfer == 'XFER':
                    run_xfer(update, err)

                if modlink == 11 or modlink == 12 or modlink == 14:
                    err, hv, docref, modlink = run_paybill(bill, update, err, hv, docref, username, modlink)

                if modal == 1:
                    calendar = 1
                    modlink = 0


            # create return status
            if update is not None and modlink != 6 and success:
                modlink = 0
                leftscreen = 1
                indat = '0'

        if modlink == 9 or modlink == 8:
            err, expdata, modlink, peep = modpeeps(peep, update, err, modlink, expdata)
            modata = People.query.get(peep)
            print(modata.Company)
# _____________________________________________________________________________________________________________B.UpdateDatabasesSection

        bdata, cdata = dataget_B(hv[1],hv[0],hv[3])
# ____________________________________________________________________________________________________________________B.SearchFilters
        if acceptthese == 1:
            print('acceptthese',acceptthese)
            modlink = 0
            # Check to see if these are all new jobs ready to be updated to ready status
            odervec = numcheckvec(bdata,'bill')
            print(odervec)
            if len(odervec)>0:
                for ix in odervec:
                    bdat = Bills.query.get(ix)
                    bdat.Temp2 = None
                db.session.commit()
            else:
                err.append('Must check at least one box to use this option')

        if modlink < 5:
            bill, peep, numchecked = numcheck(2, bdata, cdata, 0, 0, 0, ['bill', 'peep'])
        else:
            numchecked = 0

        if uploadS is not None:
            print('Using uploadS')
            if bill > 0  and numchecked == 1:
                bdat = Bills.query.get(bill)
                jo = bdat.Jo
                cache = bdat.Cache
                filename2 = f'Source_{jo}_c{str(cache)}.pdf'
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
                err.append('No Bill Selected for Source Upload')
                err.append('Select One Box')
# ____________________________________________________________________________________________________________________E.SearchFilters


# ____________________________________________________________________________________________________________________B.Viewers
        if viewo == 1 and numchecked == 1:
            if bill > 0:
                modata = Bills.query.get(bill)
                viewtype = 'source'
                hv[2] = viewtype
                if modata.Original is not None:
                    if len(modata.Original) > 5:
                        docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                        leftscreen = 0
                        leftsize = 8
                        modlink = 0
                        err.append('Viewing document '+docref)

        if viewo == 1 and numchecked != 1:
            err.append('Must check exactly one box to view source file')

        if viewck == 1 and numchecked == 1:
            if bill > 0:
                modata = Bills.query.get(bill)
                viewtype = 'check'
                hv[2] = viewtype
                if modata.Code1 is not None:
                    if len(modata.Code1) > 5:
                        docref = f'tmp/{scac}/data/vchecks/{modata.Code1}'
                        leftscreen = 0
                        leftsize = 8
                        modlink = 0
                        err.append('Viewing check '+docref)

        if viewck == 1 and numchecked != 1:
            err.append('Must check exactly one box to view checks')

# ____________________________________________________________________________________________________________________E.Viewers
# ____________________________________________________________________________________________________________________B.Modify Entries
        if vmod is not None and numchecked == 1:
            modlink, leftscreen, docref, expdata, modata = mod_init(err, bill, peep)

        # Modification coming from calendar
        if modify2 is not None:
            bill = nonone(modify2)
            modata = Bills.query.get(bill)
            modlink = 7
            leftsize = 8

# ____________________________________________________________________________________________________________________E.Modify Entries
# ____________________________________________________________________________________________________________________B.Add Entries

        if addE is not None:
            leftsize = 8
            modlink = 9
            # Remove any new starts that were not completed
            People.query.filter(People.Ptype=='NewVendor').delete()
            # We will create a blank line and simply modify that by updating:
            input = People(Company='', First=None, Middle=None, Last=None, Addr1='', Addr2='', Addr3='', Idtype=None, Idnumber='', Telephone='',
                           Email='', Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='NewVendor', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter(People.Ptype == 'NewVendor').first()
            peep = modata.id
            err.append('Enter Data for New Entity')
            expdata = Accounts.query.filter(Accounts.Type == 'Expense').order_by(Accounts.Name).all()

        if addE2 is not None:
            leftsize = 8
            modlink = 8
            # We will create a blank line and simply modify that by updating:
            hlist = hv_capture(['thiscomp','ctype','billacct','bamt','bdate','ddate','bdesc'])
            hv = hv[0:2]+hlist
            print(hv)
            # We will create a blank line and simply modify that by updating:
            input = People(Company='', First=None, Middle=None, Last=None, Addr1='', Addr2='', Addr3='', Idtype=None, Idnumber='', Telephone='',
                           Email='', Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='NewVendor', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter(People.Ptype == 'NewVendor').first()
            peep = modata.id
            err.append('Enter Data for New Entity')
            expdata = Accounts.query.filter(Accounts.Type == 'Expense').order_by(Accounts.Name).all()


# ____________________________________________________________________________________________________________________E.Add Entries

# ____________________________________________________________________________________________________________________B.Delete an Entry
        if deletehit is not None and numchecked >= 1:
            if bill > 0:
                bdat = Bills.query.get(bill)
                try:
                    orderid = nonone(bdat.Temp2)
                    adat = Autos.query.get(orderid)
                    if adat is not None:
                        adata = Autos.query.filter(Autos.Orderid == adat.Orderid).all()
                        for dat in adata:
                            dat.Status = 'Novo'
                except:
                    err.append('Delete problem')
                jo = bdat.Jo
                Gledger.query.filter(Gledger.Tcode==jo).delete()
                Bills.query.filter(Bills.id == bill).delete()
                db.session.commit()
            if peep > 0:
                peepvec = numcheckvec(cdata, 'peep')
                for peep in peepvec:
                    People.query.filter(People.id == peep).delete()
                    db.session.commit()

            bdata = Bills.query.order_by(Bills.bDate).all()
            cdata = People.query.filter((People.Ptype == 'Vendor') | (
                People.Ptype == 'TowCo')).order_by(People.Company).all()

        if deletehit is not None and numchecked == 0:
            err.append('Must have at least one item checked to use this option')
# ____________________________________________________________________________________________________________________E.Delete an Entry
# ____________________________________________________________________________________________________________________B.NewXfer.Billing
        if newxfer == 1:
            modlink = 3
            err.append('Select Source Document from List')
            leftscreen = 0
            expdata = Accounts.query.filter((Accounts.Type != 'Expense') & (Accounts.Type != 'Income') & (~Accounts.Type.contains('Accounts'))).order_by(Accounts.Name).all()
            vdata = [today, today, '', '']

        if newxfer is None and modlink == 3:

            leftscreen = 0
            bdate = request.values.get('bdate')
            ddate = request.values.get('bdate')
            xamt = request.values.get('xamt')
            new_desc = request.values.get('desc')
            xferfrom = request.values.get('fromacct')
            xferto = request.values.get('toacct')
            if xamt is None:
                xamt = '0.00'
            vdata = [bdate, ddate, xamt, new_desc, xferfrom, xferto]
            print(vdata)
            expdata = Accounts.query.filter((Accounts.Type != 'Expense') & (Accounts.Type != 'Income') & (~Accounts.Type.contains('Accounts'))).order_by(Accounts.Name).all()

        if thisxfer is not None:
            modlink = 0

            sdate = request.values.get('bdate')
            if sdate is None or sdate == '':
                sdate = today

            fromacct = request.values.get('fromacct')
            toacct = request.values.get('toacct')
            adat = Accounts.query.filter(Accounts.Name == toacct).first()
            if adat is not None:
                cat = adat.Category
                sub = adat.Subcategory
            else:
                cat = None
                sub = None
            xamt = request.values.get('xamt')
            xamt = d2s(xamt)
            xdesc = request.values.get('xdesc')
            btype = 'XFER'
            nextjo = newjo(billxfrcode, today)
            co = nextjo[0]

            input = Bills(Jo=nextjo, Pid=0, Company=toacct, Memo=None, Description=xdesc, bAmount=xamt, Status='Paid', Cache=0, Original=None,
                             Ref=None, bDate=sdate, pDate=sdate, pAmount=xamt, pMulti=None, pAccount=fromacct, bAccount=toacct, bType=btype,
                             bCat=cat, bSubcat=sub, Link=None, User=username, Co=co, Temp1=None, Temp2=None, Recurring=0, dDate=today,
                             pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0, iflag = 0, PmtList=None,
                             PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)

            db.session.add(input)
            db.session.commit()

            modata = Bills.query.filter(Bills.Jo == nextjo).first()
            err = gledger_write('xfer',nextjo,toacct,fromacct)
            bill = modata.id
            leftscreen = 1
            err.append('All is well')
            bdata = Bills.query.order_by(Bills.bDate).all()
        # ____________________________________________________________________________________________________________________E.NewXfer.Billing
        if copy == 1:
            if bill > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                bdat = Bills.query.get(bill)
                thisdate = bdat.bDate
                nextdate = thisdate + datetime.timedelta(days=30)
                nextjo = newjo(billexpcode, today)
                input = Bills(Jo=nextjo, Pid=bdat.Pid, Company=bdat.Company, Memo=bdat.Memo, Description=bdat.Description, bAmount=bdat.bAmount, Status=bdat.Status, Cache=0, Original=bdat.Original,
                                 Ref=bdat.Ref, bDate=nextdate, pDate=None, pAmount='0.00', pMulti=None, pAccount=bdat.pAccount, bAccount=bdat.bAccount, bType=bdat.bType,
                                 bCat=bdat.bCat, bSubcat=bdat.bSubcat, Link=None, User=username, Co=bdat.Co, Temp1=None, Temp2='Copy', Recurring=0, dDate=today, pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0,
                                 iflag=0, PmtList=None,PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)
                db.session.add(input)
                db.session.commit()

                err = gledger_write('newbill', nextjo, bdat.bAccount, bdat.pAccount)

            elif peep > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                pdat = People.query.get(peep)
                input = People(Company=pdat.Company, First=pdat.First, Middle='Copy', Last=None, Addr1=pdat.Addr1, Addr2=pdat.Addr2, Addr3=pdat.Addr3,
                               Idtype=pdat.Idtype, Idnumber=pdat.Idnumber, Telephone=pdat.Telephone,
                               Email=pdat.Email, Associate1=pdat.Associate1, Associate2=pdat.Associate2, Date1=today, Date2=None, Original=None,
                               Ptype='Vendor', Temp1=pdat.Temp1, Temp2=pdat.Temp2, Accountid=pdat.Accountid)
                db.session.add(input)
                db.session.commit()

            else:
                err.append('Must select one item to use this function')

        if copy12 is not None:
            if bill > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                bdat = Bills.query.get(bill)
                thisdate = bdat.bDate
                year = thisdate.year
                month = thisdate.month
                day = thisdate.day
                while month < 12:
                    month = month+1
                    nextdate = datetime.datetime(year, month, day)
                    nextjo = newjo(billexptype, today)
                    input = Bills(Jo=nextjo, Pid=bdat.Pid, Company=bdat.Company, Memo=bdat.Memo, Description=bdat.Description, bAmount=bdat.bAmount, Status=bdat.Status, Cache=0, Original=bdat.Original,
                                     Ref=bdat.Ref, bDate=nextdate, pDate=None, pAmount='0.00', pMulti=None, pAccount=bdat.pAccount, bAccount=bdat.bAccount, bType=bdat.bType,
                                     bCat=bdat.bCat, bSubcat=bdat.bSubcat, Link=None, User=username, Co=bdat.Co, Temp1=None, Temp2='Copy', Recurring=0, dDate=today, pAmount2='0.00', pDate2=None, Code1 = None, Code2=None, CkCache=0, QBi=0, iflag = 0, PmtList=None,
                                     PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)
                    db.session.add(input)
                    db.session.commit()

                    err = gledger_write('newbill',nextjo,bdat.bAccount,bdat.pAccount)

        if qpay is not None:
            if bill > 0 and numchecked == 1:
                print('qpay entered!!')
                bdat = Bills.query.get(bill)
                bdat.pDate = bdat.bDate
                bdat.pAmount = bdat.bAmount
                bdat.Temp2 = ''
                bdat.Status = 'Paid'
                pacct = bdat.pAccount
                if pacct is None:
                    pacct = get_def_bank(bdat)
                elif pacct == '0' or pacct == '1' or pacct == 0 or pacct == 1:
                    pacct = get_def_bank(bdat)
                bdat.pAccount = pacct
                db.session.commit()

# ____________________________________________________________________________________________________________________B.NewJob
        if newbill is not None:
            err, modlink, leftscreen, hv, expdata, vdata = newbill_init(err, hv)

        if newbill is None and modlink == 4:
            err, modlink, leftscreen, hv, expdata, vdata, assdata = newbill_passthru(err, hv, modlink)

        if thisbill is not None:
            err, modlink, leftscreen, bill = newbill_update(err, hv, modlink, username)
            bdata = Bills.query.order_by(Bills.bDate).all()
# ____________________________________________________________________________________________________________________E.New Bill
        if unpay == 1:
            if numchecked == 1 and bill > 0:
                myb = Bills.query.get(bill)
                iflag = myb.iflag
                if iflag is None: iflag = 0
                if iflag > 0 :
                    undolastpayment(bill)
                    err.append(f'Unpaid Last Payment on Bill {myb.Jo} and removed from register')
                else:
                    myb.Status = 'Unpaid'
                    myb.pAmount = '0.00'
                    db.session.commit()
                    Gledger.query.filter((Gledger.Tcode == myb.Jo) & (Gledger.Type == 'PD')).delete()
                    Gledger.query.filter((Gledger.Tcode == myb.Jo) & (Gledger.Type == 'PC')).delete()
                    Gledger.query.filter((Gledger.Tcode == myb.Jo) & (Gledger.Type == 'XD')).delete()
                    Gledger.query.filter((Gledger.Tcode == myb.Jo) & (Gledger.Type == 'XC')).delete()
                    db.session.commit()
                    err.append(f'Unpay Bill {myb.Jo} and remove from register')
            else:
                err.append('Must select one Bill to Unpay')

        if paybill is not None or paybill2 is not None or viewbill == 1:
            print('paybill',numchecked,modlink,bill)
            if numchecked == 1 and bill > 0:
                myb = Bills.query.get(bill)
                if viewbill == 1 and myb.Status == 'Paid': modlink = 15

                if myb.iflag is None: myb.iflag = 0
                if myb.iflag > 0:
                    err, modlink, leftscreen, docref, prevpayvec = install_pay_init(bill, err, modlink)
                    hv[19] = prevpayvec
                else:
                    err, modlink, leftscreen, docref = pay_init(bill, err, modlink)
                modata = Bills.query.get(bill)

            if numchecked > 1 and bill > 0:
                err, modlink, lefscreen, docref = multi_pay_init(bill, err, modlink)
                modata = Bills.query.get(bill)

            if numchecked == 0 or bill == 0:
                err.append('Must check at least one bill for this selection')
                err.append(f'Numchecked = {numchecked}')

            bdata = Bills.query.order_by(Bills.bDate).all()

        if printck is not None or modlink == 6 or modlink == 14 or indat != '0':
            from viewfuncs import check_prep

            def multi_prep(bill):
                if bdat.Status == 'Paid-M':
                    linkcode = bdat.Link
                    sbdata = Bills.query.filter(Bills.Link == linkcode)
                    link = linkcode.replace('Link+', '')
                    items = link.split('+')
                    links = []
                    [links.append(int(item)) for item in items]
                else:
                    links = 0
                    sbdata = 0

            if printck is not None and numchecked == 1:
                modlink = 14
            elif printck is not None and numchecked > 1:
                modlink = 6

            if indat != '0':
                bdat = Bills.query.filter(Bills.Jo == indat).first()
                bill = bdat.id
                modlink = 6
                if numchecked == 1: modlink = 14

            if (numchecked >= 1 and bill > 0) or modlink == 6 or modlink == 12 or modlink == 14:

                if modlink == 6 or modlink == 12 or modlink == 14:
                    bdat = Bills.query.get(bill)
                    try:
                        bill_list = json.loads(bdat.Link)
                    except:
                        bill_list = [bill]
                    billready, err, linkcode = check_prep(bill_list)

                else:
                    bill_list = numcheckvec(bdata, 'bill')
                    billready, err, linkcode = check_prep(bill_list)

                if billready == 1:
                    from viewfuncs import check_inputs
                    sbdata = Bills.query.filter(Bills.Link == linkcode).all()
                    links = json.loads(linkcode)
                    bdat = Bills.query.get(links[0])
                    pdat = People.query.get(bdat.Pid)

                    ckcache = bdat.CkCache
                    if ckcache is None or ckcache == 0:
                        ckcache = 1
                    last_ckfile = f'Check_{bdat.Jo}_{bdat.Ref}_c{str(ckcache-1)}.pdf'
                    ckfile = f'Check_{bdat.Jo}_{bdat.Ref}_c{str(ckcache)}.pdf'
                    docref = f'tmp/{scac}/data/vchecks/{ckfile}'
                    bdat.Code1 = ckfile
                    ckcache = ckcache+1
                    bdat.CkCache = ckcache
                    pamount = bdat.pAmount
                    if pamount == '0.00':
                        bdat.pAmount = bdat.bAmount
                    db.session.commit()

                    ckstyle = request.values.get('ckstyle')
                    if ckstyle is not None:
                        hv[21] = ckstyle
                        ckstyle = nonone(ckstyle)
                    else:
                        ckstyle = 1


                    err = check_inputs(bill_list)
                    co = bdat.Co
                    expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == co)) | ((Accounts.Type == 'Credit Card') & (Accounts.Co == co))).order_by(Accounts.Name).all()
                    #modlink = 6
                    leftscreen = 0
                    modata = Bills.query.get(links[0])
                    pb = 1
                    if err[0] != 'All is Well':
                        err.append('Check will not be displayed until above input items input or corrected')

                    else:
                        from writechecks import writechecks
                        if pdat is not None:
                            writechecks(bdat, pdat, docref, sbdata, links, ckstyle)

                            ck_check = bdat.bType

                            db.session.commit()
                            pacct = bdat.pAccount
                            #Only write to the ledger on update
                            if update is not None:
                                if pacct is not None and pacct != '0':
                                    print('check is',ck_check)
                                    if ck_check == 'Credit Card' or ck_check == 'XFER':
                                        print('Doing the Transfer')
                                        err = err = gledger_write('xfer',bdat.Jo,bdat.bAccount,bdat.pAccount)
                                        err.append(f'Ledger xfer for {bdat.Jo} to {bdat.bAccount} from {bdat.pAccount}')
                                    else:
                                        print('Paying the Bill')
                                        err = gledger_write('paybill',bdat.Jo,bdat.bAccount,bdat.pAccount)
                                        err.append(f'Ledger paid {bdat.Jo} to {bdat.bAccount} from {bdat.pAccount}')
                                else:
                                    err.append('No Account for Fund Withdrawal')


                        #Attempt to remove the previous cache copy:
                        try:
                            last_file = addpath(f'tmp/{scac}/data/vchecks/{last_ckfile}')
                            os.remove(last_file)
                        except:
                            print(f'Could nor remove {last_file}')

            else:
                err.append('Must select exactly 1 Bill box to use this option.')


# ____________________________________________________________________________________________________________________B.Matching
        if match is not None:
            if bill > 0 and peep > 0 and numchecked == 2:
                myo = Bills.query.get(bill)
                myp = People.query.get(peep)
                myo.Pid = peep
                myo.Company = myp.Company
                myo.Description = myp.Associate1
                db.session.commit()
            if numchecked != 2:
                err.append('Must select exactly 2 boxes to use this option.')
# ____________________________________________________________________________________________________________________E.Matching
# ____________________________________________________________________________________________________________________B.Calendar.Billing
        if calendar is not None or calupdate is not None:
            leftscreen = 2
            if calupdate is not None:
                waft = request.values.get('waft')
                wbef = request.values.get('wbef')
                waft = nonone(waft)
                wbef = nonone(wbef)
                nweeks = [wbef, waft]
            else:
                nweeks = [2, 2]
            caldays, daylist, weeksum = calendar7_weeks('Billing', nweeks)

            if calupdate is not None:
                for j in range(len(daylist)):
                    ilist = daylist[j]
                    if ilist:
                        tid = ilist[0]
                        fnum = 'note'+str(tid)
                        fput = request.values.get(fnum)
                        if len(fput) > 3:
                            billno = f'{scac}_Bill_{str(tid)}'
                            input = ChalkBoard(Jo=billno, creator=username,
                                               comments=fput, status=1)
                            db.session.add(input)
                            db.session.commit()

                caldays, daylist, weeksum = calendar7_weeks('Billing', nweeks)
# ____________________________________________________________________________________________________________________E.Calendar.Billing

        if (modlink > 0 and bill > 0) or (modlink > 0 and peep > 0) or leftscreen == 0:
            leftsize = 8
        elif leftscreen == 2:
            leftsize = 10
        else:
            leftsize = 10
    else:
        username, bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist,\
        weeksum, nweeks, filesel, docref, doctxt, bType, bClass, expdata, addjobselect, jobdata, modal, viewck, acceptthese,\
        assdata, monlvec = var_start()
        err = []
        hv = [0]*25
        hv[0] = 'X'
        hv[1] = '1'
        from viewfuncs import nonone, erud, dataget_B
        leftscreen = 1
        leftsize = 10
        addjobselect = 0
        dlist = ['on']*2
        dlist[1] = 'off'
        jobdata = 0
        modal = 0
        expdata = 0
        assdata = [0]
        divdat = Divisions.query.all()
        err.append('All is well')

    leftsize = 8
    rightsize = 12 - leftsize
    today = datetime.date.today()
    critday = datetime.date.today()+datetime.timedelta(days=7)
    bdata, cdata = dataget_B(hv[1],hv[0],hv[3])
    hv[23] = assdata
    acdata = Accounts.query.filter((Accounts.Type == 'Bank') | (Accounts.Type == 'Credit Card') | (Accounts.Type == 'Current Liability') ).order_by(Accounts.Name).all()
    err = erud(err)
    if expdata == 0: expdata = Accounts.query.filter(Accounts.Type == 'Expense').order_by(Accounts.Name).all()

    return username, divdat, hv, bdata, cdata, bill, peep, err, modata, adata, acdata, expdata, modlink, caldays, daylist, weeksum, nweeks, addjobselect, jobdata, modal, dlist, fdata, today, cdat, pb, critday, vdata, leftscreen, docref, doctxt, leftsize, cache, filesel
