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
from viewfuncs import docuploader, d2s, newjo, run_adjustments
from utils import requester
from gledger_write import gledger_write

today=datetime.date.today()
today_str = today.strftime('%Y-%m-%d')


def get_def_bank(bdat):
    coo = bdat.Co
    pdat = Accounts.query.filter( (Accounts.Co == coo) & (Accounts.Type == 'Bank')).first()
    if pdat is not None:
        pacct = pdat.Name
    else:
        pacct = 'No Bank'
    print('The Paying Acct',pacct)
    return pacct

def var_start():
    username = session['username'].capitalize()
    bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = [0] * 15
    filesel, docref, doctxt, bType, bClass = [''] * 5
    expdata, addjobselect, jobdata, modal, viewck, acceptthese, assdata = 0, 0, 0, 0, 0, 0, 0
    monlvec = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

    return username, bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, \
           weeksum, nweeks, filesel, docref, doctxt, bType, bClass, expdata, addjobselect, jobdata, modal, viewck, \
           acceptthese, assdata, monlvec

def var_request():
    getlist1 = ['Match', 'Vmod', 'Modify2', 'ViewO', 'addentity', 'addentity2', 'PayB', 'PayB2', 'UnPay', 'Prt',
                'Return', 'Delete']
    match, vmod, modify2, viewo, addE, addE2, paybill, paybill2, unpay, printck, returnhit, deletehit \
        = requester(getlist1)

    getlist2 = ['Update', 'modlink', 'NewB', 'ThisBill', 'Xfer', 'ThisXfer', 'Calendar', 'calupdate', 'incoming',
                'datatable1', 'datatable2']
    update, modlink, newbill, thisbill, newxfer, thisxfer, calendar, calupdate, incoming, datatable1, datatable2 \
        = requester(getlist2)

    getlist3 = ['copy', 'copy12', 'qpay', 'bill', 'cache', 'peep', 'UploadS', 'thismuch', 'vendmuch', 'codiv', 'addbox',
                'editbox', 'invobox', 'viewbox', 'xbox', 'dispbox']
    copy, copy12, qpay, bill, cache, peep, uploadS, thismuch, vendmuch, thisbox0, thisbox1, thisbox2, thisbox3, \
    thisbox4, thisbox5, thisbox6 = requester(getlist3)

    return match, vmod, modify2, viewo, addE, addE2, paybill, paybill2, unpay, printck, returnhit, deletehit, \
           update, modlink, newbill, thisbill, newxfer, thisxfer, calendar, calupdate, incoming, datatable1, \
           datatable2, copy, copy12, qpay, bill, cache, peep, uploadS, thismuch, vendmuch, thisbox0, thisbox1, thisbox2,\
           thisbox3, thisbox4, thisbox5, thisbox6


def container_list(lbox,holdvec):
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=20)
    err=[]
    comps = []
    tjobs = Orders.query.filter( (Orders.Hstat < 1) & (Orders.Date > stopdate) ).all()
    for job in tjobs:
        com = job.Shipper
        if com not in comps:
            comps.append(com)
    imlines='<br>'
    exlines='<br>'
    if len(comps) >= 1:
        for com in comps:
            tjobs = Orders.query.filter( (Orders.Hstat < 1) & (Orders.Shipper==com) & (Orders.Date > stopdate)).all()
            for ix,job in enumerate(tjobs):
                con = job.Container
                bk = job.Booking
                if con =='' or con == 'TBD':
                    if ix == 0:
                        exlines = exlines + f'<b>{com}</b><br>'
                    exlines = exlines + f'{bk}<br>'
                else:
                    if ix == 0:
                        imlines = imlines + f'<b>{com}</b><br>'
                    imlines = imlines + f'{con}<br>'

    holdvec[0] = imlines
    holdvec[1] = exlines
    err.append('Unpulled Import Container Last 20 Days')
    err.append('Unused Export Bookings Last 20 Days')

    return lbox, holdvec, err

def get_selections(thismuch, vendmuch, thisbox0, thisbox1, thisbox2, thisbox3, thisbox4, thisbox5, thisbox6, newbill, vmod, paybill, printck):
    hv = [0]*24
    hv[21] = 1  # default check style
    err = []
    holdvec = []
    AddE, copy, copy12, UploadS, newxfer, match, acceptthese, qpay, paybill2, viewo, viewck, deletehit, unpay, lbox, viewbill = [None]*15

    if thismuch is not None:
        hv[1] = thismuch
    else:
        hv[1] = request.values.get('passthismuch')

    if vendmuch is not None:
        hv[3] = vendmuch
    else:
        hv[3] = request.values.get('passvendmuch')

    if thisbox0 is not None:
        hv[0] = thisbox0
    else:
        hv[0] = request.values.get('passco')

    if thisbox1 == '1':
        newbill = 1
    elif thisbox1 == '2':
        addE = 1
    elif thisbox1 == '3':
        copy = 1
    elif thisbox1 == '4':
        copy12 = 1
    elif thisbox1 == '5':
        uploadS = 1
    elif thisbox1 == '6':
        newxfer = 1

    if thisbox2 == '1':
        vmod = 1
    elif thisbox2 == '2':
        match = 1
    elif thisbox2 == '3':
        acceptthese = 1
    elif thisbox2 == '4':
        run_adjustments()

    if thisbox3 == '1':
        qpay = 1
    elif thisbox3 == '2':
        paybill = 1
    elif thisbox3 == '3':
        paybill2 = 1
    elif thisbox3 == '4':
        printck = 1

    if thisbox4 == '1':
        viewo = 1
    elif thisbox4 == '3':
        viewbill = 1
    elif thisbox4 == '2':
        viewck = 1

    if thisbox5 == '1':
        deletehit = 1
    elif thisbox5 == '2':
        unpay = 1

    if thisbox6 == '1':
        mm2 = 1
        # Signature date:
        holdvec[16] = today_str
    elif thisbox6 == '2':
        lbox = 6
        lbox, holdvec, err = container_list(lbox, holdvec)
    elif thisbox6 == '3':
        lbox = 1

    return hv, newbill, AddE, copy, copy12, UploadS, newxfer, vmod, match, acceptthese, qpay, paybill, paybill2, printck, viewo, viewbill, viewck, deletehit, unpay, lbox, holdvec, err

