from runmain import db
from models import Vehicles, Dealer, General, Invoices, JO, Income, Bills, Accounts, Autos, People, Interchange, Drivers, ChalkBoard, Services
from flask import render_template, flash, redirect, url_for, session, logging, request

import datetime
import shutil
from CCC_system_setup import myoslist, addpath, scac

def isoH():

    if request.method == 'POST':
        username = session['username'].capitalize()
        from viewfuncs import d2s, newjo, popjo, jovec, timedata, nonone, nononef, GetCo,init_horizon_zero, numcheck, sdiff, calendar7_weeks,GetCo3
        cars,auto,peep,invo,cache,modata,modlink,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks=init_horizon_zero()
        filesel=''
        docref=''
        doctxt=''
        displdata=0
        err=['All is well', ' ', ' ', ' ',  ' ']

# ____________________________________________________________________________________________________________________B.FormVariables.Dealer
        leftsize=10
        today = datetime.date.today()
        jobdate = datetime.date.today()

        match    =  request.values.get('Match')
        modify   =  request.values.get('Modify')
        vmod     =  request.values.get('Vmod')
        minvo    =  request.values.get('MakeI')
        mbill    =  request.values.get('MakeB')
        viewo     =  request.values.get('ViewO')
        viewi     =  request.values.get('ViewI')
        addE     = request.values.get('addentity')
        addA     = request.values.get('addauto')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        datatable1=request.values.get('datatable1')
        datatable2=request.values.get('datatable2')
        datatable3=request.values.get('datatable3')
        dlist=[datatable1,datatable2,datatable3]

        # hidden values
        update   =  request.values.get('Update')
        invoupdate = request.values.get('invoUpdate')
        modlink =  request.values.get('passmodlink')
        emailnow = request.values.get('emailnow')
        emailinvo = request.values.get('emailInvo')
        newjob=request.values.get('NewJ')
        thisjob=request.values.get('ThisJob')
        recpay   = request.values.get('RecPay')
        hispay   = request.values.get('HisPay')
        recupdate = request.values.get('recUpdate')

        calendar=request.values.get('Calendar')
        calupdate=request.values.get('calupdate')

        cars=request.values.get('cars')
        peep=request.values.get('peep')
        auto=request.values.get('auto')

        invo=request.values.get('invo')
        invooder=request.values.get('invooder')
        cache=request.values.get('cache')

        modata=0
        idata=0
        leftscreen=1
        docref=''
        ldata=None

        modlink=nonone(modlink)
        cars=nonone(cars)
        peep=nonone(peep)
        auto=nonone(auto)

        invo=nonone(invo)
        invooder=nonone(invooder)
        cache=nonone(cache)

        if returnhit is not None:
            modlink=0
            invooder=0
            cars=0
            invo=0


