from runmain import db
from models import Vehicles, Storage, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Proofs, Services
from flask import render_template, flash, redirect, url_for, session, logging, request

from viewfuncs import popjo, jovec, timedata, nonone, nononef, numcheck, newjo, init_storage_zero, init_storage_blank, sdiff, money12
from CCC_system_setup import myoslist, addpath, scac

import math
from decimal import Decimal
import datetime
import calendar
import os
import subprocess
import shutil
import re

def isoS():

    if request.method == 'POST':

        monsel,oder,peep,serv,invo,inco,cache,modata,modlink,fdata,invooder = init_storage_zero()
        invojo, filesel,docref,search11,search12,search21,search31 = init_storage_blank()
        leftscreen=1
        docref=' '
        err=['All is well', ' ', ' ', ' ', ' ']
        ldata=None
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        today=datetime.date.today()
        invodate=datetime.date.today()
        leftsize=10
        monvec=['Month', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monlvec=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

        match    =  request.values.get('Match')
        modify   =  request.values.get('Modify')
        vmod     =  request.values.get('Vmod')
        minvo    =  request.values.get('MakeI')
        mpack    =  request.values.get('MakeP')
        viewo    =  request.values.get('ViewO')
        viewi    =  request.values.get('ViewI')
        viewp    =  request.values.get('ViewP')
        analyze  =  request.values.get('Analyze')
        print    =  request.values.get('Print')
        addE     = request.values.get('addentity')
        addS     = request.values.get('addservice')
        recpay   = request.values.get('RecPay')
        hispay   = request.values.get('HisPay')
        monsel   = request.values.get('monsel')

        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        # hidden values
        update   =  request.values.get('Update')
        invoupdate = request.values.get('invoUpdate')
        recupdate = request.values.get('recUpdate')
        modlink =  request.values.get('passmodlink')
        emailnow = request.values.get('emailnow')
        emailinvo = request.values.get('emailInvo')
        newjob=request.values.get('NewJ')
        thisjob=request.values.get('ThisJob')

        oder=request.values.get('oder')
        invo=request.values.get('invo')
        invooder=request.values.get('invooder')
        cache=request.values.get('cache')
        peep=request.values.get('peep')
        serv=request.values.get('serv')
        inco=request.values.get('inco')

        modlink=nonone(modlink)
        oder=nonone(oder)
        invo=nonone(invo)
        invooder=nonone(invooder)
        peep=nonone(peep)
        serv=nonone(serv)
        monsel=nonone(monsel)
        inco=nonone(inco)
        modal=0

        if returnhit is not None:
            modlink=0
            invo=0
            invooder=0
            inco=0
# ____________________________________________________________________________________________________________________B.UpdateDatabases.Storage
        if update is not None and modlink==1:
            if oder > 0:
                modata=Storage.query.get(oder)
                desc=request.values.get('desc')
                amount=request.values.get('amount')
                thiscomp=request.values.get('thiscomp')
                dstart=request.values.get('dstart')
                balfwd=request.values.get('pybal')
                modata.Description=desc
                modata.Amount=amount
                modata.Date=dstart
                modata.BalFwd=balfwd
                ldat=People.query.filter(People.Company==thiscomp).first()
                if ldat is not None:
                    acomp=ldat.Company
                    aid=ldat.id
                else:
                    acomp=None
                    aid=None
                modata.Company=acomp
                modata.Pid=aid
                modata.Label=modata.Jo+' '+thiscomp+' '+amount
                db.session.commit()
                err[3]= 'Modification to Storage JO ' + modata.Jo + ' completed.'
                modlink=0
            if peep > 0:
                modata=People.query.get(peep)
                modata.Ptype='Storage'
                vals=['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3', 'idtype', 'tid', 'tel', 'email' , 'assoc1', 'assoc2', 'date1']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Company=a[0]
                modata.First=a[1]
                modata.Middle=a[2]
                modata.Last=a[3]
                modata.Addr1=a[4]
                modata.Addr2=a[5]
                modata.Addr3=a[6]
                modata.Idtype=a[7]
                modata.Idnumber=a[8]
                modata.Telephone=a[9]
                modata.Email=a[10]
                modata.Associate1=a[11]
                modata.Associate2=a[12]
                modata.Date1=a[13]
                db.session.commit()
                err=[' ', ' ', 'Modification to Entity ID ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0
                # And now update the crossover to Storage in case the Company info changed:
                cross=Storage.query.filter(Storage.Pid==peep)
                for cros in cross:
                    cros.Company=a[0]
                db.session.commit()

            if serv > 0:
                modata=Services.query.get(serv)
                vals=['service','price']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Service=a[0]
                modata.Price=a[1]
                db.session.commit()
                err=[' ', ' ', 'Modification to Services Data with ID ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0

            if inco > 0:
                modata=Income.query.get(inco)
                vals=['desc', 'recamount', 'custref', 'recdate']
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Description=a[0]
                modata.Amount=a[1]
                modata.Ref=a[2]
                modata.Date=a[3]
                db.session.commit()
                err=[' ', ' ', 'Modification to Income Data with ID ' + str(modata.id) + ' completed.', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.UpdateDatabases.Storage
# ____________________________________________________________________________________________________________________B.UpdateInvoice.Storage
        if invoupdate is not None and monsel!=0:
            leftsize=8
            odata1=Storage.query.get(invooder)
            invojo=popjo(invooder,monsel)
            ldata=Invoices.query.filter(Invoices.SubJo==invojo).all()
            invodate=request.values.get('invodate')
            total=0
            for data in ldata:
                iqty=request.values.get('qty'+str(data.id))
                iqty=nononef(iqty)
                data.Description=request.values.get('desc'+str(data.id))
                deach=request.values.get('cost'+str(data.id))
                if deach is not None:
                    deach="{:.2f}".format(float(deach))
                    amount=iqty*float(deach)
                else:
                    deach="{:.2f}".format(0.00)
                    amount=0.00
                total=total+amount
                amount="{:.2f}".format(amount)
                data.Qty=iqty
                data.Ea=deach
                data.Amount= amount
                data.Total=0.00
                data.Date=invodate
                db.session.commit()

            if total>0 and ldata is not None:
                for data in ldata:
                    data.Total="%0.2f" % total
                    db.session.commit()
                odata1.Amount="%0.2f" % total
                db.session.commit()

            #Remove zeros from invoice in case a zero was the mod
            Invoices.query.filter(Invoices.Qty==0).delete()
            db.session.commit()

            #Create invoice code for order
            err=[' ', ' ', 'Invoice created for Storage JO: '+invojo, ' ',  ' ']
            ldata=Invoices.query.filter(Invoices.SubJo==invojo).all()
# ____________________________________________________________________________________________________________________E.UpdateInvoice.Storage

        odata = Storage.query.order_by(Storage.Jo).all()
        cdata = People.query.filter(People.Ptype=='Storage').order_by(People.Company).all()
        sdata = Services.query.all()

        oder,peep,serv,numchecked = numcheck(3,odata,cdata,sdata,0,0,['oder','peep','serv'])

# ____________________________________________________________________________________________________________________E.SearchFilters.Storage

# ____________________________________________________________________________________________________________________B.EmailInvoice.Storage
        if emailinvo is not None:
            leftsize=10
            leftscreen=1
            modlink=0
            modata = Storage.query.get(invooder)
            invojo=popjo(invooder,monsel)
            ldata=Invoices.query.filter(Invoices.SubJo==invojo).order_by(Invoices.Ea.desc()).all()
            pdata1=People.query.filter(People.id==modata.Pid).first()
            ldat=Invoices.query.filter(Invoices.SubJo==invojo).first()
            if pdata1 is None:
                err=[' ', ' ', 'There is no Billing information for this selection', ' ',  ' ']
            else:
                email=pdata1.Email
                company=pdata1.Company
            docref=ldat.Original
            if 'vinvoice' not in docref:
                err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            else:
                if email is not None:
                    import invoice_mimemail_S
                    invoice_mimemail_S.main(invojo,docref,email,monsel,inco, company)
                    if inco == 0:
                        for data in ldata:
                            data.Status="E"
                            db.session.commit()
                    else:
                        for data in ldata:
                            data.Status="P"
                            db.session.commit()
            invooder=0
            invo=0
            inco=0

# ____________________________________________________________________________________________________________________E.EmailInvoice.Storage
# ____________________________________________________________________________________________________________________B.Viewers.Storage
        if viewo is not None and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder>0:
                modata=Storage.query.get(oder)
                if modata.Original is not None:
                    if len(modata.Original)>5:
                        docref=modata.Original
                        leftscreen=0
                        leftsize=8
                        modlink=0
                        err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if (viewo is not None or viewi is not None or viewp is not None) and numchecked!=1:
            err=['Must check exactly one box to use this option', ' ', ' ', ' ',  ' ']

        if viewi is not None and numchecked==1:
            err=['There is no document available for this selection', ' ', ' ', ' ',  ' ']
            if monsel==0:
                err[1]='Need to select the month'
            if oder>0 and monsel>0:
                invooder=oder
                modata=Storage.query.get(oder)
                invojo=popjo(oder,monsel)
                ldat=Invoices.query.filter(Invoices.SubJo==invojo).first()
                if ldat.Original is not None:
                    docref=ldat.Original
                    leftscreen=0
                    leftsize=8
                    modlink=5
                    err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Viewers.Storage
# ____________________________________________________________________________________________________________________B.ModifyEntries.Storage
        if (modify is not None or vmod is not None) and numchecked==1 :
            modlink=1
            leftsize=8

            if oder>0:
                modata=Storage.query.get(oder)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             docref=modata.Original
                             err=['All is well', ' ', ' ', ' ',  ' ']

            if serv>0:
                modata=Services.query.get(serv)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']

            if peep>0:
                modata=People.query.get(peep)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']


        if (modify is not None or vmod is not None) and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.ModifyEntries.Storage
# ____________________________________________________________________________________________________________________B.AddEntries.Storage

        if addS is not None and serv>0 and numchecked==1:
            leftsize=8
            modlink=2
            modata=Services.query.get(serv)

        if addS is not None and numchecked==0:
            leftsize=8
            modlink=1
            #We will create a blank line and simply modify that by updating:
            input= Services(Service='New', Price=0.00)
            db.session.add(input)
            db.session.commit()
            modata= Services.query.filter(Services.Service=='New').first()
            serv=modata.id
            err=[' ', ' ', 'Enter Data for New Service', ' ',  ' ']

        if addS is not None and numchecked>1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'

        if addE is not None and peep>0 and numchecked==1:
            leftsize=8
            modlink=3
            modata=People.query.get(peep)

        if addE is not None and numchecked==0:
            leftsize=8
            modlink=1
            #We will create a blank line and simply modify that by updating:
            input= People(Company='New', First='', Middle='', Last='', Addr1='', Addr2='', Addr3='', Idtype='', Idnumber='', Telephone='',
                          Email='', Associate1='', Associate2='', Date1=today, Date2=None, Original=None, Ptype='Storage', Temp1=None, Temp2=None)
            db.session.add(input)
            db.session.commit()
            modata= People.query.filter( (People.Company=='New') & (People.Ptype=='Storage') ).first()
            peep=modata.id
            modata.Company=''
            db.session.commit()
            modata=People.query.get(peep)
            err=[' ', ' ', 'Enter Data for New Company', ' ',  ' ']

        if addE is not None and numchecked>1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.AddEntries.Storage
# ____________________________________________________________________________________________________________________B.ReceivePayment.Storage

        if (recpay is not None and oder>0 and numchecked==1 and monsel>0) or recupdate is not None:
            leftsize=8
            if recpay is not None:
                invooder=oder
            odat = Storage.query.get(invooder)
            invojo=popjo(invooder,monsel)
            ldat=Invoices.query.filter(Invoices.SubJo==invojo).first()
            err=['Have no Invoice to Receive Against', ' ', ' ', ' ', ' ']
            if ldat is not None:
                invodate=ldat.Date
                if ldat.Original is not None:
                    docref=ldat.Original
                    leftscreen=0
                    leftsize=8

                incdat=Income.query.filter(Income.SubJo==invojo).first()
                if incdat is None:
                    err=['Creating New Payment on SubJo', ' ', ' ', ' ', ' ']
                    paydesc='Received payment on Invoice '+invojo+' for month of '+monvec[monsel]
                    recamount=str(ldat.Amount)
                    custref='ChkNo'
                    recdate=datetime.date(today.year, monsel, 28)
                    input= Income(Jo=odat.Jo,SubJo=invojo,Pid=odat.Pid,Description=paydesc,Amount=recamount,Ref=custref,Date=recdate,Original=None)
                    db.session.add(input)
                    payment=0
                else:
                    recamount=request.values.get('recamount')
                    custref=request.values.get('custref')
                    desc=request.values.get('desc')
                    recdate=request.values.get('recdate')
                    incdat.Amount=recamount
                    incdat.Ref=custref
                    incdat.Description=desc
                    incdat.Date=recdate
                db.session.commit()
                payment=[recamount,custref,recdate]

                modata= Income.query.filter(Income.SubJo==invojo).first()
                inco=modata.id
                err=[' ', ' ', 'Amend Payment for Invoice', ' ',  ' ']

                ldata=Invoices.query.filter(Invoices.SubJo==invojo).order_by(Invoices.Ea.desc()).all()
                pdata1=People.query.filter(People.id==odat.Pid).first()
                cache=nonone(odat.Cache)+1

                basejo=odat.Jo
                involine,paidline,refline,balline = money12(basejo)

                balduenow=balline[monsel]
                try:
                    balduenow=float[balduenow]
                except:
                    balduenow=0.00
                if balduenow<.001:
                    for data in ldata:
                        data.Status="P"
                        db.session.commit()

                import make_S_invoice
                make_S_invoice.main(odat,ldata,pdata1,invojo,involine,paidline,refline,balline,invodate,cache,payment)

                if cache>1:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                    # Store for future use
                else:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'

                odat.Cache=cache
                idat=Invoices.query.filter(Invoices.SubJo==invojo).first()
                idat.Original=docref
                db.session.commit()
                leftscreen=0
                err[4]='Viewing '+docref

        if recpay is not None and (oder==0 or numchecked!=1 or monsel==0):
            err=['Invalid selections:', '', '', '', '']
            if oder==0:
                err[1]='Must select a Storage Job'
            if numchecked!=1:
                err[2]='Must select exactly one Storage Job'
            if monsel==0:
                err[3]='Must select a month to apply payment'
# ____________________________________________________________________________________________________________________E.ReceivePayment.Storage
# ____________________________________________________________________________________________________________________B.PaymentHistory.Storage
        if hispay is not None or modlink==7:
            if oder==0 and invooder==0:
                err[1]='Must select a Storage Job'
            else:
                if oder != 0:
                    invooder=oder
                modata = Storage.query.get(invooder)
                ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.SubJo).all()
                fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.SubJo).all()
                #Check to see if we need to delete anything from history
                killthis=request.values.get('killthis')
                if killthis is not None and modlink==7:
                    for data in ldata:
                        testone = request.values.get('bill'+str(data.id))
                        if testone:
                            kill=int(testone)
                            Invoices.query.filter(Invoices.id == kill).delete()
                            db.session.commit()
                    for data in fdata:
                        testone = request.values.get('pay'+str(data.id))
                        if testone:
                            kill=int(testone)
                            Income.query.filter(Income.id == kill).delete()
                            db.session.commit()
                    ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.SubJo).all()
                    fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.SubJo).all()

                leftsize=8
                modlink=7