def cleanup():
    modlink = 0
    leftscreen = 1
    indat = '0'
    # Delete all vendors created but not completed
    pgone = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
    for pg in pgone:
        company = pg.Company
        if company == '' or company == ' ' or company == None or company == 'None':
            People.query.filter(People.id == pg.id).delete()
            db.session.commit()
    # Put all bills in Paying Status back to unpaid
    pybills = Bills.query.filter(Bills.Status == 'Paying').all()
    for py in pybills:
        py.Status = 'Unpaid'
        db.session.commit()

    return modlink, leftscreen, indat

def next_check(pacct,bid):
    bdata = Bills.query.filter( (Bills.pAccount == pacct) & (Bills.Temp2 == 'Check') ).all()
    try:
        bdat = bdata[-1]
    except:
        cknum = '0000'
        bdat = None
    if bdat is not None:
        cknum = bdat.Ref
        print('Last Number Recorded is:',cknum)
        try:
            cknum = str(int(cknum)+1)
        except:
            cknum = '0000'
    else:
        cknum = '0000'
    return cknum

def alterations(modlink, leftscreen):
    if modlink == 4 or modlink == 8:
        leftscreen = 0
    else:
        leftscreen = 1
    return leftscreen

def incoming_setup():
    # Came to this point from outside so nothing is translated
    bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_billing_zero()
    filesel, docref, search11, search12, search13, search14, search21, search22, bType, bClass = init_billing_blank()

    towid = request.values.get('towid')
    towid = nonone(towid)
    adat = Autos.query.get(towid)
    pufrom = adat.Pufrom
    bdesc = 'Towing performed by \r\n' + adat.TowCompany
    print('Towing Items', adat.TowCompany, adat.Pufrom)
    adata = Autos.query.filter(Autos.Orderid == adat.Orderid).all()
    for dat in adata:
        bdesc = bdesc + '\r\n' + nons(dat.Year) + ' ' + nons(dat.Make) + \
                ' ' + nons(dat.Model) + ' VIN: ' + nons(dat.VIN)
        dat.Status = 'Paid'
        db.session.commit()

    cdat = People.query.filter((People.Company == adat.TowCompany) & (
            (People.Ptype == 'TowCo') | (People.Ptype == 'Vendor'))).first()
    if cdat is None:
        input = People(Company=adat.TowCompany, First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None,
                       Idtype=None, Idnumber=None, Telephone=None,
                       Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None,
                       Ptype='TowCo', Temp1=None, Temp2=None, Accountid=None)
        db.session.add(input)
        db.session.commit()
        cdat = People.query.filter((People.Company == adat.TowCompany) & (
                (People.Ptype == 'TowCo') | (People.Ptype == 'Vendor'))).first()

    if cdat is not None:
        cid = cdat.Accountid
        aid = cdat.id
        acdat = Accounts.query.filter(Accounts.id == cid).first()
        if acdat is not None:
            descript = acdat.Description
            baccount = acdat.Name
            btype = acdat.Type
            bcat = acdat.Category
            bsubcat = acdat.Subcategory
        else:
            bcat = 'NAY'
            bsubcat = 'NAY'
            descript = ''
            baccount = ''
    else:
        bcat = 'NAY'
        bsubcat = 'NAY'
        descript = ''
        baccount = ''

    # Create the new database entry for the source document
    sdate = adat.Date2
    ckmemo = 'Towing for Dealership Car Purchase'
    bamt = d2s(adat.TowCost)
    bref = ''
    btype = 'Expense'
    bcat = 'Direct'
    bsubcat = 'Overseas'
    account = compdata[9]
    baccount = 'Towing Costs'
    nextjo = newjo(billexpcode, today_str)
    print('JO generation output', billexpdata, nextjo)

    input = Bills(Jo=nextjo, Pid=aid, Company=cdat.Company, Memo=ckmemo, Description=bdesc, bAmount=bamt, Status='Paid',
                  Cache=0, Original='',
                  Ref=bref, bDate=sdate, pDate=today, pAmount=bamt, pMulti=None, pAccount=account, bAccount=baccount,
                  bType=btype,
                  bCat=bcat, bSubcat=bsubcat, Link=pufrom, User=username, Co=compdata[10], Temp1=None, Temp2=str(towid),
                  Recurring=0, dDate=today,
                  pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0, iflag=0, PmtList=None,
                  PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)

    db.session.add(input)
    db.session.commit()

    modata = Bills.query.filter(Bills.Jo == nextjo).first()
    csize = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
    bill = modata.id
    leftscreen = 1
    modlink = 12


