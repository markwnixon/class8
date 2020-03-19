from runmain import db
from models import Vehicles, Storage, Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas
from models import Autos, People, Interchange, Drivers, ChalkBoard, Services, Moving, Drops
from flask import session, logging, request
import datetime
import calendar
import re
import os
from CCC_system_setup import myoslist, addpath, scac

def isoM():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.Moving

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef, init_truck_zero
        from viewfuncs import numcheck, numcheckv, sdiff, calendar7_weeks, viewbuttons, get_ints, containersout, dropupdate

        #Zero and blank items for default
        username = session['username'].capitalize()
        oder,poof,tick,serv,peep,invo,cache,modata,modlink,stayslim,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks = init_truck_zero()
        filesel=''
        docref=''
        doctxt=''

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=10
        howapp=0
        newc='Not found at top'

        match,modify,vmod,minvo,mpack,viewo,viewi,viewp,print,addE,addS,slim,stayslim,unslim,limitptype,returnhit,deletehit,update,invoupdate,emailnow,emailinvo,newjob,thisjob,recpay,hispay,recupdate,calendar,calupdate=viewbuttons()
        emailnow2=request.values.get('emailnow2')
        emailinvo2=request.values.get('emailInvo2')
        addI=request.values.get('addinterchange')
        copy = request.values.get('copy')
        datatable1=request.values.get('datatable1')
        datatable2=request.values.get('datatable2')
        unpay = request.values.get('unpay')
        dlist=[datatable1,datatable2]

        holdvec=[0]*3
        oder,poof,tick,serv,peep,invo,invooder,cache,modlink = get_ints()

        leftscreen=1
        err=['All is well', ' ', ' ', ' ', ' ']
        ldata=None

        if returnhit is not None:
            modlink=0
            invo=0
            invooder=0
            inco=0

