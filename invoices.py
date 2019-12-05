from runmain import db
from models import Invoices, People, OverSeas, Bookings, Services, Autos, Income, Moving
from flask import session, logging, request
import datetime
import calendar
import re


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.units import inch
import csv
import math
import shutil
from viewfuncs import d2s, dollar, avg, comporname, fullname, address, nononestr, nonone, nononef, parseline, commaguard, parselinenoupper
from CCC_system_setup import addpath, bankdata, scac


def invoiceO(ship, payment):
    today = datetime.datetime.today()
    myo = OverSeas.query.get(ship)
    # Check to see if we have the required data to make an invoice:
    pdat = People.query.get(myo.Pid)

    if pdat is not None:
        invo = 1
        leftsize = 8
        if myo.Cache is not None:
            cache = myo.Cache+1
        else:
            cache = 1

        # if no invoice has been created add all the basics:
        idat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
        if idat is None:
            descript = 'Job ' + myo.Jo+': ' + myo.Pol + ' to ' + myo.Pod
            try:
                total = myo.Charge.replace('$', '').replace(',', '')
                total = float(total)
            except:
                total = 0.00
            input = Invoices(Jo=myo.Jo, SubJo=None, Pid=0, Service='Overseas Shipping', Description=descript,
                             Ea=total, Qty=1, Amount=total, Total=total, Date=today, Original=None, Status='New')
            db.session.add(input)
            db.session.commit()

        # These are the services we wish to add to the invoice
        sdata = Services.query.order_by(Services.Price.desc()).all()
        total = 0
        for data in sdata:
            testone = request.values.get('serv'+str(data.id))
            if testone:
                servid = int(testone)
                mys = Services.query.get(servid)
                qty = 1
                total = total+mys.Price
                input = Invoices(Jo=myo.Jo, SubJo=None, Pid=myo.Pid, Service=mys.Service, Description='',
                                 Ea=mys.Price, Qty=qty, Amount=mys.Price, Total=None, Date=today, Original=None, Status='New')
                db.session.add(input)
                db.session.commit()

        adata = Autos.query.filter(Autos.Jo == myo.Jo).all()
        for data in adata:
            ihave = Invoices.query.filter(Invoices.SubJo == str(data.id)).first()
            if ihave is None:
                qty = 1
                towcost = data.TowCostEa

                if towcost is None:
                    data.TowCostEa = '0.00'
                    towcost = '0.00'

                towcharge = nononef(towcost)
                total = total+towcharge
                descript = data.Year+' '+data.Color+' '+data.Make+' '+data.Model+' VIN:'+data.VIN
                input = Invoices(Jo=myo.Jo, SubJo=str(data.id), Pid=myo.Pid, Service='Towing', Description=descript,
                                 Ea=towcharge, Qty=qty, Amount=towcharge, Total=None, Date=today, Original=None, Status='New')
                db.session.add(input)
                db.session.commit()

        total = 0.0
        ldata = Invoices.query.filter(Invoices.Jo == myo.Jo).all()
        for ldat in ldata:
            qty = float(ldat.Qty)
            each = float(ldat.Ea)
            amount = qty*each
            total = total+amount
            ldat.Amount = d2s(amount)
            db.session.commit()
        for ldat in ldata:
            ldat.Total = d2s(total)
            db.session.commit()

        ldat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
        if ldat is None:
            invo = 0
            leftsize = 10
            err = [' ', ' ', 'No services on invoice yet and none selected', ' ',  ' ']
        else:
            invo = 1
            leftsize = 8
            dt = ldat.Date
            invodate = ldat.Date.strftime('%m/%d/%Y')
            err = [' ', ' ', 'Created invoice for JO= '+myo.Jo, ' ',  ' ']
            ldata = Invoices.query.filter(Invoices.Jo == myo.Jo).order_by(Invoices.Ea.desc()).all()
            pdata1 = People.query.get(myo.Pid)
            pdata2 = People.query.get(myo.ExportID)
            pdata3 = People.query.get(myo.ConsigID)
            pdata4 = People.query.get(myo.NotifyID)