def uploadsource(modlink,err,bill,docref,username):
    upnow = request.values.get('uploadnow')
    if upnow is not None:
        err, bill = docuploader('bill')
        if modlink == 4:
            bdat = Bills.query.get(bill)
            bdat.User = username
            original = bdat.Original
            if original is not None:
                docref = f'tmp/{scac}/data/vbills/' + original
            modlink = 7
        else:
            modlink = 0

    return modlink, err, bill, docref

def run_xfer(update,err):
    vals = ['fromacct', 'toacct', 'pamt', 'bref',
            'pdate', 'ckmemo', 'bdesc', 'ddate']
    a = list(range(len(vals)))
    for ix, v in enumerate(vals):
        a[ix] = request.values.get(v)
    if a[4] is None:
        a[4] = today
    bdol = d2s(a[2])
    modata.Memo = a[5]
    modata.Description = a[6]
    modata.bAmount = bdol
    modata.bDate = a[4]
    modata.dDate = a[7]
    modata.pAmount = bdol
    modata.pDate = a[4]
    modata.pAccount = a[0]
    modata.Ref = a[3]
    modata.User = username
    modata.Company = a[1]
    modata.bAccount = a[1]
    adat = Accounts.query.filter(Accounts.Name == a[1]).first()
    if adat is not None:
        cat = adat.Category
        sub = adat.Subcategory
        modata.bCat = cat
        modata.bSubcat = sub

    err.append('Modification to Xfer ' + modata.Jo + ' completed.')
    if update is not None:
        err = gledger_write('xfer', modata.Jo, modata.Company, modata.pAccount)
    return err

def modbill(bill, update, err, docref, expdata, assdata, leftscreen, modlink, hv):
    success = 1
    modata = Bills.query.get(bill)
    # Just updating the billing section
    vendor = request.values.get('thiscomp')
    vdat = People.query.filter((People.Ptype == 'Vendor') & (People.Company == vendor)).first()
    ptype = request.values.get('thistype')
    jo = modata.Jo
    ccode = jo[0]
    expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == ccode)) | (
                (Accounts.Type == 'Credit Card') & (Accounts.Co == ccode))).order_by(Accounts.Name).all()
    if ptype == 'asset1':
        assdata = Accounts.query.filter(
            (Accounts.Type == 'Fixed Asset') & (Accounts.Co == ccode)).order_by(Accounts.Name).all()
    elif ptype == 'asset2':
        assdata = Accounts.query.filter(
            (Accounts.Type == 'Current Asset') & (Accounts.Co == ccode)).order_by(Accounts.Name).all()

    co = request.values.get('ctype')
    if co == 'Pick':
        if vdat is not None:
            co = vdat.Idtype

    defexp = request.values.get('billacct')
    if defexp == '1':
        if vdat is not None:
            defexp = vdat.Associate1

    vals = ['bamt', 'bdate', 'ddate', 'bdesc']
    a = list(range(len(vals)))
    for ix, v in enumerate(vals): a[ix] = request.values.get(v)
    try:
        ba = float(a[0])
        ba = d2s(ba)
    except:
        success = 0
        err.append('Bill amount not a valid number')

    cdat = People.query.filter((People.Company == vendor) & ((People.Ptype == 'Vendor') | (
            People.Ptype == 'TowCo') | (People.Ptype == 'Overseas'))).first()
    if cdat is not None:
        modata.Pid = cdat.id
        if cdat.Ptype == 'TowCo': hv[3] = '2'
    else:
        modata.Pid = 0
        err.append('Vendor not found in database')

    modata.Company = vendor
    modata.bAccount = defexp
    modata.Co = co
    modata.Code2 = ptype
    if success == 1 and update is not None:
        modata.bAmount = ba
        modata.bDate = a[1]
        modata.dDate = a[2]
        modata.Description = a[3]
        leftscreen = 1
        modlink = 0

    db.session.commit()

    docref = f'tmp/{scac}/data/vbills/{modata.Original}'
    if os.path.isfile(addpath(docref)):
        leftscreen = 0
        err.append(f'Paying Bill {modata.Jo}')
    else:
        leftscreen = 1
        err.append(f'modifying Bill {modata.Jo}')
        err.append('Bill has no source document')

    return err, docref, expdata, assdata, leftscreen, modlink, hv



def run_paybill(bill, update, err, hv, docref, username, modlink):
    modata = Bills.query.get(bill)
    success = 1
    # This section means paying the bill and the transaction is not a transfer
    pamt = request.values.get('pamt')
    pacct = request.values.get('account')
    pmethod = request.values.get('method')
    pmemo = request.values.get('ckmemo')
    pdate = request.values.get('pdate')
    if pmethod == 'Check': modata.Ref = next_check(pacct, modata.id)
    elif pmethod == 'Bank Debit Card': modata.Ref = f'xx{getdebit(pacct)}'
    elif pmethod == 'Online Epay': modata.Ref = 'Epay'
    elif pmethod == 'Vendor ACH': modata.Ref = 'ACH'

    modata.pAmount = d2s(pamt)
    modata.pAccount = pacct
    modata.Temp2 =  pmethod
    modata.Memo = pmemo
    modata.pDate = pdate
    db.session.commit()

    # If it is an installment then need to grab the previous payment data if not an update:
    if update is None and modlink == 12:
        err, modlink, leftscreen, docref, prevpayvec = install_pay_init(bill, err, modlink)
        hv[19] = prevpayvec

    # if updating the database:
    elif update is not None:
        vals = ['pamt', 'account', 'bref', 'ckmemo', 'pdate', 'method']
        a = list(range(len(vals)))
        for ix, v in enumerate(vals): a[ix] = request.values.get(v)
        try:
            pa = float(a[0])
        except:
            success = 0
            err.append('Paid amount not a valid number')
        try:
            ba = float(modata.bAmount)
        except:
            success = 0
            err.append('Bill amount not a valid number')

        if success:
            if pa < ba or modlink == 12:
                print('Installment Section')
                err = installment(a, bill, username, err)
            else:
                err = regular_payment(a, bill, username, err)

            # Write to ledger as bill or asset
            modata = Bills.query.get(bill)
            jo, baccount = modata.Jo, modata.bAccount

            ptype = modata.Code2
            if ptype == 'bill':
                err = gledger_write('paybill', jo, baccount, pacct)
            elif ptype == 'asset1':
                err = gledger_write('purchase', jo, baccount, pacct)
            elif ptype == 'asset2':
                err = gledger_write('purchase', jo, baccount, pacct)

    return err, hv, docref, modlink