# ____________________________________________________________________________________________________________________E.FormVariables.Moving
# ____________________________________________________________________________________________________________________B.DataUpdates.Moving
        if update is not None and ((modlink==4 and peep > 0) | modlink==30):
            modata=People.query.get(peep)
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
            err=[' ', ' ', 'Modification to Entity ID ' + str(modata.id) + ' completed.', ' ',  ' ']
            db.session.commit()
            peep=0
            modlink=0
            invo=0
            invooder=0
            inco=0


        if update is not None and modlink==2:
            modata=Services.query.get(serv)
            vals=['service', 'price']
            a=list(range(len(vals)))
            i=0
            for v in vals:
                a[i]=request.values.get(v)
                i=i+1
            input= Services(Service=a[0], Price=a[1])
            db.session.add(input)
            db.session.commit()
            err=[' ', ' ', 'New Service Added to Database.', ' ',  ' ']
            modlink=0
            serv=0
            invo=0
            invooder=0
            inco=0

        if update is not None and modlink==1:
            if oder > 0:
                modata=Moving.query.get(oder)
                vals=['load','order','bol','booking','container','pickup','date','time','date2','time2','amount']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                dropblock1=request.values.get('dropblock1')
                dropblock2=request.values.get('dropblock2')
                shipper=request.values.get('shipper')
                drop1=dropupdate(dropblock1)
                drop2=dropupdate(dropblock2)
                modata.Shipper=shipper
                pdat=People.query.filter((People.Company==shipper) & (People.Ptype=='Moving')).first()
                if pdat is not None:
                    pid=pdat.id
                else:
                    pid=0
                modata.Pid=pid
                modata.Dropblock2=dropblock2
                modata.Dropblock1=dropblock1
                modata.Load=a[0]
                modata.Order=a[1]
                modata.BOL=a[2]
                modata.Booking=a[3]
                modata.Container=a[4]
                modata.Pickup=a[5]

                modata.Drop1=drop1
                modata.Drop2=drop2

                try:
                    modata.Date=a[6]
                except:
                    modata.Date=None
                    err[5]='Bad Date Value'
                modata.Time=a[7]
                try:
                    modata.Date2=a[8]
                except:
                    modata.Date2=None
                    err[5]='Bad Date Value'
                modata.Time2=a[9]
                modata.Amount=a[10]
                try:
                    modata.Label=modata.Jo+' '+a[1]+' '+shipper+' '+ a[10]
                except:
                    modata.Label=modata.Jo+' '+shipper

                db.session.commit()
                err[3]= 'Modification to Moving JO ' + modata.Jo + ' completed.'
                modlink=0

            if poof > 0:
                modata=Proofs.query.get(poof)
                vals=['order','bol','container','booking','company','location','proofdate','prooftime']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Order=a[0]
                modata.BOL=a[1]
                modata.Container=a[2]
                modata.Booking=a[3]
                modata.Company=a[4]
                modata.Location=a[5]
                modata.Date=a[6]
                modata.Time=a[7]
                db.session.commit()
                err=[' ', ' ', 'Modification to Proof ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0

            if tick > 0:
                modata=Interchange.query.get(tick)
                vals=['intcontainer', 'intdate', 'inttime', 'chassis', 'release', 'truck', 'grosswt', 'driver', 'type']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Container=a[0]
                modata.Date=a[1]
                modata.Time=a[2]
                modata.Chassis=a[3]
                modata.Release=a[4]
                modata.TruckNumber=a[5]
                modata.GrossWt=a[6]
                modata.Driver=a[7]
                modata.Type=a[8]
                modata.Status='BBBBBB'
                db.session.commit()
                err=[' ', ' ', 'Modification to Interchange Ticket with ID ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0

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

            if peep > 0:
                modata=People.query.get(peep)
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
                err=[' ', ' ', 'Modification to Entity ID ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0
                db.session.commit()

            modlink=0
            oder=0
            peep=0
            serv=0
            invo=0
            invooder=0
            inco=0
# ____________________________________________________________________________________________________________________E.DataUpdates.Moving
# ____________________________________________________________________________________________________________________B.InvoiceUpdate.Moving

        if invoupdate is not None:
            leftsize=8
            odata1=Moving.query.get(invooder)
            invodate=request.values.get('invodate')
            if invodate is None:
                invodate=today
            if isinstance(invodate, str):
                invodate=datetime.datetime.strptime(invodate, '%Y-%m-%d')
            ldata=Invoices.query.filter(Invoices.Jo==odata1.Jo).all()
            itotal=0
            icode=''
            for data in ldata:
                iqty=request.values.get('qty'+str(data.id))
                iqty=nononef(iqty)
                data.Description=request.values.get('desc'+str(data.id))
                deach=request.values.get('cost'+str(data.id))
                if deach is not None:
                    damount=float(iqty)*float(deach)
                    itotal=itotal+damount
                    deach="{:.2f}".format(float(deach))
                    damount="{:.2f}".format(damount)
                else:
                    damount="{:.2f}".format(0.00)
                    deach="{:.2f}".format(0.00)
                data.Qty=iqty
                data.Ea=deach
                icode=icode+'+'+str(data.Qty)+'*'+str(data.Ea)
                data.Amount=damount
                data.Date=invodate
                db.session.commit()

            for data in ldata:
                data.Total=itotal
                db.session.commit()


            #Remove zeros from invoice in case a zero was the mod
            Invoices.query.filter(Invoices.Qty==0).delete()
            db.session.commit()
            #Create invoice code for order
            err=[' ', ' ', 'Invoice created for JO: '+odata1.Jo, ' ',  ' ']

            odata1.Delivery=icode
            odata1.Amount=itotal
            odata1.Status='Invoiced'
            myp=Proofs.query.filter(Proofs.Order==odata1.Order).first()
            if myp is not None:
                myp.Status='Invoiced'

            db.session.commit()
# ____________________________________________________________________________________________________________________E.InvoiceUpdate.Moving
# ____________________________________________________________________________________________________________________B.GetData.Moving
        odata = Moving.query.order_by(Moving.Jo.desc()).all()
        sdata = Services.query.order_by(Services.Price.desc()).all()
        cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()
# ____________________________________________________________________________________________________________________E.GetData.Moving
# ____________________________________________________________________________________________________________________B.Search.Moving

        if modlink<10:
            oder=0
            serv=0
            peep=0
            oder,serv,peep,numchecked=numcheck(3,odata,sdata,cdata,0,0,['oder','serv','peep'])

# ____________________________________________________________________________________________________________________E.Search.Moving
# ____________________________________________________________________________________________________________________B.Package.Moving

        if mpack is not None and numchecked==1:
            err=['Must have order, proof and invoice complete to make this selection', ' ', ' ', ' ',  ' ']
            if oder>0:
                odata1 = Moving.query.get(oder)
                ofile=odata1.Original
                if ofile is None:
                    err[2]='No original order data'
                else:
                    docref1 = f'tmp/{scac}/data/vorders/' + odata1.Original
                docref3 = odata1.Path
                if docref3 is None:
                    err[4]='No Invoice data'
            else:
                err[1]='No Order data'
            if oder>0  and docref3 and ofile:
                err=['Step 1: Sign the package', ' ', ' ', ' ',  ' ']
                invooder=oder
                leftscreen=0
                leftsize=8
                modlink=0
                cache2 = int(odata1.Detention)
                cache2=cache2+1
                #sandiwich it all together
                docref=f'tmp/{scac}/data/vorders/P_c'+str(cache2)+'_' + odata1.Original
                tes=subprocess.check_output(['pdfunite', docref1, docref3, docref])
                odata1.Detention=cache2
                db.session.commit()

# ____________________________________________________________________________________________________________________E.Package.Moving
# ____________________________________________________________________________________________________________________B.Package2.Moving

        if mpack is not None and numchecked>1:
            err=['Combining Invoices for Summary Invoice', ' ', ' ', ' ',  ' ']
            odervec=numcheckv(subdata1)
            keydata=[0]*len(odervec)
            grandtotal=0
            for j, i in enumerate(odervec):
                odat=Moving.query.get(i)
                if j==0:
                    pdata1=People.query.filter(People.id==odat.Bid).first()
                    date1=odat.Date
                    order=odat.Order
                date2=odat.Date2
                idat=Invoices.query.filter(Invoices.Jo==odat.Jo).order_by(Invoices.Ea.desc()).first()
                keydata[j]=[odat.Jo, odat.Booking, odat.Container, idat.Total, idat.Description]
                grandtotal=grandtotal+float(idat.Total)
                # put together the file paperwork

            file1=f'tmp/{scac}/data/vinvoice/P_' + 'test.pdf'
            cache2 = int(odat.Detention)
            cache2=cache2+1
            docref=f'tmp/{scac}/data/vinvoice/P_c'+str(cache2)+'_' + order + '.pdf'

            for j, i in enumerate(odervec):
                odat=Moving.query.get(i)
                odat.Location=docref
                db.session.commit()


            import make_TP_invoice
            make_TP_invoice.main(file1,keydata,grandtotal,pdata1,date1,date2)

            invooder=oder
            leftscreen=0
            leftsize=8
            modlink=0

            filegather=['pdfunite', file1]
            for i in odervec:
                odat=Moving.query.get(i)
                filegather.append(odat.Path)

            filegather.append(docref)
            tes=subprocess.check_output(filegather)

            odat.Detention=cache2
            db.session.commit()

# ____________________________________________________________________________________________________________________E.Package2.Moving
# ____________________________________________________________________________________________________________________B.Email.Moving

        if emailnow is not None or emailnow2 is not None:
            leftscreen=1
            leftsize=10
            modlink=0
            odata1 = Moving.query.get(invooder)
            docref = odata1.Location
            order = odata1.Order
            if emailnow2 is not None:
                emailin='export@firsteaglelogistics.com'
            else:
                pdat=People.query.get(odata1.Bid)
                emailin=str(pdat.Email)
            #If ready to email then we want a permanent copy and get rid of old:
            odata1.Status='InvoEml'
            db.session.commit()
            import invoice_mimemail
            invoice_mimemail.main(order,docref,emailin)
            invo=0
            invooder=0
            err[1]='Successful email to: ' + emailin

        if emailinvo is not None or emailinvo2 is not None:
            leftsize=10
            leftscreen=1
            modlink=0
            modata = Moving.query.get(invooder)
            ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Ea.desc()).all()
            jo=modata.Jo
            pdata1=People.query.get(modata.Bid)
            if pdata1 is None:
                err=[' ', ' ', 'There is no Billing information for this selection', ' ',  ' ']
            else:
                emailin=str(pdata1.Email)

            if emailinvo2 is not None:
                emailin='export@firsteaglelogistics.com'

            docref=modata.Path
            if 'vinvoice' not in docref:
                err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            else:
                if emailin is not None:
                    import invoice_mimemail2
                    invoice_mimemail2.main(jo,docref,emailin)
                    err[1]='Successful email to: '+emailin
            invo=0
            invooder=0
# ____________________________________________________________________________________________________________________E.Email.Moving
# ____________________________________________________________________________________________________________________B.Views.Moving

        if viewo is not None and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder>0:
                modata=Moving.query.get(oder)
                if modata.Original is not None:
                    dot=modata.Original
                    if 'sig' in dot:
                        dot=dot.replace('_sig','')
                        modata.Original=dot
                        db.session.commit()
                    docref=f'tmp/{scac}/data/vorders/' + dot
            if poof>0:
                modata=Proofs.query.get(poof)
                if modata.Original is not None:
                    docref=f'tmp/{scac}/data/vproofs/' + modata.Original
            if tick>0:
                modata=Interchange.query.get(tick)
                if modata.Original is not None:
                    docref=f'tmp/{scac}/data/vinterchange/' + modata.Original
            if (oder>0 or poof>0 or tick>0) and modata.Original is not None:
                    if len(modata.Original)>5:
                        leftscreen=0
                        leftsize=10
                        modlink=0
                        err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if (viewo is not None or viewi is not None or viewp is not None) and numchecked!=1:
            err=['Must check exactly one box to use this option', ' ', ' ', ' ',  ' ']

        if viewi is not None and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder>0:
                modata=Moving.query.get(oder)
                if modata.Path is not None:
                    docref=modata.Path
                    if 'Paid' in modata.Status:
                        idat=Invoices.query.filter(Invoices.Jo==modata.Jo).first()
                        if idat is not None:
                            docref=idat.Original
                    leftscreen=0
                    leftsize=10
                    modlink=0
                    err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if viewp is not None and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder>0:
                modata=Moving.query.get(oder)
                pfile = modata.Location
                if 'vorders' in pfile or 'vinvoice' in pfile:
                    docref=modata.Location
                    leftscreen=0
                    leftsize=8
                    modlink=0
                    invooder=oder
                    err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Views.Moving
# ____________________________________________________________________________________________________________________B.Modify.Moving
        if (modify is not None or vmod is not None) and numchecked==1 :
            modlink=1
            leftsize=8

            if oder>0:
                modata=Moving.query.get(oder)
                csize=People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             docref=f'tmp/{scac}/data/vorders/' + modata.Original
                             err=['All is well', ' ', ' ', ' ',  ' ']

            if poof>0:
                modata=Proofs.query.get(poof)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             docref=f'tmp/{scac}/data/vproofs/' + modata.Original
                             err=['All is well', ' ', ' ', ' ',  ' ']
            if tick>0:
                modata=Interchange.query.get(tick)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             docref=f'tmp/{scac}/data/vinterchange/' + modata.Original
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
# ____________________________________________________________________________________________________________________E.Modify.Moving
        if copy is not None:
            now = datetime.datetime.now().strftime('%I:%M %p')
            if oder > 0 and numchecked == 1:
                sdate = today.strftime('%Y-%m-%d')
                jtype = 'M'
                nextjo = newjo(jtype, sdate)
                myo = Moving.query.get(oder)
                order='New'+myo.Order

                input = Moving(Status='Unmatched', Jo=nextjo, Drop1=myo.Drop1,Order=order, Dropblock1=myo.Dropblock1,Drop2=myo.Drop2,Booking=myo.Booking,BOL=myo.BOL,Container=myo.Container,
                                   Date=myo.Date,Driver=myo.Driver,Dropblock2=myo.Dropblock2, Time=myo.Time, Date2=myo.Date2, Time2=myo.Time2, Seal=myo.Seal, Pickup=myo.Seal, Delivery=None,
                                   Amount=myo.Amount, Path=myo.Path, Original=myo.Original, Description=myo.Description, Chassis=myo.Chassis, Pid=myo.Pid, Cache='1',
                                   Release=0, Shipper=myo.Shipper, Type=None, Time3=None, Label=myo.Label)
                db.session.add(input)
                db.session.commit()
                odata = Moving.query.all()

# ____________________________________________________________________________________________________________________B.AddItems.Moving
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

        if addE is not None and serv>0 and numchecked==1:
            leftsize=8
            modlink=3
            modata=Services.query.get(peep)

        if (addE is not None and numchecked==0) or modlink==30:
            leftsize=8
            if modlink==30:
                copypeople=request.values.get('pullfrom')
                if copypeople != 1:
                    cdat=People.query.filter(People.Company==copypeople).first()
                    if cdat is not None:
                        modata=cdat
            else:
                modlink=1
                #We will create a blank line and simply modify that by updating:
                input= People(Company='New', First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None, Idtype=None, Idnumber=None, Telephone=None,
                              Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='Moving',Temp1=None, Temp2=None, Accountid=None)
                db.session.add(input)
                db.session.commit()
                modata= People.query.filter( (People.Company=='New') & (People.Ptype=='Moving') ).first()
                peep=modata.id
                modlink=30
            err=[' ', ' ', 'Enter Data for New Company', ' ',  ' ']

        if addE is not None and numchecked>1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'

        if addI is not None and numchecked==0:
            leftscreen=0
            leftsize=8
            modlink=20
            #We will create a blank line and simply modify that by updating:
            input = Interchange(Container='New',TruckNumber='',Driver='', Chassis='',Date=None,Release='',GrossWt='',
                                Seals='',ConType='',CargoWt='',Time=None,Status='Unmatched',Original='',Path='',Type='Empty Out',Jo='',Company='', Other=None)
            db.session.add(input)
            db.session.commit()
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            docref=f'tmp/{scac}/data/vunknown/NewJob.pdf'
            modata= Interchange.query.filter( Interchange.Container == 'New' ).first()
            tick=modata.id
            err=[' ', ' ', 'Enter Data for New Interchange Ticket', ' ',  ' ']


        if slim is not None and (numchecked != 1 or oder==0):
            modlink=0
            err=[' ', ' ', 'Must select exactly one box from Shipping Data to use this option', ' ',  ' ']

        if slim is not None and numchecked==1 and oder>0:
            odata1 = Moving.query.get(oder)
            stayslim=odata1.id
            err=[' ', ' ', 'Showing SLIM data around JO='+odata1.Jo, ' ',  ' ']
            modlink=0

# ____________________________________________________________________________________________________________________E.AddItems.Moving
# ____________________________________________________________________________________________________________________B.Delete.Moving
        if deletehit is not None and numchecked==1:
            if oder>0:
                Moving.query.filter(Moving.id == oder).delete()
            if poof>0:
                Proofs.query.filter(Proofs.id == poof).delete()
            if tick>0:
                Interchange.query.filter(Interchange.id == tick).delete()
            if peep>0:
                People.query.filter(People.id == peep).delete()
            if serv>0:
                Services.query.filter(Services.id == serv).delete()

            db.session.commit()

            odata = Moving.query.order_by(Moving.Jo.desc()).all()
            sdata = Services.query.order_by(Services.Price.desc()).all()
            cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()

        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.Moving
        if unpay is not None and oder>0 and numchecked==1:

            odat = Moving.query.get(oder)
            odat.Status='Unpaid'
            db.session.commit()

            myi=Income.query.filter(Income.Jo==odat.Jo).first()
            idelete=myi.id
            Income.query.filter(Income.id == idelete).delete()

            input = ChalkBoard(Jo=myi.Jo,creator=username,comments='Auto Message Invoice Unpaid',status=1)
            db.session.add(input)
            db.session.commit()

# ____________________________________________________________________________________________________________________B.ReceivePayment.Moving

        if (recpay is not None and oder>0 and numchecked==1) or recupdate is not None:
            leftsize=8
            if recpay is not None:
                invooder=oder
            odat = Moving.query.get(invooder)

            if recupdate is not None:
                odat.Status='Paid'
                db.session.commit()

            invojo=odat.Jo
            ldat=Invoices.query.filter(Invoices.Jo==invojo).first()
            err=['Have no Invoice to Receive Against', ' ', ' ', ' ', ' ']
            if ldat is not None:
                idate=ldat.Date
                if ldat.Original is not None:
                    docref=ldat.Original
                    leftscreen=0
                    leftsize=8

                incdat=Income.query.filter(Income.Jo==invojo).first()
                if incdat is None:
                    err=['Creating New Payment on Jo', ' ', ' ', ' ', ' ']
                    paydesc='Receive payment on Invoice '+ invojo
                    recamount=str(ldat.Total)
                    custref='ChkNo'
                    recdate=datetime.datetime.today()
                    input= Income(Jo=odat.Jo,SubJo=None,Pid=odat.Pid,Description=paydesc,Amount=recamount,Ref=custref,Date=recdate,Original=None)
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

                modata= Income.query.filter(Income.Jo==invojo).first()
                inco=modata.id
                err=[' ', ' ', 'Amend Payment for Invoice', ' ',  ' ']

                ldata=Invoices.query.filter(Invoices.Jo==invojo).order_by(Invoices.Ea.desc()).all()
                pdata1=People.query.filter(People.id==odat.Pid).first()
                cache=nonone(odat.Cache)+1

                from invoices import invoiceM
                invo, err, docref, leftsize , invodate = invoiceM(invooder,payment)#minvo??


                if cache>1:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                    # Store for future use
                else:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'

                odat.Cache=cache
                idat=Invoices.query.filter(Invoices.Jo==invojo).first()
                idat.Original=docref
                db.session.commit()
                leftscreen=0
                err[4]='Viewing '+docref

        if recpay is not None and (oder==0 or numchecked!=1):
            err=['Invalid selections:', '', '', '', '']
            if oder==0:
                err[1]='Must select a Moving Job'
            if numchecked!=1:
                err[2]='Must select exactly one Moving Job'
# ____________________________________________________________________________________________________________________E.Receive Payment.Moving
# ____________________________________________________________________________________________________________________B.Payment History.Moving
        if hispay is not None or modlink==7:
            if oder==0 and invooder==0:
                err[1]='Must select a Moving Job'
            else:
                if oder != 0:
                    invooder=oder
                modata = Moving.query.get(invooder)
                ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Jo).all()
                fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.Jo).all()
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
                    ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Jo).all()
                    fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.Jo).all()

                leftsize=8
                modlink=7