# _______________________________________________________________________________________________________________
            joborder = myo.Jo
            file1 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'.pdf')
            file2 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'c'+str(cache)+'.pdf')
            file3 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'c'+str(cache-1)+'.pdf')
            today = datetime.datetime.today().strftime('%m/%d/%Y')
            type = joborder[1]
            myb = Bookings.query.filter(myo.Booking == Bookings.Booking).first()
            if myb is not None:
                loadat1 = myo.Pol
                saildate = myb.SailDate.strftime('%m/%d/%Y')
                shipto1 = myo.Pod
                arrival = myb.EstArr.strftime('%m/%d/%Y')
                theline = myb.Line
                vessel = myb.Vessel
            else:
                loadat1 = myo.Pol
                saildate = 'TBD'
                shipto1 = myo.Pod
                arrival = 'TBD'
                theline = ' '
                vessel = ' '

            if payment != 0:
                try:
                    paydate = payment[2].strftime('%m/%d/%Y')
                except:
                    paydate = payment[2]

            billto = list(range(5))
            if pdata1 is not None:
                billto[0] = comporname(pdata1.Company, fullname(
                    pdata1.First, pdata1.Middle, pdata1.Last))
                billto[1] = nononestr(pdata1.Addr1)
                billto[2] = nononestr(pdata1.Addr2)
                billto[3] = nononestr(pdata1.Telephone)
                billto[4] = nononestr(pdata1.Email)
            else:
                for i in range(5):
                    billto[i] = ' '

            loadat = list(range(5))
            if pdata2 is not None:
                loadat[0] = parselinenoupper(loadat1, 34)
                loadat[1] = parselinenoupper('Depart Date: '+saildate, 28)
                loadat[2] = ' '
                loadat[3] = parselinenoupper(shipto1, 28)
                loadat[4] = parselinenoupper('Est. Arrival Date: '+arrival, 28)
            else:
                for i in range(5):
                    loadat[i] = ' '

            shipto = list(range(5))
            if pdata3 is not None:
                shipto[0] = comporname(pdata3.Company, fullname(
                    pdata3.First, pdata3.Middle, pdata3.Last))
                shipto[0] = shipto[0].title()
                shipto[1] = nononestr(pdata3.Addr1).title()
                shipto[2] = nononestr(pdata3.Addr2).title()
                shipto[3] = nononestr(pdata3.Telephone)
                shipto[4] = nononestr(pdata3.Email).lower()
            else:
                for i in range(5):
                    shipto[i] = ' '

            us = list(range(4))
            us[0] = 'FIRST EAGLE LOGISTICS INC'
            us[1] = '505 HAMPTON PARK BLVD UNIT O'
            us[2] = 'CAPITOL HEIGHTS MD  20743'
            us[3] = '301-516-3000  info@firsteaglelogistics.com'

            line1 = ['Booking #', 'Container No.', 'Ship', 'Via', 'Vessel', 'Terms']
            line2 = ['Quantity', 'Item Code', 'Description', 'Price Each', 'Amount']
            line3 = [myo.Booking, myo.Container, theline, myo.MoveType, vessel, 'Due Upon Receipt']

            note, bank = bankdata('FC')

            lab1 = 'Balance Due'
            lab2 = 'Add $39.00 for all international wires'

            ltm = 36
            rtm = 575
            ctrall = 310
            left_ctr = 170
            right_ctr = 480
            dl = 17.6
            tdl = dl*2
            hls = 530
            m1 = hls-dl
            m2 = hls-2*dl
            m3 = hls-3*dl
            m4 = hls-4*dl
            m5 = hls-18*dl
            m6 = hls-23*dl
            m7 = hls-27*dl
            fulllinesat = [m1, m2, m3, m4, m5, m6, m7]
            p1 = ltm+87
            p2 = ltm+168
            p3 = ctrall-25
            p4 = rtm-220
            p5 = rtm-120
            sds1 = [p1, p2, p3, p4, p5]
            n1 = ltm+50
            n2 = ltm+130
            n3 = rtm-140
            n4 = rtm-70
            sds2 = [n1, n2, n3, n4]
            q1 = ltm+180
            q2 = rtm-180
            sds3 = [q1, q2]
            bump = 2.5
            tb = bump*2

            c = canvas.Canvas(file1, pagesize=letter)
            c.setLineWidth(1)

            logo = addpath("tmp/pics/logo3.jpg")
            c.drawImage(logo, 185, 680, mask='auto')

            # Date and JO boxes
            dateline = m1+8.2*dl
            c.rect(rtm-150, m1+7*dl, 150, 2*dl, stroke=1, fill=0)
            c.line(rtm-150, dateline, rtm, dateline)
            c.line(rtm-75, m1+7*dl, rtm-75, m1+9*dl)

            ctm = 218
            c.rect(ltm, m1+dl, 175, 5*dl, stroke=1, fill=0)
            c.rect(ctm, m1+dl, 150, 5*dl, stroke=1, fill=0)
            c.rect(rtm-200, m1+dl, 200, 5*dl, stroke=1, fill=0)
            level1 = m1+5*dl
            c.line(ltm, level1, ltm+175, level1)
            c.line(ctm, level1, ctm+150, level1)
            c.line(rtm-200, level1, rtm, level1)

            for i in fulllinesat:
                c.line(ltm, i, rtm, i)
            for k in sds1:
                c.line(k, m1, k, m3)
            for l in sds2:
                c.line(l, m3, l, m5)
            for m in sds3:
                c.line(m, m6, m, m7)
            c.line(ltm, m1, ltm, m7)
            c.line(rtm, m1, rtm, m7)
            h1 = avg(m6, m7)-3
            c.line(q2, h1, rtm, h1)

            c.setFont('Helvetica-Bold', 24, leading=None)
            c.drawCentredString(rtm-75, dateline+1.5*dl, 'Invoice')

            c.setFont('Helvetica', 12, leading=None)

            c.drawCentredString(rtm-112.5, dateline+bump, 'Date')
            c.drawCentredString(rtm-37.7, dateline+bump, 'Invoice #')

            c.drawString(ltm+bump*3, m1+5*dl+bump*2, 'Bill To')
            c.drawString(ctm+bump*3, m1+5*dl+bump*2, 'Port to Port')
            c.drawString(rtm-200+bump*2, m1+5*dl+bump*2, 'Customer/Consignee')

            ctr = [avg(ltm, p1), avg(p1, p2), avg(p2, p3), avg(p3, p4), avg(p4, p5), avg(p5, rtm)]
            for j, i in enumerate(line1):
                c.drawCentredString(ctr[j], m2+tb, i)

            ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n3, n4), avg(n4, rtm)]
            for j, i in enumerate(line2):
                c.drawCentredString(ctr[j], m4+tb, i)

            dh = 12
            ct = 305
            top = m6-1.5*dh
            for i in bank:
                c.drawCentredString(ct, top, i)
                top = top-dh

            top = m1+9*dl-5
            for i in us:
                c.drawString(ltm+bump, top, i)
                top = top-dh

            bottomline = m6-23
            c.setFont('Helvetica-Bold', 12, leading=None)
            c.drawString(q2+tb, bottomline, 'Balance Due:')

            c.setFont('Helvetica', 10, leading=None)
            c.drawCentredString(avg(q2, rtm), m7+12, 'Add $39.00 for all international wires')

            c.setFont('Times-Roman', 9, leading=None)
            dh = 9.95
            top = m5-dh
            for j, i in enumerate(note):
                c.drawString(ltm+tb, top, note[j])
                top = top-dh