# ____________________________________________________________________________________________________________________E.FormVariables.Dealer
# ____________________________________________________________________________________________________________________B.DataModifications.Dealer

        if update is not None and modlink==2:
            modata=People.query.get(peep)
            vals=['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3', 'idtype', 'tid', 'tel', 'email' , 'assoc1', 'assoc2', 'date1', 'ptype']
            a=list(range(len(vals)))
            i=0
            for v in vals:
                a[i]=request.values.get(v)
                i=i+1

            try:
                sdate1dt=datetime.datetime.strptime(a[13],"%Y-%m-%d")
            except:
                a[13]=datetime.datetime.today().strftime('%Y-%m-%d')

            input= People(Company=a[0], First=a[1], Middle=a[2], Last=a[3], Addr1=a[4], Addr2=a[5], Addr3=a[6], Idtype=a[7], Idnumber=a[8],
                          Telephone=a[9], Email=a[10], Associate1=a[11], Associate2=a[12], Date1=a[13], Ptype=a[14], Date2=None, Original=None, Temp1=None, Temp2=None)
            db.session.add(input)
            db.session.commit()
            err=[' ', ' ', 'New Entity Added to Database.', ' ',  ' ']
            modlink=0

        if (update is not None and modlink==1) or (update is not None and modlink==10):
            if cars > 0:
                modata=Dealer.query.get(cars)
                vals=['cost', 'sale', 'bfee', 'tow', 'repair', 'oitem', 'ocost', 'modelyear', 'make', 'model', 'color', 'vin', 'dfee', 'thiscompany']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1
                modata.Cost=a[0]
                modata.Sale=a[1]
                modata.Bfee=a[2]
                modata.Tow=a[3]
                modata.Repair=a[4]
                modata.Oitem=a[5]
                modata.Ocost=a[6]
                modata.Year=a[7]
                modata.Make=a[8]
                modata.Model=a[9]
                modata.Color=a[10]
                modata.Vin=a[11]
                modata.DocumentFee=a[12]
                modata.Company=a[13]
                pdat=People.query.filter(People.Company==a[13]).first()
                if pdat is not None:
                    modata.Pid=pdat.id
                try:
                    modata.Label=modata.Jo+' '+a[13]
                except:
                    err[4]='Cannot create Label with missing information (company, Year, Make, Model)'
                db.session.commit()
                err=[' ', ' ', 'Modification to Auto Sale JO ' + modata.Jo + ' completed.', ' ',  ' ']
                modlink=0



            if peep > 0:
                modata=People.query.get(peep)
                vals=['company', 'fname', 'mnames', 'lname', 'addr1', 'addr2', 'addr3', 'idtype', 'tid', 'tel', 'email' , 'assoc1', 'assoc2', 'date1', 'role']
                a=list(range(len(vals)))
                i=0
                for v in vals:
                    a[i]=request.values.get(v)
                    i=i+1

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
                modata.Ptype=a[14]
                #Need to infuse change into Autos if it is a Tow Company:
                if modata.Ptype=='TowCo' or a[14]=='TowCo':
                    adat=Autos.query.filter(Autos.TowCompany==modata.Company).first()
                    if adat is not None:
                        adat.TowCompany=a[0]

                modata.Company=a[0]

                db.session.commit()
                err=[' ', ' ', 'Modification to Entity ID ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0

            if auto > 0 or modlink==10:


                if modlink==10:
                    filesel=request.values.get('FileSel')
                    if filesel != '1':
                        oldref=f'tmp/{scac}/data/vunknown/'+filesel
                        oldtxt=oldref.split('.',1)[0]+'.txt'
                    else:
                        oldref=''
                        oldtxt=''
                    modata= Autos.query.filter(Autos.Status=='New').first()
                    auto=modata.id
                    docref=f'tmp/{scac}/data/vdispatch/DISP'+str(auto)+'.pdf'
                    doctxt=f'tmp/{scac}/data/vdispatch/DISP'+str(auto)+'.txt'
                    try:
                        shutil.move(addpath(oldref),addpath(docref))
                    except:
                        err[3]='.pdf file already moved'
                    try:
                        shutil.move(addpath(oldtxt),addpath(doctxt))
                    except:
                        err[4]='.txt file already moved'
                    modata.Original=docref
                    modlink=0
                else:
                    modata=Autos.query.get(auto)

                vals=['modelyear', 'make', 'model', 'color', 'vin', 'title', 'state', 'empweight', 'dispatched', 'owner', 'towcompany', 'towcost', 'delto', 'orderid', 'newtowcompany','towcostea','pufrom','cvalue','ncars']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)
                modata.Year=a[0]
                modata.Make=a[1]
                modata.Model=a[2]
                modata.Color=a[3]
                modata.VIN=a[4]
                modata.Title=a[5]
                modata.State=a[6]
                modata.EmpWeight=a[7]
                modata.Dispatched=a[8]
                modata.Owner=a[9]
                company=a[10]
                if company == '1':
                    modata.TowCompany=a[14]
                    input= People(Company=a[14], First='', Middle='', Last='', Addr1='', Addr2='', Addr3='', Idtype='', Idnumber='', Telephone='',
                          Email='', Associate1='', Associate2='', Date1=today, Date2=None, Original='', Ptype='TowCo', Temp1='', Temp2='')
                    db.session.add(input)
                    modata.TowCompany=a[14]
                else:
                    modata.TowCompany=company
                modata.TowCost=d2s(a[11])
                modata.Delto=a[12]
                modata.Pufrom=a[16]
                modata.Value=d2s(a[17])
                ncars=a[18]
                try:
                    ncars=int(a[18])
                    towcost=float(d2s(a[11]))
                    towcostea=towcost/float(ncars)
                    towcostea=str(towcostea)
                    towcostea=d2s(towcostea)
                    modata.TowCostEa=towcostea
                except:
                    modata.TowCostEa=a[15]
                    ncars=0
                modata.Ncars=ncars
                sdate1=request.values.get('date1')
                try:
                    sdate1dt=datetime.datetime.strptime(sdate1,"%Y-%m-%d")
                except:
                    sdate1=today.strftime('%Y-%m-%d')

                sdate2=request.values.get('date2')
                try:
                    sdate2dt=datetime.datetime.strptime(sdate2,"%Y-%m-%d")
                except:
                    sdate2=today.strftime('%Y-%m-%d')
                modata.Date1=sdate1
                modata.Date2=sdate2
                modata.Orderid=a[13]
                modata.Status='Novo'

                db.session.commit()
                err=[' ', ' ', 'Modification to Auto Data ' + str(modata.id) + ' completed.', ' ',  ' ']
                modlink=0