def modpeeps(peep, update, err, modlink, expdata):
    modata = People.query.get(peep)
    modata.Ptype = 'Vendor'
    vals = ['company', 'addr1', 'addr2', 'tid', 'tel', 'email', 'date1', 'ctype', 'billacct']
    a = list(range(len(vals)))
    for ix, v in enumerate(vals):
        a[ix] = request.values.get(v)
    modata.Company = a[0]
    modata.Addr1 = a[1]
    modata.Addr2 = a[2]
    modata.Idnumber = a[3]
    modata.Telephone = a[4]
    modata.Email = a[5]
    modata.Date1 = a[6]
    modata.Idtype = a[7]
    diva = Divisions.query.filter(Divisions.Co == a[7]).first()
    if diva is not None:
        modata.First = diva.Color
    aname = a[8]
    if aname is not None:
        aname = aname.strip()
    else:
        aname = ''
    modata.Associate1 = aname
    aadat = Accounts.query.filter((Accounts.Name == aname) & (Accounts.Co == a[7])).first()
    if aadat is not None:
        modata.Accountid = aadat.id
        modata.Associate2 = aadat.Type
        modata.Temp1 = aadat.Category
        modata.Temp2 = aadat.Subcategory
        modata.Idtype = aadat.Co
    db.session.commit()
    err.append('Continue New Entry for Entity ID ' + str(modata.id))

    if update is not None:
        err.append('Modification to Entity ID ' + str(modata.id) + ' completed.')
        # if modlink=8 then we are updating vendor while entering a new bill, time to transition back to the bill
        if modlink == 8:
            modlink = 44
            cdat = People.query.get(peep)
            print('cdat1', cdat.Company, modlink)
            if cdat is not None:
                # Set account defaults for this vendor
                ccode = cdat.Idtype
                expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == ccode)) | (
                            (Accounts.Type == 'Credit Card') & (Accounts.Co == ccode))).order_by(Accounts.Name).all()
                print('Color Here', ccode)
                diva = Divisions.query.filter(Divisions.Co == ccode).first()
                if diva is not None:
                    modata.First = diva.Color
                    db.session.commit()
            peep = 0

        else:
            modlink = 0
    else:
        leftsize = 8
        bval = request.values.get('ctype')
        if bval is not None:
            modata.Idtype = bval
            db.session.commit()
            ccode = bval
            expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == ccode)) | (
                        (Accounts.Type == 'Credit Card') & (Accounts.Co == ccode))).order_by(Accounts.Name).all()

    # And now update the crossover to Storage in case the Company info changed:
    cross = Bills.query.filter(Bills.Pid == peep)
    for cros in cross:
        cros.Company = a[0]
    db.session.commit()

    return err, expdata, modlink, peep

def regular_payment(a, bill, username, err):
    modata = Bills.query.get(bill)
    pamtf = float(a[0])
    pamt = d2s(pamtf)
    pacct = a[1]
    ckref = a[2]
    ckmemo = a[3]
    pdate = a[4]
    pmethod = a[5]
    if pdate is None: pdate = today
    modata.Memo = ckmemo
    modata.pAmount = pamt
    modata.pDate = pdate
    modata.pAccount = pacct
    modata.Ref = ckref
    modata.Temp2 = pmethod
    modata.Status = 'Paid'
    modata.User = username
    db.session.commit()

    return err


def installment(a, bill, username, err):
    modata = Bills.query.get(bill)
    pamtf = float(a[0])
    bamtf = float(modata.bAmount)
    pamt = d2s(pamtf)
    pacct = a[1]
    ckref = a[2]
    ckmemo = a[3]
    pdate = a[4]
    pmethod = a[5]
    if pdate is None: pdate = today
    ckfile = modata.Code1
    if ckfile is None: ckfile = 'NoFile'

    iflag = modata.iflag
    #If this is first payment of installments can still change bill information
    if iflag == 0 or iflag is None:
        modata.iflag = 1
        modata.Memo = ckmemo
        modata.pAmount = pamt
        modata.pAmount2 = pamt
        modata.pDate = pdate
        modata.pAccount = pacct
        modata.Ref = ckref
        modata.Status = 'PartPaid'
        modata.User = username
        db.session.commit()
        pmtlist, paclist, reflist, memolist, pdatelist, checklist, pmethods = [],[],[],[],[],[],[]
    else:
        iflag = iflag + 1
        modata.iflag = iflag
        modata.Memo = ckmemo
        modata.pAmount2 = pamt
        modata.pDate = pdate
        modata.pAccount = pacct
        modata.Ref = ckref
        modata.Status = 'PartPaid'
        modata.User = username

        pmtlist = json.loads(modata.PmtList)
        paclist = json.loads(modata.PacctList)
        reflist = json.loads(modata.RefList)
        memolist = json.loads(modata.MemoList)
        pdatelist = json.loads(modata.PdateList)
        checklist = json.loads(modata.CheckList)
        pmethods = json.loads(modata.MethList)
        total = pamtf
        for pmt in pmtlist:
            total = total + float(pmt)
        diff = bamtf - total
        if diff < .01:
            print(bamtf,total,diff)
            modata.Status = 'Paid'
        modata.pAmount = d2s(total)

    pmtlist.append(pamt)
    paclist.append(pacct)
    reflist.append(ckref)
    memolist.append(ckmemo)
    pdatelist.append(pdate)
    checklist.append(ckfile)
    pmethods.append(pmethod)

    modata.PmtList = json.dumps(pmtlist)
    modata.PacctList = json.dumps(paclist)
    modata.RefList = json.dumps(reflist)
    modata.MemoList = json.dumps(memolist)
    modata.PdateList = json.dumps(pdatelist)
    modata.CheckList = json.dumps(checklist)
    modata.MethList = json.dumps(pmethods)

    db.session.commit()

    return err