# _______________________________________________________________________
    # Insert data here
# _______________________________________________________________________

            c.setFont('Helvetica', 10, leading=None)

            dh = 13
            top = level1-dh
            lft = ltm+bump*3
            for i in billto:
                i = i.title()
                c.drawString(lft, top, i)
                top = top-dh

            top = level1-dh
            lft = ctm+bump*3
            for i in loadat:
                for k in i:
                    c.drawString(lft, top, k)
                    top = top-dh

            top = level1-dh
            lft = rtm-205+bump*3
            for i in shipto:
                c.drawString(lft, top, i)
                top = top-dh

            x = avg(rtm-75, rtm)
            y = dateline-dh-bump
            c.drawCentredString(x, y, joborder)
            x = avg(rtm-75, rtm-150)
            c.drawCentredString(x, y, invodate)

            c.setFont('Helvetica', 9, leading=None)

            ctr = [avg(ltm, p1), avg(p1, p2), avg(p2, p3), avg(p3, p4), avg(p4, p5), avg(p5, rtm)]
            for j, i in enumerate(line3):
                c.drawCentredString(ctr[j], m3+tb, i)

            total = 0
            top = m4-dh
            for data in ldata:
                qty = data.Qty
                if qty != -1:
                    qty = int(nonone(data.Qty))
                    each = float(nonone(data.Ea))
                    subtotal = qty*each
                    if subtotal == 0:
                        sqty = ''
                        theservice = 'Included/NoTow'
                        theeach = ''
                        thesubtotal = ''
                    else:
                        sqty = str(qty)
                        theservice = data.Service
                        theeach = dollar(each)
                        thesubtotal = dollar(subtotal)

                    total = total+subtotal
                    line4 = [sqty, theservice]
                    line5 = nononestr(data.Description)
                    line6 = [theeach, thesubtotal]

                    ctr = [avg(ltm, n1), avg(n1, n2)]
                    for j, i in enumerate(line4):
                        c.drawCentredString(ctr[j], top, i)

                    c.drawString(n2+tb, top, line5)

                    ctr = [n4-tb*2, rtm-tb*2]
                    for j, i in enumerate(line6):
                        c.drawRightString(ctr[j], top, i)

                    top = top-dh

            if payment != 0:
                c.setFont('Helvetica-Bold', 18, leading=None)
                c.drawCentredString(ct, top-2*dh, 'Payment Received')

            if payment != 0:
                c.setFont('Helvetica-Bold', 12, leading=None)

                try:
                    thispay = dollar(float(payment[0]))
                except:
                    thispay = '$0.00'

                # dollar(float(payment[0]))

                top = top-4*dh
                try:
                    c.drawString(n2+bump, top, 'Your payment of '+thispay+', Ref No. '+payment[1])
                except:
                    c.drawString(ct, top, 'There is no payment data as of yet')
                try:
                    c.drawString(n2+bump, top-dh, 'was applied on ' + paydate)
                except:
                    c.drawString(ct, top-dh, 'There is a problem with the date')

                thispay = nononef(thispay)

            else:
                thispay = 0.00

            baldue = total-thispay

            c.drawRightString(rtm-tb*2, bottomline, dollar(baldue))

            c.showPage()
            c.save()
            #
            # Now make a cache copy
            shutil.copy(file1, file2)
            try:
                shutil.move(file3, file1)
            except:
                err = 'No file there'