# ____________________________________________________________________________________________________________________E.DataModifications.Dealer
# ____________________________________________________________________________________________________________________B.InvoiceUpdate.Dealer

        if invoupdate is not None:
            leftsize=8
            hdata1=Dealer.query.get(invooder)
            invodate=request.values.get('invodate')
            #if invodate is None:
                #invodate=today
            idata=Invoices.query.filter(Invoices.Jo==hdata1.Jo).all()
            for data in idata:
                iqty=request.values.get('qty'+str(data.id))
                iqty=nononef(iqty)
                data.Description=request.values.get('desc'+str(data.id))
                deach=request.values.get('cost'+str(data.id))
                if deach is not None:
                    deach="{:.2f}".format(float(deach))
                else:
                    deach="{:.2f}".format(0.00)
                data.Qty=iqty
                data.Ea=deach
                data.Date=invodate
                db.session.commit()
            #Remove zeros from invoice in case a zero was the mod
            Invoices.query.filter(Invoices.Qty==0).delete()
            db.session.commit()
            #Create invoice code for order
            err=[' ', ' ', 'Invoice created for JO: '+hdata1.Jo, ' ',  ' ']
            idat=Invoices.query.filter(Invoices.Jo==hdata1.Jo).first()
            invodate=idat.Date

            idata=Invoices.query.filter(Invoices.Jo==hdata1.Jo).all()
            amt=0.0
            for data in idata:
                amt=amt+float(data.Qty)*float(data.Ea)
            hdata1.Charge="%0.2f" % amt
            hdata1.Status='Invoiced'
            db.session.commit()
            invo=1
# Regenerate invoice with new data
            idata=Invoices.query.filter(Invoices.Jo==hdata1.Jo).order_by(Invoices.Ea.desc()).all()
            pdat=People.query.filter(People.id==hdata1.Pid).first()
            cache=cache+1

            import make_H_invoice
            make_H_invoice.main(hdata1,idata,pdat,cache,invodate,0)

            if cache>0:
                docref=f'tmp/{scac}/data/vinvoice/INV'+hdata1.Jo+'c'+str(cache)+'.pdf'
            else:
                docref=f'tmp/{scac}/data/vinvoice/INV'+hdata1.Jo+'.pdf'
            hdata1.Ipath=docref
            hdata1.Cache=cache
            db.session.commit()
            leftscreen=0
            err[3]='invooder='+str(invooder)
            err[4]='Viewing '+docref
            modata=Dealer.query.get(invooder)
# ____________________________________________________________________________________________________________________E.InvoiceUpdate.Dealer
# ____________________________________________________________________________________________________________________B.SetBaseData.Dealer

        hdata = Dealer.query.all()
        adata = Autos.query.all()
        pdata=People.query.filter( (People.Ptype=='Jays') | (People.Ptype== 'TowCo') ).all()
# ____________________________________________________________________________________________________________________E.SetBaseData.Dealer
# ____________________________________________________________________________________________________________________B.Numcheck.Dealer

        try:
            cars,auto,peep,numchecked=numcheck(3,hdata,adata,pdata,0,0,['cars','auto','peep'])
        except:
            cars=0
            auto=0
            peep=0
            numchecked=0