def pay_init(bill, err, modlink):
    success = 1
    myb = Bills.query.get(bill)
    status = myb.Status
    if status == 'Paid':
        success = 0
        err.append('Bill has been paid in full.  Use unpay to restart payment process')
    if success == 1:
        myb.pDate = today
        myb.pAmount = myb.bAmount
        pacct = myb.pAccount
        if pacct is None:
            pacct = get_def_bank(myb)
        elif len(pacct) < 4:
            pacct = get_def_bank(myb)
        myb.pAccount = pacct
        myb.Status = 'Paying'
        db.session.commit()
        modlink = 11
        err.append(f'Paying Bill {myb.Jo}')
        docref = f'tmp/{scac}/data/vbills/{myb.Original}'
        if os.path.isfile(addpath(docref)): leftscreen = 0
        else:
            leftscreen = 1
            err.append('Bill has no source document')
    else:
        err.append('Could not complete billpay')
        modlink = 0
        leftscreen = 1

    return err, modlink, leftscreen, docref

def multi_pay_init(bill, err, modlink):
    # See how many bills are to be paid together
    nbill = 0
    bill_ids = []
    total = 0
    for data in bdata:
        testone = request.values.get('bill' + str(data.id))
        if testone:
            myb = Bills.query.get(data.id)
            try:
                nbill = nbill + 1
                bamt = myb.bAmount
                bamt = d2s(bamt)
                amt = float(bamt)
                total = total + amt
                bill_ids.append(data.id)
            except:
                err.append('Some checked bills of multi-pay already paid')
                exit = 1
    if exit == 0 and nbill > 1:
        # Create link code
        linkcode = 'Link'
        # Create a master reference from first bill
        masterbill = bill_ids[0]
        myb = Bills.query.get(masterbill)
        masterref = myb.Ref
        masteracct = myb.pAccount
        masterdesc = ''
        masterpid = myb.Pid
        masterpayee = myb.Company
        co = myb.Co
        expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == co)) | (
                    (Accounts.Type == 'Credit Card') & (Accounts.Co == co))).order_by(Accounts.Name).all()
        if masteracct is None or len(masteracct) < 4:
            masteracct = 'Industrial Bank'
        for bill in bill_ids:
            myb = Bills.query.get(bill)
            linkcode = linkcode + '+' + str(bill)
            try:
                descline = 'Bill ID:' + str(myb.id) + ' Billcode: ' + \
                           myb.Jo + ' Amount: ' + str(myb.bAmount) + '\n'
            except:
                descline = 'Bill ID:' + str(myb.id)
            masterdesc = masterdesc + descline
        for bill in bill_ids:
            myb = Bills.query.get(bill)
            myb.Status = 'Paid-M'
            myb.Link = linkcode
            myb.pDate = today
            myb.pAmount = myb.bAmount
            myb.pMulti = "{:.2f}".format(total)
            myb.Ref = masterref
            myb.pAccount = masteracct
            myb.Description = masterdesc
            myb.Pid = masterpid
            myb.Company = masterpayee
            db.session.commit()
            jo = myb.Jo
            err = gledger_write('paybill', jo, myb.bAccount, myb.pAccount)

    return err, modlink, leftscreen, docref

def install_pay_init(bill, err, modlink):
    success = 1
    modata = Bills.query.get(bill)
    status = modata.Status
    if status == 'Paid':
        success = 0
        leftscreen, docref, prevpayvec = 1,0,0
        err.append('Bill has been paid in full.  Use unpay to restart payment process')
    else:
        prevpayvec = []
        pmtlist = json.loads(modata.PmtList)
        paclist = json.loads(modata.PacctList)
        reflist = json.loads(modata.RefList)
        pmethods = json.loads(modata.MethList)
        memolist = json.loads(modata.MemoList)
        pdatelist = json.loads(modata.PdateList)
        checklist = json.loads(modata.CheckList)
        total = 0.00
        for ix, pmt in enumerate(pmtlist):
            prevpayvec.append([pmtlist[ix],paclist[ix],pmethods[ix],reflist[ix],memolist[ix],pdatelist[ix]])
            total = total + float(pmt)
        bamtf = float(modata.bAmount)
        diff = bamtf - total
        modata.pDate = today
        modata.pAmount = d2s(diff)
        pacct = modata.pAccount
        if pacct is None:
            pacct = get_def_bank(modata)
        elif len(pacct) < 4:
            pacct = get_def_bank(modata)
        modata.pAccount = pacct
        db.session.commit()

        modlink = 12
        err.append(f'Paying Part of Bill {modata.Jo}')
        docref = f'tmp/{scac}/data/vbills/{modata.Original}'
        if os.path.isfile(addpath(docref)): leftscreen = 0
        else:
            leftscreen = 1
            err.append('Bill has no source document')

    return err, modlink, leftscreen, docref, prevpayvec

