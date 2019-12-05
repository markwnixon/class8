from runmain import db
from models import Invoices, People, Orders, Drops, OverSeas
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import subprocess
from CCC_system_setup import myoslist, addpath, addtxt, tpath, scac
from viewfuncs import nodollar, numcheckv, nonone


def updateinvo(jo, thisdate):
    idata = Invoices.query.filter(Invoices.Jo == jo).all()
    total = 0.0
    for idat in idata:
        each = float(idat.Qty)
        amtea = float(idat.Ea)
        amount = each*amtea
        idat.Amount = nodollar(amount)
        db.session.commit()
        total = total+amount
    for idat in idata:
        idat.Date = thisdate
        idat.Total = nodollar(total)
        db.session.commit()
    if jo[1] == 'T':
        ldata = Invoices.query.filter(Invoices.Jo == jo).order_by(Invoices.Ea.desc()).all()
        myo = Orders.query.filter(Orders.Jo == jo).first()
        cache = myo.Storage+1
        pdata1 = People.query.filter(People.id == myo.Bid).first()
        pdata2 = Drops.query.filter(Drops.id == myo.Lid).first()
        pdata3 = Drops.query.filter(Drops.id == myo.Did).first()

        from make_T_invoice import T_invoice
        T_invoice(myo, ldata, pdata1, pdata2, pdata3, cache, thisdate, 0)

        if cache > 1:
            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
            # Store for future use
        else:
            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'.pdf'

        for ldatl in ldata:
            ldatl.Pid = pdata1.id
            ldatl.Original = docref
            db.session.commit()

        myo.Path = docref
        myo.Storage = cache
        db.session.commit()

    if jo[1] == 'O':
        odat = OverSeas.query.filter(OverSeas.Jo == jo).first()
        invooder = odat.id
        cache = nonone(odat.Cache)+1
        from invoices import invoiceO
        invo, err, leftscreen, leftsize, docref, invodate = invoiceO(invooder, 0)

        if cache > 1:
            docref = f'tmp/{scac}/data/vinvoice/INV'+jo+'c'+str(cache)+'.pdf'
            # Store for future use
        else:
            docref = f'tmp/{scac}/data/vinvoice/INV'+jo+'.pdf'
        odat.Cache = cache
        modata = OverSeas.query.get(invooder)
        jo = modata.Jo
        booking = modata.Booking
        ldata = Invoices.query.filter(Invoices.Jo == jo).order_by(Invoices.Jo).all()


def isoInvM():

    if request.method == 'POST':
        # ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec

        # Zero and blank items for default
        username = session['username'].capitalize()
        cache = 0
        modata = 0
        modlink = 0
        docref = ''

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize = 10

        match = request.values.get('Match')
        modify = request.values.get('Qmod')
        vmod = request.values.get('Vmod')
        viewo = request.values.get('ViewO')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        delfile = request.values.get('DELF')
        # hidden values
        update = request.values.get('Update')
        newact = request.values.get('NewA')
        thisjob = request.values.get('ThisJob')
        oder = request.values.get('oder')
        modlink = request.values.get('modlink')

        oder = nonone(oder)
        modlink = nonone(modlink)

        leftscreen = 1
        err = ['All is well', ' ', ' ', ' ', ' ']

        if returnhit is not None:
            modlink = 0


# ____________________________________________________________________________________________________________________E.FormVariables.General
# ____________________________________________________________________________________________________________________B.DataUpdates.General

        if modlink == 1:
            if oder > 0:
                modata = Invoices.query.get(oder)
                vals = ['jo', 'subjo', 'pid', 'service', 'description', 'each',
                        'qty', 'amount', 'total', 'idate', 'original', 'status']
                a = list(range(len(vals)))
                for i, v in enumerate(vals):
                    a[i] = request.values.get(v)

                modata.Jo = a[0]
                modata.Subjo = a[1]
                modata.Pid = a[2]
                modata.Service = a[3]
                modata.Description = a[4]
                modata.Ea = a[5]
                modata.Qty = a[6]
                modata.Amount = a[7]
                modata.Total = a[8]
                modata.Date = a[9]
                modata.Original = a[10]
                modata.Status = a[11]
                db.session.commit()

                updateinvo(modata.Jo, modata.Date)

                err[3] = 'Modification to Invoices id ' + str(modata.id) + ' completed.'
                # if update is not None:
                #modlink = 0
                #leftsize = 10
                # else:
                leftsize = 6
                leftscreen = 0
                modata = Invoices.query.get(oder)
                fname = os.path.basename(modata.Original)
                docref = tpath('invo', fname)

# ____________________________________________________________________________________________________________________B.GetData.General
        odata = Invoices.query.all()
# ____________________________________________________________________________________________________________________B.Search.General

        if modlink == 0:
            oder, numchecked = numcheck(1, odata, 0, 0, 0, 0, ['oder'])

# ____________________________________________________________________________________________________________________E.Search.General

# ____________________________________________________________________________________________________________________B.Modify.General
        if (modify is not None or vmod is not None) and numchecked == 1:
            modlink = 1
            leftsize = 6
            if vmod is not None:
                leftscreen = 0

            if oder > 0:
                modata = Invoices.query.get(oder)
                if modata.Original is not None:
                    fname = os.path.basename(modata.Original)
                else:
                    fname = ''
                print('oder=', oder)
                print('jo=', modata.Jo)
                print('fname=', fname)

                # print('fname=',modata.Original)
                # fname=os.path.basename(modata.Original)

                docref = tpath('invo', fname)

        if (modify is not None or vmod is not None) and numchecked != 1:
            modlink = 0
            err[0] = ' '
            err[2] = 'Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.Modify.General

# ____________________________________________________________________________________________________________________B.Delete.General
        if deletehit is not None and numchecked >= 1:
            oderlist = numcheckv(odata)
            for oder in oderlist:
                modata = Invoices.query.get(oder)
                jo = modata.Jo
                Invoices.query.filter(Invoices.id == oder).delete()
                db.session.commit()
                updateinvo(jo, modata.Date)
            odata = Invoices.query.all()
        if deletehit is not None and numchecked != 1:
            err = [' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.General

    # This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder = 0
        cache = 0
        modata = 0
        modlink = 0
        odata = Invoices.query.all()
        leftscreen = 1
        leftsize = 10
        docref = ''
        err = ['All is well', ' ', ' ', ' ',  ' ']
    leftsize = 8

    return odata, oder, err, modata, modlink, leftscreen, leftsize, today, now, docref