# ____________________________________________________________________________________________________________________E.Numcheck.Dealer
# ____________________________________________________________________________________________________________________B.Views.Dealer

        if (viewo is not None or viewi is not None) and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']

            if cars>0 and viewi is not None:
                modata=Dealer.query.get(cars)
                if modata.Ipath is not None:
                    docref=modata.Ipath

            if cars>0 and viewo is not None:
                modata=Dealer.query.get(cars)
                if modata.Apath is not None:
                    docref=modata.Apath

            if auto>0:
                modata=Autos.query.get(auto)
                if modata.Original is not None:
                    docref=modata.Original

            if (auto>0 or cars>0) and docref:
                    if len(docref)>5:
                        leftscreen=0
                        leftsize=10
                        modlink=0
                        err=['All is well', ' ', ' ', ' ',  ' ']

        if (viewo is not None or viewi is not None) and numchecked!=1:
            err=['Must check exactly one box to use this option', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Views.Dealer
# ____________________________________________________________________________________________________________________B.ModifySetup.Dealer

        if (modify is not None or vmod is not None) and numchecked==1:
            modlink=1
            leftsize=8
            if cars>0:
                fdata = myoslist(f'tmp/{scac}/data/vunknown')
                fdata.sort()
                modata=Dealer.query.get(cars)
                jobdate=modata.Date
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Apath is not None:
                        if len(modata.Apath)>5:
                             leftscreen=0
                             docref=f'tmp/{scac}/data/vcarbuy/' + modata.Apath
                             err=['All is well', ' ', ' ', ' ',  ' ']

            if peep>0:
                modata=People.query.get(peep)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             docref=f'tmp/{scac}/data/vpersons/' + modata.Original
                             err=['All is well', ' ', ' ', ' ',  ' ']
            if auto>0:
                modata=Autos.query.get(auto)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.Original is not None:
                        if len(modata.Original)>5:
                             leftscreen=0
                             leftsize=8
                             docref=modata.Original
                             doctxt=docref.split('.',1)[0]+'.txt'
                             err=['All is well', ' ', ' ', ' ',  ' ']

        if (modify is not None or vmod is not None) and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.ModifySetup.Dealer
# ____________________________________________________________________________________________________________________B.AddItemsSetup.Dealer

        if addE is not None and peep>0 and numchecked==1:
            modlink=2
            modata=People.query.get(peep)

        if addE is not None:
            leftsize=8
            modlink=1
            #We will create a blank line and simply modify that by updating:
            input= People(Company='New', First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None, Idtype=None, Idnumber=None, Telephone=None,
                          Email=None, Associate1=None, Associate2=None, Date1=None, Date2=None, Original=None, Ptype='Dealer', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata= People.query.filter( (People.Company=='New') & (People.Ptype=='Dealer') ).first()
            if modata is not None:
                peep=modata.id
            else:
                peep=0
            err=[' ', ' ', 'Enter Data for New Entity', ' ',  ' ']


        if addA is not None or modlink==10:
            leftscreen=0
            leftsize=8
            if modlink==10:
                titledata=General.query.filter((General.Subject.contains('title')) & (General.Category.contains('1'))).all()
                fdata=[]
                displdata=[]
                for title in titledata:
                    fdata.append(title.Path)
                    displdata.append(title.Category)
                filesel=request.values.get('FileSel')
                docref=f'tmp/{scac}/data/vgeneral/'+filesel
                doctxt=docref.split('.',1)[0]+'.txt'


            if modlink!=10:
                titledata=General.query.filter((General.Subject.contains('title')) & (General.Category.contains('1'))).all()
                fdata=[]
                displdata=[]
                for title in titledata:
                    file1=f'tmp/{scac}/data/vgeneral/'+title.Path
                    fdata.append(title.Path)
                    displdata.append(title.Category)

                docref=f'tmp/{scac}/data/vgeneral/'+fdata[0]
                doctxt=''
                #We will create a blank line and simply modify that by updating:
                input= Autos(Jo=None,Hjo=None,Year=None,Make=None,Model=None,Color=None,VIN=None,Title=None,State=None,EmpWeight=None,Dispatched=None,Value=None,TowCompany=None,TowCost=None,TowCostEa=None,Original=None,Status='New',Date1=None, Date2=None, Pufrom=None, Delto=None, Ncars=None, Orderid=None)
                db.session.add(input)
                db.session.commit()
                modata= Autos.query.filter(Autos.Status=='New').first()
                if modata is not None:
                    auto=modata.id
                else:
                    auto=0
                modlink=10

            err=[' ', ' ', 'Enter Data for New Auto', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.AddItemsSetup.Dealer
# ____________________________________________________________________________________________________________________B.Email.Dealer

        if emailinvo is not None:
            leftsize=8
            leftscreen=0
            modlink=0
            modata = Dealerquery.get(invooder)
            ldata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Ea.desc()).all()
            jo=modata.Jo
            pdat=People.query.filter(People.id==modata.Pid).first()
            if pdat is None:
                err=[' ', ' ', 'There is no Billing information for this selection', ' ',  ' ']
            else:
                email=pdat.Email
            docref=modata.Ipath
            modata.Status='EmlInvo'
            db.session.commit()

            if 'vinvoice' not in docref:
                err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            else:
                if email is not None:
                    import invoice_mimemail2
                    invoice_mimemail2.main(jo,docref,email)
# ____________________________________________________________________________________________________________________E.Email.Dealer
# ____________________________________________________________________________________________________________________B.Delete.Dealer

        if deletehit is not None and numchecked==1:
            if cars>0:
                Dealer.query.filter(Dealer.id == cars).delete()
            if peep>0:
                People.query.filter(People.id == peep).delete()
            if auto>0:
                Autos.query.filter(Autos.id == auto).delete()
            db.session.commit()

            pdata = GetCo('Jays','All')
            hdata = Dealer.query.order_by(Dealer.Jo).all()
            adata = Autos.query.all()

        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.Dealer
# ____________________________________________________________________________________________________________________B.ReceivePayment.Dealer

        if (recpay is not None and cars>0 and numchecked==1) or recupdate is not None:
            leftsize=8
            if recpay is not None:
                invooder=cars
            hdat = Dealer.query.get(invooder)
            invojo=hdat.Jo
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
                    recamount=str(ldat.Amount)
                    custref='ChkNo'
                    recdate=today
                    input= Income(Jo=hdat.Jo,SubJo=None,Pid=hdat.Pid,Description=paydesc,Amount=recamount,Ref=custref,Date=recdate,Original=None)
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
                pdat=People.query.filter(People.id==hdat.Pid).first()
                cache=nonone(hdat.Cache)+1

                import make_H_invoice
                make_H_invoice.main(hdat,ldata,pdat,cache,invodate,payment)

                if cache>1:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'c'+str(cache)+'.pdf'
                    # Store for future use
                else:
                    docref=f'tmp/{scac}/data/vinvoice/INV'+invojo+'.pdf'

                hdat.Cache=cache
                hdat.Status='Paid'
                idat=Invoices.query.filter(Invoices.Jo==invojo).first()
                idat.Original=docref
                db.session.commit()
                leftscreen=0
                err[4]='Viewing '+docref

        if recpay is not None and (cars==0 or numchecked!=1):
            err=['Invalid selections:', '', '', '', '']
            if cars==0:
                err[1]='Must select a Dealer Job'
            if numchecked!=1:
                err[2]='Must select exactly one Dealer Job'
# ____________________________________________________________________________________________________________________E.Receive Payment.Dealer
# ____________________________________________________________________________________________________________________B.Payment History.Dealer
        if hispay is not None or modlink==7:
            if cars==0 and invooder==0:
                err[1]='Must select an Dealer Job'
            else:
                if cars != 0:
                    invooder=cars
                modata = Dealer.query.get(invooder)
                idata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Jo).all()
                fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.Jo).all()
                #Check to see if we need to delete anything from history
                killthis=request.values.get('killthis')
                if killthis is not None and modlink==7:
                    for data in idata:
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
                    idata=Invoices.query.filter(Invoices.Jo==modata.Jo).order_by(Invoices.Jo).all()
                    fdata=Income.query.filter(Income.Jo==modata.Jo).order_by(Income.Jo).all()

                leftsize=8
                modlink=7