def newbill_init(err, hv):
    err.append('Select Source Document from List')
    modlink = 4
    leftscreen = 0
    narrow = 1
    hv[5], hv[6] = vendorlist(narrow)
    expdata = Accounts.query.filter((Accounts.Type == 'Expense') | (Accounts.Type == 'Credit Card')).order_by(
        Accounts.Name).all()
    vdata = [today, today, '', '']
    return err, modlink, leftscreen, hv, expdata, vdata

def newbill_passthru(err, hv, modlink):
    leftscreen = 0
    assdata = 0
    bdate = request.values.get('bdate')
    ddate = request.values.get('ddate')
    bamt = request.values.get('bamt')
    bdesc = request.values.get('bdesc')
    narrow = 1
    hv[5], hv[6] = vendorlist(narrow)

    if modlink == 4:
        thiscompany = request.values.get('thiscomp')
        form_co = request.values.get('ctype')
        form_exp = request.values.get('billacct')
        form_type = request.values.get('thistype')
        if thiscompany != '0':
            cdat = People.query.filter((People.Company == thiscompany) & (
                (People.Ptype == 'Vendor') | (People.Ptype == 'TowCo')) ).first()
            if cdat is not None:
                default_co = cdat.Idtype
                default_exp = cdat.Associate1
            else:
                default_co = None
                default_exp = None
        else:
            default_co = None
            default_exp = None

        hv[22] = form_type

        if form_co == '0':
            comp = default_co
        else:
            comp = form_co
        hv[8] = comp

        if form_exp == '0':
            thisaccount = default_exp
        else:
            thisaccount = form_exp
        hv[9] = thisaccount



        ccdat = Accounts.query.filter(Accounts.Name == thisaccount).first()

        if cdat is not None:
            hv[7] = cdat.Company
            cdat.Idtype = comp
            cdat.Associate1 = thisaccount
            db.session.commit()

            ddat = Divisions.query.filter(Divisions.Co==cdat.Idtype).first()
            if ddat is not None:
                err.append(f'Loading data for {thiscompany} Defaults')
                err.append(f'Bill for {cdat.Idtype}: {ddat.Name}')
        elif thiscompany != 0:
            # This section for case of bill to credit card account
            thisaccount = request.values.get('billacct')
            ccdat = Accounts.query.filter( Accounts.Name == thisaccount ).first()
            if ccdat is not None:
                hv[7] = thiscompany
                hv[8] = ccdat.Co
                hv[9] = 'No'

    else:
        modlink = 4 #reset the vendor feed back to bill feed
        cdat = None

    if cdat is not None:
        # Set account defaults for this vendor
        ccode = cdat.Idtype
        cchg = request.values.get('ctype')
        ddat = Divisions.query.filter(Divisions.Co ==cchg).first()
        if ddat is not None:
            cdat.Idtype = ddat.Co
            ccode = ddat.Co
        print('expdata coming from above', form_type)
        expdata = Accounts.query.filter( ((Accounts.Type == 'Expense') & (Accounts.Co == ccode)) | ((Accounts.Type == 'Credit Card') & (Accounts.Co == ccode)) ).order_by(Accounts.Name).all()
        if form_type == 'asset1':
            assdata = Accounts.query.filter( (Accounts.Type == 'Fixed Asset') & (Accounts.Co == ccode) ).order_by(Accounts.Name).all()
        elif form_type == 'asset2':
            assdata = Accounts.query.filter((Accounts.Type == 'Current Asset') & (Accounts.Co == ccode)).order_by(Accounts.Name).all()

        # Get information from previous bill paid by the vendor

        ldata = Bills.query.filter(Bills.Company == cdat.Company).all()
        if ldata:
            ldat = ldata[-1]
            last_desc = ldat.Description
            last_memo = ldat.Memo
            new_desc = ''
            new_memo = ''
            try:
                for i, x in enumerate(monlvec):
                    if i == 11:
                        k = 0
                    else:
                        k = i+1
                    if x in last_desc:
                        new_desc = last_desc.replace(x, monlvec[k])
                    if x in last_memo:
                        new_memo = last_memo.replace(x, monlvec[k])
                last_amt = d2s(ldat.bAmount)
            except:
                last_amt = 0.00
                #No previous bills
            # last_date=datetime.datetime.strptime(ldat.bDate,"%Y-%m-%d")+datetime.timedelta(days=30)

            last_date = ldat.bDate
            if last_date is not None:
                last_date = last_date.strftime("%Y-%m-%d")
                err.append(f'The last bill to this vendor was written on {last_date} for ${last_amt}')
            else:
                last_date = 'None'
                err.append(f'No Bills Recorded for this Vendor')
            vdata = [bdate, ddate, last_amt, new_desc]
        else:
            # if not then get the category info from the vendor data
            vdata = [bdate, ddate, bamt, bdesc]
    else:
        ccode = hv[8]
        print('expdata coming from below', form_type)
        expdata = Accounts.query.filter( ((Accounts.Type == 'Expense') & (Accounts.Co == ccode)) | ((Accounts.Type == 'Credit Card') & (Accounts.Co == ccode)) ).order_by(Accounts.Name).all()
        if form_type == 'asset1':
            assdata = Accounts.query.filter( (Accounts.Type == 'Fixed Asset') & (Accounts.Co == ccode) ).order_by(Accounts.Name).all()
        elif form_type == 'asset2':
            assdata = Accounts.query.filter((Accounts.Type == 'Current Asset') & (Accounts.Co == ccode)).order_by(Accounts.Name).all()
        vdata = [bdate, ddate, bamt, bdesc]

    return err, modlink, leftscreen, hv, expdata, vdata, assdata



