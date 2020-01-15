from runmain import db
from models import Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Orders, Drops, Services
from flask import session, logging, request
import datetime
import calendar
import re
import os
import subprocess
from CCC_system_setup import myoslist, addpath, scac
from viewfuncs import chassismatch, stat_update, dropupdate2, dropupdate3, getexpimp, stripper, d2s
import json

today = datetime.date.today()


def multi_inv(odata, odervec, chas, newchas):
    # First create all the invoices for these specific jobs
    for oder in odervec:
        myo = Orders.query.get(oder)
        con = myo.Container
        qty, d1, d2 = chassismatch(myo)
        myo.Links = json.dumps(odervec)
        Invoices.query.filter(Invoices.Jo == myo.Jo).delete()
        myo.Istat = 1
        db.session.commit()

    for oder in odervec:
        myo = Orders.query.get(oder)
        qty, d1, d2 = chassismatch(myo)
        shipper = myo.Shipper
        jo = myo.Jo
        bid = myo.Bid

        lid = myo.Lid
        if lid is None or lid == 0:
            expimp = getexpimp(con)
            if expimp == 'Export':
                lid = dropupdate2(bid)
            if expimp == 'Import':
                lid = dropupdate3('BAL')
            if lid is None or lid == 0:
                myo.lid = 0
                myo.Company = 'NAY'
            else:
                print('lid=',lid)
                ddat = Drops.query.get(lid)
                myo.Lid = lid
                myo.Company = ddat.Entity
            db.session.commit()
            myo = Orders.query.get(oder)

        did = myo.Did
        if did is None or did == 0:
            expimp = getexpimp(con)
            if expimp == 'Export':
                did = dropupdate3('BAL')
            if expimp == 'Import':
                did = dropupdate2(bid)
            if did is None or did == 0:
                myo.did = 0
                myo.Company2 = 'NAY'
            else:
                ddat = Drops.query.get(did)
                myo.Did = did
                myo.Company2 = ddat.Entity
            db.session.commit()
            myo = Orders.query.get(oder)

        cache = myo.Icache
        c1, c2 = myo.Company, myo.Company2
        c1, c2 = stripper(c1), stripper(c2)

        if chas != 1:
            # Make sure all invoices have the required parts
            total = float(myo.Amount)
            descript = 'From ' + c1 + ' to ' + c2
            input = Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Line Haul', Description=descript,
                             Ea=myo.Amount, Qty=1, Amount=total, Total=total, Date=today, Original=None, Status='New')
            db.session.add(input)
            db.session.commit()

        # If chassis to be added then we have to add those fees in:
        if chas == 1:
            mys = Services.query.filter(Services.Service == 'Chassis Fees').first()
            descript = 'Days of Chassis'
            if newchas == 0:
                price = float(mys.Price)
            else:
                price = float(newchas)
            chassis_amount = price*qty
            haul_amount = float(myo.Amount)
            total = haul_amount+chassis_amount
            input = Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service=mys.Service, Description=descript,
                             Ea=d2s(price), Qty=qty, Amount=chassis_amount, Total=total, Date=today, Original=None, Status='New')
            db.session.add(input)
            db.session.commit()
            descript = 'From ' + c1 + ' to ' + c2
            input = Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Line Haul', Description=descript,
                             Ea=myo.Amount, Qty=1, Amount=haul_amount, Total=total, Date=today, Original=None, Status='New')
            db.session.add(input)
            db.session.commit()
        # Now write out the invoice
        ldata = Invoices.query.filter(Invoices.Jo == myo.Jo).order_by(Invoices.Ea.desc()).all()
        pdata1 = People.query.filter(People.id == myo.Bid).first()
        pdata2 = Drops.query.filter(Drops.id == myo.Lid).first()
        pdata3 = Drops.query.filter(Drops.id == myo.Did).first()
        from make_T_invoice import T_invoice
        T_invoice(myo, ldata, pdata1, pdata2, pdata3, cache, today, 0)
        docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'

        for ldatl in ldata:
            ldatl.Pid = pdata1.id
            ldatl.Original = docref
            db.session.commit()

        myo.Invoice = os.path.basename(docref)
        myo.Icache = cache+1
        db.session.commit()
# Now all the invoices are created.  Next pack them up and create a single master invoice.
    keydata = [0]*len(odervec)
    grandtotal = 0
    for jx, ix in enumerate(odervec):

        odat = Orders.query.get(ix)
        print(f'Working {oder} {odat.Jo} ')
        if jx == 0:
            pdata1 = People.query.filter(People.id == odat.Bid).first()
            date1 = odat.Date
            order = odat.Order
            date2 = odat.Date2
        dtest1 = odat.Date
        dtest2 = odat.Date2
        if dtest1 < date1:
            date1 = dtest1
        if dtest2 > date2:
            date2 = dtest2
        idat = Invoices.query.filter(Invoices.Jo == odat.Jo).order_by(Invoices.Ea.desc()).first()
        c1, c2 = odat.Company, odat.Company2
        c1, c2 = stripper(c1), stripper(c2)
        descr = 'From ' + c1 + ' to ' + c2
        keydata[jx] = [odat.Jo, odat.Booking, odat.Container, idat.Total, descr]
        grandtotal = grandtotal+float(idat.Total)
        print(keydata[jx])
        # put together the file paperwork

    file1 = f'tmp/{scac}/data/vpackages/P_' + 'test.pdf'
    cache2 = int(odat.Pkcache)
    docref = f'tmp/{scac}/data/vpackages/P_c'+str(cache2)+'_' + order + '.pdf'
    odat.Pkcache = cache2 + 1

    for jx, ix in enumerate(odervec):
        odat = Orders.query.get(ix)
        odat.Package = os.path.basename(docref)
        db.session.commit()

    import make_TP_invoice
    make_TP_invoice.main(file1, keydata, grandtotal, pdata1, date1, date2)

    filegather = ['pdfunite', addpath(file1)]
    for ix in odervec:
        odat = Orders.query.get(ix)
        filegather.append(addpath(f'tmp/{scac}/data/vinvoice/{odat.Invoice}'))

    filegather.append(addpath(docref))
    tes = subprocess.check_output(filegather)

    return docref