# ____________________________________________________________________________________________________________________E.PaymentHistory.Storage
# ____________________________________________________________________________________________________________________B.Delete.Storage
        if deletehit is not None and numchecked==1:
            if oder>0:
                Storage.query.filter(Storage.id == oder).delete()
                odata = Storage.query.all()
            if peep>0:
                People.query.filter(People.id == peep).delete()
                cdata = People.query.filter(People.Ptype=='Storage').order_by(People.Company).all()
            if serv>0:
                Services.query.filter(Services.id == serv).delete()
                sdata = Services.query.all()
            db.session.commit()
        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.Storage
# ____________________________________________________________________________________________________________________B.Invoicing.Storage
        if ((minvo is not None and oder>0) or invoupdate is not None) and monsel>0:
            err=['Could not create invoice', ' ', ' ', ' ',  ' ']
            # First time through: have an order to invoice
            if oder>0:
                invooder=oder
            myo=Storage.query.get(invooder)
            fee=myo.Amount
            #Check to see if we have the required data to make an invoice:
            invojo=popjo(invooder,monsel)
            thismonth=calendar.month_name[monsel]
            invodate = request.values.get('invodate')

            invo=1
            leftsize=8
            cache=nonone(myo.Cache)+1
            mys=Services.query.get(serv)
            if mys is not None:
                addserv=mys.Service
                price=mys.Price
                qty=1
                d = datetime.date(today.year, monsel, 1)
                descript='Monthly Storage Fee for Month of ' + thismonth
                input=Invoices(Jo=myo.Jo, SubJo=invojo, Pid=myo.Pid, Service=addserv, Description=descript, Ea=price, Qty=qty, Amount=price, Total=price, Date=d, Original=None, Status='New')
                db.session.add(input)
                db.session.commit()

            ldata=Invoices.query.filter(Invoices.SubJo==invojo).first()
            if ldata is None:
                invodate = datetime.date(today.year, monsel, 1)
                #See if there is an invoice from previous month to copy from
                try:
                    invojoprev=popjo(invooder,monsel-1)
                    invodate = datetime.date(today.year, monsel, 1)
                    ldata2=Invoices.query.filter(Invoices.SubJo==invojoprev).all()
                    for data in ldata2:
                        mydescript=data.Description
                        newdescript=data.Description
                        for i in range(12):
                            if monlvec[i] in newdescript:
                                j=i+1
                                if j==12:
                                    j=0
                                mydescript=newdescript.replace(monlvec[i],monlvec[j])

                        input=Invoices(Jo=myo.Jo, SubJo=invojo, Pid=myo.Pid, Service=data.Service, Description=mydescript, Ea=data.Ea, Qty=data.Qty, Amount=data.Amount, Date=invodate, Total=data.Total, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                except:
                    if mys is None:
                        addserv='Monthly Storage'
                        price=fee
                    else:
                        addserv=mys.Service
                        price=mys.Price

                    qty=1
                    invodate = datetime.date(today.year, monsel, 1)
                    descript='Monthly Storage Fee for Month of ' + thismonth
                    input=Invoices(Jo=myo.Jo, SubJo=invojo, Pid=myo.Pid, Service=addserv, Description=descript, Ea=price, Qty=qty, Amount=price, Date=invodate, Total=price, Original=None, Status='New')
                    db.session.add(input)
                    db.session.commit()
                else:
                    ldat=Invoices.query.filter(Invoices.SubJo==invojo).first()
                    if ldat is None:
                        if mys is None:
                            addserv='Monthly Storage'
                            price=fee
                        else:
                            addserv=mys.Service
                            price=mys.Price

                        qty=1
                        invodate = datetime.date(today.year, monsel, 1)
                        descript='Monthly Storage Fee for Month of ' + thismonth
                        input=Invoices(Jo=myo.Jo, SubJo=invojo, Pid=myo.Pid, Service=addserv, Description=descript, Ea=price, Qty=qty, Amount=price, Date=invodate, Total=price, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    ldat=Invoices.query.filter(Invoices.SubJo==invojo).first()
                    invodate=ldat.Date

            # If have ldata:
            err=[' ', ' ', 'Created invoice for JO= '+invojo, ' ',  ' ']

            ldata=Invoices.query.filter(Invoices.SubJo==invojo).order_by(Invoices.Ea.desc()).all()
            pdata1=People.query.filter(People.id==myo.Pid).first()

            odat=Storage.query.get(invooder)
            basejo=odat.Jo
            involine, paidline, refline, balline = money12(basejo)


            import make_S_invoice
            make_S_invoice.main(odat, ldata, pdata1, invojo,involine, paidline, refline, balline, invodate, cache, 0)

            if cache>1:
                docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                # Store for future use
            else:
                docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'


            odat.Path=docref
            odat.Cache=cache
            idat=Invoices.query.filter(Invoices.SubJo==invojo).first()
            idat.Original=docref
            db.session.commit()
            leftscreen=0
            err[4]='Viewing '+docref
            modata=Storage.query.get(invooder)
        elif minvo is not None and monsel==0:
            err=[' ', ' ', 'Choose a Month for the Invoice', ' ',  ' ']
        elif minvo is not None:
            err=[' ', ' ', 'Must select at least 1 Job for this selection', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Invoicing.Storage

# ____________________________________________________________________________________________________________________B.NewJob.Storage
        if newjob is not None:
            err=['Select Source Document from List']
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            modlink=4
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/NewJob.pdf'

        if newjob is None and modlink==4:
            filesel=request.values.get('FileSel')
            if filesel != '1':
                fdata = myoslist(f'tmp/{scac}/data/vunknown')
                leftsize=8
                leftscreen=0
                docref=f'tmp/{scac}/data/vunknown/'+filesel

        if thisjob is not None:
            modlink=0
            #Create the new database entry for the source document
            filesel=request.values.get('FileSel')
            if filesel != '1':
                docold=f'tmp/{scac}/data/vunknown/'+filesel
                docref=f'tmp/{scac}/data/vorders/'+filesel
                shutil.move(addpath(docold),addpath(docref))
            else:
                docref=''
            sdate=request.values.get('dstart')
            if sdate is None:
                sdate=today

            jtype='S'
            nextjo = newjo(jtype, sdate)

            thisdesc=request.values.get('thisdesc')
            thisamt=request.values.get('thisamt')
            thiscomp=request.values.get('thiscomp')
            pybal=request.values.get('pybal')
            ldat=People.query.filter(People.Company==thiscomp).first()
            if ldat is not None:
                acomp=ldat.Company
                aid=ldat.id
            else:
                acomp=None
                aid=None
            label = nextjo+' '+thiscomp+' '+thisamt
            input = Storage(Jo=nextjo,Description=thisdesc,BalFwd=pybal,Amount=thisamt,Status='New',Cache=1,Original=docref,Path=None,Pid=aid,Company=thiscomp,Date=sdate,Label=label)

            db.session.add(input)
            db.session.commit()
            modata=Storage.query.filter(Storage.Jo==nextjo).first()
            csize=People.query.filter(People.Ptype=='Storage').order_by(People.Company).all()
            oder=modata.id
            leftscreen=1
            err=['All is well', ' ', ' ', ' ',  ' ']
            odata = Storage.query.all()
# ____________________________________________________________________________________________________________________E.New Job.Storage
# ____________________________________________________________________________________________________________________B.Matching.Storage
        if match is not None:
            if oder>0 and peep>0 and numchecked==2:
                myo=Storage.query.get(oder)
                myp=People.query.get(peep)
                myo.Pid=peep
                myo.Company=myp.Company
                db.session.commit()
            if numchecked != 2:
                err[1]='Must select exactly 2 boxes to use this option.'
                err[0]=' '
# ____________________________________________________________________________________________________________________E.Matching.Storage

        # Create the time oriented data for the columns
        bm, cm = timedata(odata)
    #This is the else for 1st time through
    else:
# ____________________________________________________________________________________________________________________B.STORAGEnotPost

        odata = Storage.query.order_by(Storage.Jo).all()
        cdata = People.query.filter(People.Ptype=='Storage').order_by(People.Company).all()
        sdata = Services.query.all()
        ldata = None
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        invodate=today
        monsel,oder,peep,serv,invo,inco,cache,modata,modlink,fdata,invooder = init_storage_zero()
        invojo, filesel,docref,search11,search12,search21,search31 = init_storage_blank()
        monvec=['All', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        leftscreen=1
        leftsize=10
        docref=' '
        err=['All is well', ' ', ' ', ' ',  ' ']
        bm, cm = timedata(odata)
    docref=docref.replace('tmp/vinvoice',f'tmp/{scac}/data/vinvoice')
    return odata,cdata,sdata,oder,peep,serv,err,modata,modlink,fdata,today,inco,leftscreen,docref,leftsize,ldata,monsel,monvec,invo,invooder,invojo,cache,filesel,bm,cm,invodate