def newbill_update(err, hv, modlink, username):
    modlink = 0
    # Create the new database entry for the source document
    bdate = request.values.get('bdate')
    ddate = request.values.get('ddate')
    print('bdate:', bdate, ddate)

    thiscompany = request.values.get('thiscomp')
    thistype = request.values.get('thistype')
    cdat = People.query.filter((People.Company == thiscompany) & (
            (People.Ptype == 'Vendor') | (People.Ptype == 'TowCo'))).first()
    if cdat is not None:
        acomp = cdat.Company
        cid = cdat.Accountid
        aid = cdat.id
        cc_check = cdat.Associate2
        acdat = Accounts.query.filter(Accounts.id == cid).first()
        if acdat is not None:
            baccount = acdat.Name
            category = acdat.Category
            subcat = acdat.Subcategory
            descript = acdat.Description
            btype = acdat.Type
        else:
            category = 'NAY'
            subcat = 'NAY'
            descript = ''
            btype = ''
            baccount = ''
    else:
        # This section for case of bill to credit card account
        thisaccount = request.values.get('billacct')
        ccdat = Accounts.query.filter(Accounts.Name == thisaccount).first()
        if ccdat is not None:
            acomp = ccdat.Name
            aid = ccdat.id
            category = ccdat.Category
            subcat = ccdat.Subcategory
            descript = ccdat.Description
            btype = ccdat.Type

        else:
            acomp = None
            aid = None
            category = 'NAY'
            subcat = 'NAY'
            descript = ''
            btype = ''
            baccount = ''

    bdesc = request.values.get('bdesc')
    bamt = request.values.get('bamt')
    bamt = d2s(bamt)
    bcomp = request.values.get('bcomp')
    cco = request.values.get('ctype')
    print(f'Getting nextjo with {cco} and {today_str}')
    if cc_check == 'Credit Card':
        nextjo = newjo(cco + 'X', today_str)
    else:
        nextjo = newjo(cco + 'B', today_str)
    account = request.values.get('crataccount')
    if thistype == 'bill':
        baccount = request.values.get('billacct')
        code2 = 'bill'
    else:
        baccount = request.values.get('assacct')
        code2 = request.values.get('billacct')
        acdat = Accounts.query.filter(Accounts.Name == baccount).first()
        if acdat is not None:
            baccount = acdat.Name
            category = acdat.Category
            subcat = acdat.Subcategory
            descript = acdat.Description
            btype = acdat.Type

    input = Bills(Jo=nextjo, Pid=aid, Company=acomp, Memo='', Description=bdesc, bAmount=bamt, Status='Unpaid', Cache=0,
                  Original=None,
                  Ref='', bDate=bdate, pDate=today, pAmount='0.00', pMulti=None, pAccount=account, bAccount=baccount,
                  bType=btype,
                  bCat=category, bSubcat=subcat, Link=None, User=username, Co=cco, Temp1=None, Temp2=None, Recurring=0,
                  dDate=ddate,
                  pAmount2='0.00', pDate2=None, Code1=None, Code2=code2, CkCache=0, QBi=0, iflag=0, PmtList=None,
                  PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)

    db.session.add(input)
    db.session.commit()
    if cc_check != 'Credit Card':
        if thistype == 'bill':
            err = gledger_write('newbill', nextjo, baccount, account)
        elif thistype == 'asset1':
            err = gledger_write('purchase', nextjo, baccount, account)
        elif thistype == 'asset2':
            err = gledger_write('purchase', nextjo, baccount, account)

            adat = Adjusting.query.filter((Adjusting.Jo == nextjo) & (Adjusting.Status == 0)).first()
            dt2 = datetime.datetime.strptime(ddate, "%Y-%m-%d")
            dt1 = datetime.datetime.strptime(bdate, "%Y-%m-%d")
            delta = dt2 - dt1
            ndays_incl = delta.days + 1
            adjamt = float(bamt) / ndays_incl
            adjamt = d2s(adjamt)
            if adat is None:
                mop = dt1.month
                input = Adjusting(Jo=nextjo, Date=bdate, DateEnd=ddate, Mop=mop, Moa=0, Asset=baccount, Expense=code2,
                                  Amtp=bamt, Amta=adjamt, Status=0)
                db.session.add(input)
                db.session.commit()
            else:
                err.append('This adjusting account exists.  Must delete it.')

    # Check if shared account:
    adat = Accounts.query.filter(Accounts.Name == baccount).first()
    if adat is not None:
        shared = adat.Shared
        if isinstance(shared, str):
            divid, fromtoid, tofromid, mirrorid = json.loads(shared)
            print('found idlist', divid, fromtoid, tofromid, mirrorid)
            ddat = Divisions.query.get(divid)
            apportion = float(ddat.Apportion)
            appamt = float(bamt) * apportion
            gledger_app_write('app1', nextjo, cco, fromtoid, mirrorid, appamt)
            gledger_app_write('app2', nextjo, ddat.Co, mirrorid, tofromid, appamt)

    # reget because we need the bill unique id number in the document
    modata = Bills.query.filter(Bills.Jo == nextjo).first()
    csize = People.query.filter((People.Ptype == 'Vendor') | (
            People.Ptype == 'TowCo')).order_by(People.Company).all()
    bill = modata.id
    leftscreen = 1
    err.append('All is well')

    return err, modlink, leftscreen, bill