# _______________________________________________________________________________________________________________
            if cache > 1:
                docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
                # Store for future use
            else:
                docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'.pdf'

            if payment == 0:
                for ldatl in ldata:
                    ldatl.Pid = pdata1.id
                    ldatl.Original = docref
                    db.session.commit()
                myo.Ipath = docref

            myo.Cache = cache
            db.session.commit()
            leftscreen = 0
            #err[4]='Viewing '+docref

    return invo, err, leftscreen, leftsize, docref, dt
# ________________________________________________________________________________________________________________________________________________
# ________________________________________________________________________________________________________________________________________________


def invoiceM(oder, payment):

    myo = Moving.query.get(oder)
    today = datetime.datetime.today()
    # Check to see if we have the required data to make an invoice:
    pdata1 = People.query.filter((People.Company == myo.Shipper) &
                                 (People.Ptype == 'Moving')).first()
    if pdata1 is not None:
        invo = 1
        leftsize = 8
        cache = myo.Cache+1

        # These are the services we wish to add to the invoice
        sdata = Services.query.order_by(Services.Price.desc()).all()
        total = 0
        for data in sdata:
            testone = request.values.get('serv'+str(data.id))
            if testone:
                servid = int(testone)
                mys = Services.query.get(servid)
                qty = 1
                total = total+mys.Price
                input = Invoices(Jo=myo.Jo, SubJo=None, Pid=0, Service=mys.Service, Description=' ', Ea=mys.Price,
                                 Qty=qty, Amount=myo.Amount, Total=myo.Amount, Date=today, Original=None, Status='New')
                db.session.add(input)
                db.session.commit()

        idat = Invoices.query.filter(Invoices.Jo == myo.Jo).first()
        if idat is None:
            descript = 'Job Order ' + myo.Jo + ' Moving from ' + myo.Drop1 + ' to ' + myo.Drop2
            total = myo.Amount
            input = Invoices(Jo=myo.Jo, SubJo=None, Pid=0, Service='Moving Services', Description=descript,
                             Ea=myo.Amount, Qty=1, Amount=myo.Amount, Total=myo.Amount, Date=today, Original=None, Status='New')
            db.session.add(input)
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
            dt = ldat.Date
            err = [' ', ' ', 'Created invoice for JO= '+myo.Jo, ' ',  ' ']
            ldata = Invoices.query.filter(Invoices.Jo == myo.Jo).order_by(Invoices.Ea.desc()).all()
            pdata1 = People.query.filter(People.Company == myo.Shipper).first()

        joborder = myo.Jo
        file1 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'c0.pdf')
        file2 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'c'+str(cache)+'.pdf')
        file3 = addpath(f'tmp/{scac}/data/vinvoice/INV'+joborder+'c'+str(cache-1)+'.pdf')
        today = datetime.datetime.today().strftime('%m/%d/%Y')
        type = joborder[1]
        if invodate is None or invodate == 0:
            invodate = today
        else:
            invodate = invodate.strftime('%m/%d/%Y')

        date1 = myo.Date.strftime('%m/%d/%Y')
        date2 = myo.Date2.strftime('%m/%d/%Y')

        if payment != 0:
            try:
                paydate = payment[2].strftime('%m/%d/%Y')
            except:
                paydate = payment[2]

        billto = list(range(5))
        if pdata1 is not None:
            billto[0] = comporname(pdata1.Company, fullname(
                pdata1.First, pdata1.Middle, pdata1.Last))
            billto[1] = nononestr(pdata1.Addr1)
            billto[2] = nononestr(pdata1.Addr2)
            billto[3] = nononestr(pdata1.Telephone)
            billto[4] = nononestr(pdata1.Email)
        else:
            for i in range(5):
                billto[i] = ' '

        loadat = [' ']*5
        p2 = myo.Dropblock1
        p2 = p2.splitlines()
        for j, p in enumerate(p2):
            if j < 5:
                loadat[j] = p.title()

        shipto = [' ']*5
        p2 = myo.Dropblock2
        p2 = p2.splitlines()
        for j, p in enumerate(p2):
            if j < 5:
                shipto[j] = p.title()

        us = list(range(4))
        us[0] = 'FIRST EAGLE LOGISTICS INC'
        us[1] = '505 HAMPTON PARK BLVD UNIT O'
        us[2] = 'CAPITOL HEIGHTS MD  20743'
        us[3] = '301-516-3000  info@firsteaglelogistics.com'

        line1 = ['No. Stops', 'Terms', 'Job Start', 'Job Finish', 'Bill of Lading', 'Container No.']
        line2 = ['Quantity', 'Item Code', 'Description', 'Price Each', 'Amount']
        time1 = date1+' '+nononestr(myo.Time)
        time2 = date2+' '+nononestr(myo.Time2)
        due = 'Due Upon Receipt'
        bol = myo.BOL
        if len(bol) < 2:
            bol = myo.Jo

        line3 = [myo.Booking, due, time1, time2, bol, myo.Container]

        note, bank = bankdata('FC')

        lab1 = 'Balance Due'
        lab2 = 'Add $39.00 for all international wires'

        ltm = 36
        rtm = 575
        ctrall = 310
        left_ctr = 170
        right_ctr = 480
        dl = 17.6
        tdl = dl*2
        hls = 530
        m1 = hls-dl
        m2 = hls-2*dl
        m3 = hls-3*dl
        m4 = hls-4*dl
        m5 = hls-18*dl
        m6 = hls-23*dl
        m7 = hls-27*dl
        fulllinesat = [m1, m2, m3, m4, m5, m6, m7]
        p1 = ltm+87
        p2 = ltm+180
        p3 = ctrall
        p4 = rtm-180
        p5 = rtm-100
        sds1 = [p1, p2, p3, p4, p5]
        n1 = ltm+58
        n2 = ltm+128
        n3 = rtm-140
        n4 = rtm-70
        sds2 = [n1, n2, n3, n4]
        q1 = ltm+180
        q2 = rtm-180
        sds3 = [q1, q2]
        bump = 2.5
        tb = bump*2

        c = canvas.Canvas(file1, pagesize=letter)
        c.setLineWidth(1)

        logo = addpath("tmp/pics/logo3.jpg")
        c.drawImage(logo, 185, 680, mask='auto')

        # Date and JO boxes
        dateline = m1+8.2*dl
        c.rect(rtm-150, m1+7*dl, 150, 2*dl, stroke=1, fill=0)
        c.line(rtm-150, dateline, rtm, dateline)
        c.line(rtm-75, m1+7*dl, rtm-75, m1+9*dl)

        # Address boxes
        ctm = 218
        c.rect(ltm, m1+dl, 175, 5*dl, stroke=1, fill=0)
        c.rect(ctm, m1+dl, 175, 5*dl, stroke=1, fill=0)
        c.rect(rtm-175, m1+dl, 175, 5*dl, stroke=1, fill=0)
        level1 = m1+5*dl
        c.line(ltm, level1, ltm+175, level1)
        c.line(ctm, level1, ctm+175, level1)
        c.line(rtm-175, level1, rtm, level1)

        for i in fulllinesat:
            c.line(ltm, i, rtm, i)
        for k in sds1:
            c.line(k, m1, k, m3)
        for l in sds2:
            c.line(l, m3, l, m5)
        for m in sds3:
            c.line(m, m6, m, m7)
        c.line(ltm, m1, ltm, m7)
        c.line(rtm, m1, rtm, m7)
        h1 = avg(m6, m7)-3
        c.line(q2, h1, rtm, h1)

        c.setFont('Helvetica-Bold', 24, leading=None)
        c.drawCentredString(rtm-75, dateline+1.5*dl, 'Invoice')

        c.setFont('Helvetica', 11, leading=None)

        c.drawCentredString(rtm-112.5, dateline+bump, 'Date')
        c.drawCentredString(rtm-37.7, dateline+bump, 'Invoice #')

        c.drawString(ltm+bump*3, m1+5*dl+bump*2, 'Bill To')
        c.drawString(ctm+bump*3, m1+5*dl+bump*2, 'Load At')
        c.drawString(rtm-170+bump*2, m1+5*dl+bump*2, 'Delv To')

        ctr = [avg(ltm, p1), avg(p1, p2), avg(p2, p3), avg(p3, p4), avg(p4, p5), avg(p5, rtm)]
        for j, i in enumerate(line1):
            c.drawCentredString(ctr[j], m2+tb, i)

        ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n3, n4), avg(n4, rtm)]
        for j, i in enumerate(line2):
            c.drawCentredString(ctr[j], m4+tb, i)

        dh = 12
        ct = 305

        top = m6-1.5*dh
        for i in bank:
            c.drawCentredString(ct, top, i)
            top = top-dh

        top = m1+9*dl-5
        for i in us:
            c.drawString(ltm+bump, top, i)
            top = top-dh

        bottomline = m6-23
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(q2+tb, bottomline, 'Balance Due:')

        c.setFont('Helvetica', 10, leading=None)
        c.drawCentredString(avg(q2, rtm), m7+12, 'Add $39.00 for all international wires')

        c.setFont('Times-Roman', 9, leading=None)
        j = 0
        dh = 9.95
        top = m5-dh
        for i in note:
            c.drawString(ltm+tb, top, note[j])
            j = j+1
            top = top-dh