# ____________________________________________________________________________________________________________________E.PaymentHistory.Dealer

# ____________________________________________________________________________________________________________________B.Invoice.Dealer

        if (minvo is not None and cars>0):
            err=['Could not create invoice', ' ', ' ', ' ',  ' ']
            # First time through: have an order to invoice
            if cars>0:
                invooder=cars
            myo=Dealer.query.get(invooder)
            #Check to see if we have the required data to make an invoice:
            bid=myo.Pid

            if bid is None:
                err[1]='No Billing Data'

            if bid:
                invo=1
                leftsize=8
                if myo.Cache is not None:
                    cache=myo.Cache+1
                else:
                    cache=1


                hdata=Dealer.query.filter(Dealer.Jo==myo.Jo).all()
                total=0
                #Delete previous invoices created for this Jo
                killdata=Invoices.query.filter(Invoices.Jo==myo.Jo).delete()
                for data in hdata:
                    qty=1
                    towcost=nononef(data.Tow)
                    repaircost=nononef(data.Repair)
                    othercost=nononef(data.Ocost)
                    buyerfee=nononef(data.Bfee)
                    carcost=nononef(data.Sale)
                    docfee=nononef(data.DocumentFee)

                    total=total+towcost+repaircost+othercost+buyerfee+carcost+docfee
                    if carcost>0:
                        descript=data.Year+' '+data.Make+' '+data.Model+' VIN:'+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Car Purchase', Description=descript, Ea=carcost, Qty=qty, Amount=carcost, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    if buyerfee>0:
                        descript='Buyer fee for VIN: '+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Buyer Fee', Description=descript, Ea=buyerfee, Qty=qty, Amount=buyerfee, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    if towcost>0:
                        descript='Towing cost for VIN: '+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Towing', Description=descript, Ea=towcost, Qty=qty, Amount=towcost, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    if repaircost>0:
                        descript='Repair cost for VIN: '+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Repairs', Description=descript, Ea=repaircost, Qty=qty, Amount=repaircost, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    if docfee>0:
                        descript='Dealer document fee for VIN: '+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Document Fee', Description=descript, Ea=docfee, Qty=qty, Amount=docfee, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()
                    if othercost>0:
                        descript=data.Oitem+' for VIN: '+data.Vin
                        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service=data.Oitem, Description=descript, Ea=othercost, Qty=qty, Amount=othercost, Total=total, Date=today, Original=None, Status='New')
                        db.session.add(input)
                        db.session.commit()

                #Cycle through again so all the line items have the correct total amount
                idata=Invoices.query.filter(Invoices.Jo==myo.Jo).all()
                if idata is not None:
                    for data in idata:
                        data.Total=total
                        db.session.commit()

                ldat=Invoices.query.filter(Invoices.Jo==myo.Jo).first()
                if ldat is None:
                    invo=0
                    leftsize=10
                    err=[' ', ' ', 'No services on invoice yet and none selected', ' ',  ' ']
                else:
                    invo=1
                    leftsize=8
                    invodate=ldat.Date
                    err=[' ', ' ', 'Created invoice for JO= '+myo.Jo, ' ',  ' ']
                    ldata=Invoices.query.filter(Invoices.Jo==myo.Jo).order_by(Invoices.Ea.desc()).all()
                    pdat=People.query.filter(People.id==myo.Pid).first()

                    import make_H_invoice
                    make_H_invoice.main(myo,ldata,pdat,cache,invodate,0)

                    if cache>0:
                        docref=f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
                        # Store for future use
                    else:
                        docref=f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'.pdf'
                    myo.Ipath=docref
                    myo.Cache=cache
                    db.session.commit()
                    leftscreen=0
                    err[3]='invooder='+str(invooder)
                    err[4]='Viewing '+docref
                    modata=Dealer.query.get(invooder)

        elif minvo is not None:
            err=[' ', ' ', 'Must select at least 1 Job for this selection', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Invoice.Dealer
# ____________________________________________________________________________________________________________________B.Newjob.Dealer
        if newjob is not None:
            err=['Select Source Document from List']
            jobdate=datetime.date.today()
            modlink=4
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/NewJob.pdf'
            doctxt=''

        if newjob is None and modlink==4:
            filesel=request.values.get('FileSel')
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            jobdate=request.values.get('dstart')
            leftsize=8
            leftscreen=0
            if filesel != '1':
                docref=f'tmp/{scac}/data/vunknown/'+filesel
                doctxt=docref.split('.',1)[0]+'.txt'
            else:
                docref=''
                doctxt=''


        if thisjob is not None:
            modlink=0
            #Create the new database entry for the source document
            filesel=request.values.get('FileSel')
            if filesel != '1':
                docold=f'tmp/{scac}/data/vunknown/'+filesel
                docref=f'tmp/{scac}/data/vcarbuy/'+filesel
                try:
                    shutil.move(addpath(docold),addpath(docref))
                except:
                    err[0]='File moved'
            else:
                docref=''
            sdate=request.values.get('dstart')
            if sdate is None:
                sdate=today

            jtype='J'
            nextjo=newjo(jtype,sdate)

            company=request.values.get('thiscompany')
            bid=People.query.filter(People.Company==company).first()
            if bid is not None:
                idb=bid.id
            else:
                idb=0

            input = Dealer(Jo=nextjo,Pid=idb,Company=company,Aid=0,Make=None,Model=None,Year=None,Vin=None,Cost=None,Sale=None,Bfee=None,Tow=None,
                            Repair=None,Oitem=None,Ocost=None,Ipath=None,Apath=filesel,Cache=0,Status='New',Label=None,Date=sdate, DocumentFee='')

            db.session.add(input)
            db.session.commit()
            modata=Dealer.query.filter(Dealer.Jo==nextjo).first()
            cars=modata.id
            leftscreen=0
            err=['All is well', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Newjob.Dealer
# ____________________________________________________________________________________________________________________B.Match.Dealer

        if match is not None:

            if cars>0 and peep>0 and numchecked==2:
                mys=Dealer.query.get(cars)
                myp=People.query.get(peep)
                mys.Pid = myp.id
                mys.Company = myp.Company

                db.session.commit()

            if cars>0 and auto>0 and numchecked==2:
                mys=Dealer.query.get(cars)
                mya=Autos.query.get(auto)
                thisjo=mys.Jo
                mya.Hjo = thisjo
                # Check to see if we need a new JO line because we already have a car assigned
                if mys.Aid>0 and mys.Aid != auto:
                    #We need a new line item
                    input = Dealer(Jo=thisjo,Pid=mys.Pid,Company=mys.Company,Aid=0,Make=None,Model=None,Year=None,Vin=None,Cost=None,Sale=None,Bfee=None,Tow=None,
                            Repair=None,Oitem=None,Ocost=None,Ipath=None,Apath=None,Cache=0,Status='New',Label=None, DocumentFee='')
                    db.session.add(input)
                    db.session.commit()
                    mys=Dealer.query.filter((Dealer.Jo==thisjo) & (Dealer.Aid==0)).first()

                mys.Aid=auto
                mys.Make=mya.Make
                mys.Model=mya.Model
                mys.Year=mya.Year
                mys.Vin=mya.VIN
                mys.Status='Car'
                mya.Status='M'
                db.session.commit()

            if numchecked != 2:
                err[1]='Must select exactly 2 boxes to use this option.'
                err[0]=' '

# ____________________________________________________________________________________________________________________E.Match.Dealer
# ____________________________________________________________________________________________________________________B.Calendar.Dealer
        if calendar is not None or calupdate is not None:
            leftscreen=2
            if calupdate is not None:
                waft=request.values.get('waft')
                wbef=request.values.get('wbef')
                waft=nonone(waft)
                wbef=nonone(wbef)
                nweeks=[wbef,waft]
            else:
                nweeks=[2,3]
            caldays,daylist,weeksum=calendar7_weeks('Dealer',nweeks)

# ____________________________________________________________________________________________________________________E.Calendar.Dealer

    #This is the else for 1st time through (not posting data from Dealer.html)
    else:
        from viewfuncs import GetCo, popjo, jovec, timedata, nonone, nononef, init_horizon_zero, GetCo3
        #today = datetime.date.today().strftime('%Y-%m-%d')
        #now = datetime.datetime.now().strftime('%I:%M %p')
        jobdate=datetime.date.today()
        idata=0
        leftscreen=1
        cars,auto,peep,invo,cache,modata,modlink,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks = init_horizon_zero()
        leftscreen=1
        dlist=['off']*3
        dlist[1]='on'
        filesel=''
        docref=''
        doctxt=''
        leftsize=10
        err=['All is well', ' ', ' ', ' ',  ' ']
        displdata=0

    if fdata==0:
        fdata = myoslist('data/vunknown')
        fdata.sort()
    pdata = GetCo('Jays','All')
    sdata= Services.query.all()
    hdata = Dealer.query.all()
    adata = Autos.query.all()
    leftsize = 8

    return hdata,adata,pdata,idata,fdata,displdata,cars,invooder,auto,peep,err,modata,caldays,daylist,nweeks,invodate,doctxt,sdata,dlist,modlink,inco,invo,cache,filesel,leftscreen,docref,leftsize,jobdate