def mod_init(err, bill, peep):
    print('Entering Modification Section')

    if bill > 0:
        modata = Bills.query.get(bill)
        vendor = request.values.get('thiscomp')
        if vendor is None:
            vendor = modata.Company

        vdat = People.query.filter((People.Ptype == 'Vendor') & (People.Company == vendor)).first()

        ptype = request.values.get('thistype')
        if ptype == 'asset1':
            print('getting asset1')
            assdata = Accounts.query.filter((Accounts.Type == 'Fixed Asset') & (Accounts.Co == ccode)).order_by(
                Accounts.Name).all()
        elif ptype == 'asset2':
            print('getting asset2')
            assdata = Accounts.query.filter((Accounts.Type == 'Current Asset') & (Accounts.Co == ccode)).order_by(
                Accounts.Name).all()

        co = request.values.get('ctype')
        if co is None:
            co = modata.Co
        if co == 'Pick':
            if vdat is not None:
                co = vdat.Idtype

        defexp = request.values.get('billacct')
        if defexp is None:
            defexp = modata.bAccount
        if defexp == '1':
            if vdat is not None:
                defexp = vdat.Associate1

        modata.Company = vendor
        modata.bAccount = defexp
        modata.Co = co
        modata.Code2 = ptype
        db.session.commit()

        duedate = modata.dDate
        if duedate is None:
            modata.dDate = modata.bDate
        paccount = modata.pAccount
        print(paccount)
        if paccount is None:
            lastbill = Bills.query.filter((Bills.Company == modata.Company) & (Bills.id != modata.id)).first()
            if lastbill is not None:
                modata.pAccount = lastbill.pAccount
        db.session.commit()
        modata = Bills.query.get(bill)

        expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == co)) | (
                    (Accounts.Type == 'Credit Card') & (Accounts.Co == co))).order_by(Accounts.Name).all()
        leftscreen = 0
        modlink = 7

        if modata.Original is not None:
            if len(modata.Original) > 5:
                leftscreen = 0
                docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                #doctxt = txtfile(docref)
                err.append('All is well')
            else:
                err.append('There is no document available for this selection')
                docref = ''
        else:
            err.append('There is no document available for this selection')
            docref = ''

    if peep > 0:
        modata = People.query.get(peep)
        modlink = 9
        co = modata.Idtype
        expdata = Accounts.query.filter(((Accounts.Type == 'Expense') & (Accounts.Co == co)) | (
                    (Accounts.Type == 'Credit Card') & (Accounts.Co == co))).order_by(Accounts.Name).all()

    return modlink, leftscreen, docref, expdata, modata

def vendorlist(narrow):
    vendors = []
    if narrow == 1:
        vdata = People.query.filter(People.Ptype == 'Vendor').order_by(People.Company).all()
        for vdat in vdata:
            vendors.append(vdat.Company)
        ccdata = Accounts.query.filter(Accounts.Type == 'CC').order_by(Accounts.Name).all()
        for ccdat in ccdata:
            vendors.append(ccdat.Name + ' (Credit Card)')
        vendors.sort()
        return vendors, 'Exp'
    if narrow == 2:
        vendors = []
        ccdata = Accounts.query.filter(Accounts.Type == 'CC').order_by(Accounts.Name).all()
        for ccdat in ccdata:
            vendors.append(ccdat.Name + ' (Credit Card)')
        vendors.sort()
        return vendors, 'CC'

def getdebit(pacct):
    adat = Accounts.query.filter(Accounts.Name==pacct).first()
    dbl4 = 'xxxx'
    if adat is not None:
        debit = adat.Shared
        if debit is not None:
            if len(debit) >= 4:
                dbl4 = debit[-4:]
    return dbl4

def undolastpayment(bill):
    myb = Bills.query.get(bill)
    ix = myb.iflag - 1
    pmtlist = json.loads(myb.PmtList)
    paclist = json.loads(myb.PacctList)
    reflist = json.loads(myb.RefList)
    pmethods = json.loads(myb.MethList)
    memolist = json.loads(myb.MemoList)
    pdatelist = json.loads(myb.PdateList)
    checklist = json.loads(myb.CheckList)

    pmtlist = pmtlist[:ix]
    total = 0.00
    for pmt in pmtlist:
        total = total + float(pmt)
    myb.pAmount = d2s(total)
    myb.pAmount2 = pmtlist[-1:]

    myb.PmtList = json.dumps(pmtlist)
    myb.PacctList = json.dumps(paclist[:ix])
    myb.RefList = json.dumps(reflist[:ix])
    myb.MemoList = json.dumps(memolist[:ix])
    myb.PdateList = json.dumps(pdatelist[:ix])
    myb.CheckList = json.dumps(checklist[:ix])
    myb.MethList = json.dumps(pmethods[:ix])
    myb.Status = 'PartPaid'

    db.session.commit()

    jo = myb.Jo + f'-{myb.iflag}'
    Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == 'PD')).delete()
    Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == 'PC')).delete()
    Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == 'XD')).delete()
    Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == 'XC')).delete()
    db.session.commit()