# _______________________________________________________________________
    # Insert data here
# _______________________________________________________________________

        c.setFont('Helvetica', 12, leading=None)

        dh = 13
        top = level1-dh
        lft = ltm+bump*3
        for i in billto:
            c.drawString(lft, top, i)
            top = top-dh

        top = level1-dh
        lft = ctm+bump*3
        for i in loadat:
            c.drawString(lft, top, i)
            top = top-dh

        top = level1-dh
        lft = rtm-175+bump*3
        for i in shipto:
            c.drawString(lft, top, i)
            top = top-dh

        x = avg(rtm-75, rtm)
        y = dateline-dh-bump
        c.drawCentredString(x, y, joborder)
        x = avg(rtm-75, rtm-150)
        c.drawCentredString(x, y, invodate)

        c.setFont('Helvetica', 9, leading=None)

        j = 0
        for i in line3:
            ctr = [avg(ltm, p1), avg(p1, p2), avg(p2, p3), avg(p3, p4), avg(p4, p5), avg(p5, rtm)]
            c.drawCentredString(ctr[j], m3+tb, i)
            j = j+1

        total = 0
        top = m4-dh
        for data in ldata:
            qty = float(data.Qty)
            each = float(data.Ea)
            subtotal = qty*each
            total = total+subtotal
            line4 = [str(qty), data.Service]
            line5 = nononestr(data.Description)
            line5lines = line5.splitlines()
            line6 = [each, subtotal]

            j = 0
            for i in line4:
                ctr = [avg(ltm, n1), avg(n1, n2)]
                c.drawCentredString(ctr[j], top, i)
                j = j+1

            j = 0
            for i in line6:
                ctr = [n4-tb*2, rtm-tb*2]
                c.drawRightString(ctr[j], top, dollar(i))
                j = j+1

            for line in line5lines:
                c.drawString(n2+tb, top, line)
                top=top-dh

            #top = top-dh

        if payment != 0:
            c.setFont('Helvetica-Bold', 18, leading=None)
            c.drawCentredString(ct, top-2*dh, 'Payment Received')

        if payment != 0:
            c.setFont('Helvetica-Bold', 12, leading=None)

            try:
                thispay = nononef(payment[0])
            except:
                thispay = 0.00

            top = top-4*dh
            try:
                c.drawString(n2+bump, top, 'Your payment of '+payment[0]+', Ref No. '+payment[1])
            except:
                c.drawString(ct, top, 'There is no payment data as of yet')
            try:
                c.drawString(n2+bump, top-dh, 'was applied on ' + paydate)
            except:
                c.drawString(ct, top-dh, 'There is a problem with the date')
        else:
            thispay = 0.00

        total = total-thispay

        c.drawRightString(rtm-tb*2, bottomline, dollar(total))

        c.showPage()
        c.save()
        #
        try:
            # Now make a cache copy
            shutil.copy(file1, file2)
        except:
            print('Could not find',file1,file2)
            # Remove old cache company
        try:
            shutil.move(file3, file1)
        except:
            print('Could not find', file3, file1)

        if cache > 1:
            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
            # Store for future use
        else:
            docref = f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c0.pdf'

        if payment == 0:
            for ldatl in ldata:
                ldatl.Pid = pdata1.id
                ldatl.Original = docref
                db.session.commit()
            myo.Path = docref

        myo.Cache = cache
        db.session.commit()

    return invo, err, docref, leftsize, dt