# ____________________________________________________________________________________________________________________E.PaymentHistory.Moving







# ____________________________________________________________________________________________________________________B.Invoice.Moving

        if (minvo is not None and oder>0) or invoupdate is not None:

            err=['Could not create invoice', ' ', ' ', ' ',  ' ']
            # First time through: have an order to invoice
            if oder>0:
                invooder=oder

            from invoices import invoiceM
            invo, err, docref, leftsize , invodate = invoiceM(invooder,0)#minvo


            leftscreen=0
            err[4]='Viewing '+docref
            modata=Moving.query.get(invooder)
            ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Jo).all()

        elif minvo is not None:
            err=[' ', ' ', 'Must select at least 1 Job for this selection', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Invoice.Moving
# ____________________________________________________________________________________________________________________B.Newjob.Moving
        if newjob is not None:
            err=['Select Source Document from List']
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()
            modlink=4
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/NewJob.pdf'

        if newjob is None and modlink==4:
            filesel=request.values.get('FileSel')
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/'+filesel
            doctxt=docref.split('.',1)[0]+'.txt'


            shipper=request.values.get('shipper')
            holdvec=[shipper]

        if thisjob is not None:
            modlink=0
            #Create the new database entry for the source document
            filesel=request.values.get('FileSel')
            if filesel != '1':
                docold=f'tmp/{scac}/data/vunknown/'+filesel
                docref=f'tmp/{scac}/data/vorders/'+filesel
                try:
                    shutil.move(addpath(docold),addpath(docref))
                except:
                    err[4]='File has been moved already'
            else:
                docref=''
            sdate=request.values.get('dstart')
            if sdate is None:
                sdate=today

            jtype='M'
            nextjo=newjo(jtype,sdate)

            vals=['shipper','load','order','bol','booking','container','pickup','dropblock1','ldate','ltime','dropblock2','ddate','dtime','thisamt','seal']
            a=list(range(len(vals)))
            i=0
            for v in vals:
                a[i]=request.values.get(v)
                i=i+1
            if a[13] is None:
                a[13]='0.00'
            label=nextjo+' '+a[2]+' '+a[0]+' '+a[13]

            bid=People.query.filter(People.Company==a[0]).first()
            if bid is not None:
                idb=bid.id
            else:
                idb=0

            dropblock1=a[7]
            dropblock2=a[10]
            drop1=dropupdate(dropblock1)
            drop2=dropupdate(dropblock2)

            input = Moving(Status='Unmatched', Jo=nextjo, Drop1=drop1,Order=a[2], Dropblock1=dropblock1,Drop2=drop2,Booking=a[4],BOL=a[3],Container=a[5],
                               Date=a[8],Driver=None,Dropblock2=dropblock2, Time=a[9], Date2=a[11], Time2=a[12], Seal=a[14], Pickup=a[6], Delivery=None,
                               Amount=a[13], Path=None, Original=filesel, Description=None, Chassis=None, Pid=idb, Cache='0',
                               Release=0, Shipper=a[0], Type=None, Time3=None, Label=label)
            db.session.add(input)
            db.session.commit()
            db.session.close()

            odata = Moving.query.order_by(Moving.Jo.desc()).all()
            sdata = Services.query.order_by(Services.Price.desc()).all()
            cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()

            modlink=0
            invo=0
            invooder=0
            inco=0
            leftscreen=1
            oder=0
            leftsize=10
            err=['All is well', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Newjob.Moving
# ____________________________________________________________________________________________________________________B.Matching.Moving
        if match is not None:

            if oder>0 and poof>0 and numchecked==2:
                myo=Moving.query.get(oder)
                myp=Proofs.query.get(poof)
                myp.Order=myo.Order
                myp.Driver=myo.Driver
                myp.Container=myo.Container
                myp.Booking=myo.Booking
                myp.Date=myo.Date
                myp.Time=myo.Time
                myo.BOL=myp.BOL
                if myo.Status=='Unmatched':
                    myo.Status='Matched'
                myp.Status=myo.Status
                db.session.commit()

            if oder>0 and tick>0 and numchecked==2:
                myo=Moving.query.get(oder)
                myi=Interchange.query.get(tick)
                myo.Container=myi.Container
                db.session.commit()

            if numchecked != 2:
                err[1]='Must select exactly 2 boxes to use this option.'
                err[0]=' '
# ____________________________________________________________________________________________________________________E.Matching.Moving
# ____________________________________________________________________________________________________________________B.Calendar.Moving
        if calendar is not None or calupdate is not None:
            leftscreen=2
            datecut= today - datetime.timedelta(days=14)
            newc=containersout(datecut)
            if calupdate is not None:
                waft=request.values.get('waft')
                wbef=request.values.get('wbef')
                waft=nonone(waft)
                wbef=nonone(wbef)
                nweeks=[wbef,waft]
            else:
                nweeks=[2,3]

            caldays,daylist,weeksum=calendar7_weeks('Moving',nweeks)

            if calupdate is not None:
                for j in range(len(daylist)):
                    ilist=daylist[j]
                    if ilist:
                        #newc=ilist
                        tid=ilist[0]
                        fnum='cin'+str(tid)
                        fput=request.values.get(fnum)
                        try:
                            if len(fput)>3:
                                odat=Moving.query.get(tid)
                                if odat is not None:
                                    odat.Container=fput
                                    db.session.commit()

                            fnum='csel'+str(tid)
                            fput=request.values.get(fnum)
                            if fput != '1':
                                odat=Moving.query.get(tid)
                                if odat is not None:
                                    odat.Container=fput
                                    db.session.commit()

                            fnum='dsel'+str(tid)
                            fput=request.values.get(fnum)
                            if fput != '1':
                                odat=Moving.query.get(tid)
                                if odat is not None:
                                    odat.Driver=fput
                                    db.session.commit()

                            fnum='tsel'+str(tid)
                            fput=request.values.get(fnum)
                            if fput != '1':
                                tnum='tsel'+str(tid)
                                trk=request.values.get(tnum)
                                odat=Moving.query.get(tid)
                                ddat=Drivers.query.filter(Drivers.Name==odat.Driver).first()
                                fdat=FELVehicles.query.filter(FELVehicles.Unit==trk).first()
                                if ddat is not None and fdat is not None:
                                    ddat.Truck=fdat.Unit
                                    ddat.Tag=fdat.Plate
                                    db.session.commit()

                        except:
                            err[1]='Not Allowed'

                caldays,daylist,weeksum=calendar7_weeks('Moving',nweeks)

# ____________________________________________________________________________________________________________________E.Calendar.Moving
    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        doctxt=''
        filesel=''
        docref=''
        odata = Moving.query.all()
        sdata = Services.query.order_by(Services.Price.desc()).all()
        cdata = People.query.filter(People.Ptype=='Moving').order_by(People.Company).all()
        ldata = None
        howapp=0
        dlist=['on']*2
        newc='Not found'
        oder,poof,tick,serv,peep,invo,cache,modata,modlink,stayslim,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks = init_truck_zero()
        leftscreen=1
        holdvec=[0]*3

        leftsize=10
        err=['All is well', ' ', ' ', ' ',  ' ']

    alltdata=Drivers.query.all()
    tdata=FELVehicles.query.all()
    rightsize=12-leftsize
    fdata = myoslist(f'tmp/{scac}/data/vunknown')
    fdata.sort()
    sdata2= Services.query.order_by(Services.Price).all()
    pfdata=People.query.filter((People.Ptype=='Exporter') | (People.Ptype=='Trucking') | (People.Ptype=='Storage') | (People.Ptype=='Moving')).order_by(People.Company).all()

    return odata,sdata,cdata,oder,sdata2,serv,peep,err,modata,caldays,daylist,nweeks,howapp,modlink,leftscreen,docref,stayslim,leftsize,newc,tdata,dlist,rightsize,ldata,invodate,inco,invo,invooder,cache,alltdata,fdata,filesel,today,now,doctxt,holdvec,pfdata
