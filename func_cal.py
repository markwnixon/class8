from runmain import db
from models import Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Orders, Drops, Vehicles
from flask import session, logging, request
import datetime
import pytz
import calendar
import re
import os
from viewfuncs import parselinenoupper,d2s, dollar


def calendar7_weeks_all(lweeks):
    today = datetime.datetime.today()
    nweeks=lweeks[0]+lweeks[1]
    ndays=nweeks*7
    day=today.day
    d = today
    nlist=ndays*12
    caldays=list(range(ndays))
    caldt=list(range(ndays))
    daylist=list(range(nlist))
    shlst=list(range(nlist))
    days_ahead=[0]*nweeks
    calmon=[0]*nweeks
    next_weekday=[0]*nweeks
    datestr=[0]*nweeks

    for i in range(ndays):
        for j in range(12):
            k=9*i+j
            daylist[k]=0

    for i in range(7):
        days_ahead1 = i - 7 - d.weekday()
        if days_ahead1 <= 0:
            days_ahead1 += 7
        day0=days_ahead1-7*lweeks[0]
        for m in range(nweeks):
            days_ahead[m]=day0+7*m
            next_weekday[m] = d + datetime.timedelta(days_ahead[m])
            calmon[m]=str(next_weekday[m].month)
            caldays[i+7*m]=   calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[m])] + ' ' + str(next_weekday[m].day)
            datestr[m]=str(next_weekday[m].month) + '/' + str(next_weekday[m].day) + '/' + str(next_weekday[m].year)
            caldt[i+7*m] = datetime.datetime.strptime(datestr[m], '%m/%d/%Y')

        if next_weekday[lweeks[0]].day==day:
            caldays[i+7*lweeks[0]]=   'X' + calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[lweeks[0]])] + ' ' + str(next_weekday[lweeks[0]].day)



    if 1==1:
        weeksum=0
        j1=0
        j2=0
        j3=0
        j4=0
        j5=0
        for i in range(ndays):
            dloc=caldt[i]
            dloc2=dloc+datetime.timedelta(days=1)

#___Overseas Part________________________________________________________________

            odata = OverSeas.query.filter(OverSeas.PuDate==dloc).all()
            for j1,data in enumerate(odata):
                k=12*i+j1
                shipper=data.BillTo
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]

                pod=data.Pod
                pol=data.Pol
                if len(pod)>8:
                    pod=re.match(r'\W*(\w[^,. !?"]*)', pod).groups()[0]
                if len(pol)>8:
                    pol=re.match(r'\W*(\w[^,. !?"]*)', pol).groups()[0]

                container=data.Container
                book=data.Booking
                bdat=Bookings.query.filter(Bookings.Booking==data.Booking).first()
                if bdat is not None:
                    doccut=bdat.PortCut.strftime('%m/%d/%Y')
                else:
                    doccut=''
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                lt=data.Jo
                lt=lt[6:8]
                shlst[k]=[lt, 'O', 'blue darken-4']
                daylist[k]=[data.id, shipper, book, container, pol, pod, data.Jo, data.Status, data.Driver, phone, trk, plate, doccut, cb]

#___Trucking Part________________________________________________________________
            tdata = Orders.query.filter((Orders.Date >= dloc) & (Orders.Date < dloc2)).all()
            for j2,data in enumerate(tdata):
                k=12*i+j1+j2+1


                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=People.query.filter((People.Company==data.Company) & (People.Ptype=='Trucking')).first()
                loc2=People.query.filter((People.Company==data.Company2) & (People.Ptype=='Trucking')).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12=''
                    addr22=''
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                lt=data.Jo
                lt=lt[6:8]
                if 'Global' in shipper:
                    oview=data.Type
                    if oview is not None:
                        if len(oview)>5:
                            oview=oview[0:5]
                else:
                    oview=data.Order
                    if len(oview)>5:
                        oview=oview[-6:]
                shlst[k]=[lt, 'T', 'red darken-4']
                daylist[k]=[data.Order, data.Pickup, data.Booking, data.Driver, data.Time, data.Jo, data.Container, data.Status, shipper, data.id, data.Company, addr11, addr21, data.Company2, addr12, addr22, phone, trk, plate, cb, oview]

#___Horizon/Towing Part________________________________________________________________
            adata = db.session.query(Autos.Orderid).distinct().filter(Autos.Date2==dloc)
            for j3,data in enumerate(adata):

                adat=Autos.query.filter((Autos.Orderid==data.Orderid)).first()
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==adat.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)
                com=adat.TowCompany
                if com is None or com=='' or len(com)<2:
                    com='FIX'

                if adat is not None:
                    autolist=[]
                    allcars=Autos.query.filter(Autos.Orderid==adat.Orderid).all()
                    for ncars,car in enumerate(allcars):
                        autolist.append([car.Year,car.Make,car.Model,car.VIN])
                    ncars=ncars+1

                try:
                    amt=adat.TowCost
                    amt=d2s(amt)
                    amteach=float(amt)/ncars
                    amteach=dollar(amteach)
                    amt='$'+amt
                    amt=amt.replace('.00','')
                except:
                    amt='$0.00'
                    amteach='$0.00'

                towid='tow'+str(adat.id)

                k=12*i+j1+j2+j3+2
                shlst[k]=[amt, 'H', 'amber accent-4']
                daylist[k]=[adat.id, com, amt, adat.Status, autolist, cb, adat.Jo, amteach, ncars, towid]
#___Moving Part________________________________________________________________

            #mdata = Moving.query.filter(Moving.Date == dloc).all()
            mdata = []
            for j4,data in enumerate(mdata):
                k=12*i+j1+j2+j3+j4+3
                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=Drops.query.filter(Drops.Entity==data.Drop1).first()
                loc2=Drops.query.filter(Drops.Entity==data.Drop2).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12='NF'
                    addr22='NF'
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                lt=data.Jo
                lt=lt[6:8]
                shlst[k]=[lt, 'M']
                daylist[k]=[data.id, data.Jo, shipper, data.Drop1, addr11, addr21, data.Time, data.Drop2, addr12, addr22, data.Time2, data.Container, data.Driver, data.Status, phone, trk, plate, cb, data.Amount]

    return caldays,daylist,weeksum,shlst


def calmodalupdate(daylist, username, busarea):
    err='ok'
    my_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
    for j in range(len(daylist)):
        ilist=daylist[j]

        if ilist:
            if busarea=='Overseas':
                tid=ilist[0]  #tid=ilist[9]
                odat=OverSeas.query.get(tid)
            elif busarea=='Trucking':
                tid=ilist[9]
                odat=Orders.query.get(tid)

            fnum='cin'+str(tid)
            fput=request.values.get(fnum)
            try:
                if len(fput)>3:
                    if odat is not None:
                        odat.Container=fput
                        db.session.commit()

                fnum='csel'+str(tid)
                fput=request.values.get(fnum)
                if fput != '1':
                    if odat is not None:
                        odat.Container=fput
                        db.session.commit()

                fnum='dsel'+str(tid)
                fput=request.values.get(fnum)
                if fput != '1':
                    if odat is not None:
                        odat.Driver=fput
                        db.session.commit()

                fnum='tsel'+str(tid)
                fput=request.values.get(fnum)
                if fput != '1':
                    tnum='tsel'+str(tid)
                    print(tnum)
                    trk=request.values.get(tnum)
                    ddat=Drivers.query.filter(Drivers.Name==odat.Driver).first()
                    fdat=FELVehicles.query.filter(FELVehicles.Unit==trk).first()
                    if ddat is not None and fdat is not None:
                        ddat.Truck=fdat.Unit
                        ddat.Tag=fdat.Plate
                        db.session.commit()

                fnum='note'+str(tid)
                fput=request.values.get(fnum)
                if len(fput)>3:
                    input = ChalkBoard(Jo=odat.Jo,register_date=my_datetime,creator=username,comments=fput)
                    db.session.add(input)
                    db.session.commit()

            except:
                err='Not Allowed'
    return err



def calendar7_weeks_all_old(lweeks):
    today = datetime.datetime.today()
    nweeks=lweeks[0]+lweeks[1]
    ndays=nweeks*7
    day=today.day
    d = today
    nlist=ndays*12
    caldays=list(range(ndays))
    caldt=list(range(ndays))
    daylist=list(range(nlist))
    shlst=list(range(nlist))
    days_ahead=[0]*nweeks
    calmon=[0]*nweeks
    next_weekday=[0]*nweeks
    datestr=[0]*nweeks

    for i in range(ndays):
        for j in range(12):
            k=9*i+j
            daylist[k]=0

    for i in range(7):
        days_ahead1 = i - 7 - d.weekday()
        if days_ahead1 <= 0:
            days_ahead1 += 7
        day0=days_ahead1-7*lweeks[0]
        for m in range(nweeks):
            days_ahead[m]=day0+7*m
            next_weekday[m] = d + datetime.timedelta(days_ahead[m])
            calmon[m]=str(next_weekday[m].month)
            caldays[i+7*m]=   calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[m])] + ' ' + str(next_weekday[m].day)
            datestr[m]=str(next_weekday[m].month) + '/' + str(next_weekday[m].day) + '/' + str(next_weekday[m].year)
            caldt[i+7*m] = datetime.datetime.strptime(datestr[m], '%m/%d/%Y')

        if next_weekday[lweeks[0]].day==day:
            caldays[i+7*lweeks[0]]=   'X' + calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[lweeks[0]])] + ' ' + str(next_weekday[lweeks[0]].day)



    if 1==1:
        weeksum=0
        j1=0
        j2=0
        j3=0
        j4=0
        j5=0
        for i in range(ndays):
            dloc=caldt[i]
            dloc2=dloc+datetime.timedelta(days=1)

#___Overseas Part________________________________________________________________

            odata = OverSeas.query.filter(OverSeas.PuDate==dloc).all()
            for j1,data in enumerate(odata):
                k=12*i+j1
                shipper=data.BillTo
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]

                pod=data.Pod
                pol=data.Pol
                if len(pod)>8:
                    pod=re.match(r'\W*(\w[^,. !?"]*)', pod).groups()[0]
                if len(pol)>8:
                    pol=re.match(r'\W*(\w[^,. !?"]*)', pol).groups()[0]

                container=data.Container
                book=data.Booking
                bdat=Bookings.query.filter(Bookings.Booking==data.Booking).first()
                if bdat is not None:
                    doccut=bdat.PortCut.strftime('%m/%d/%Y')
                else:
                    doccut=''
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                lt=data.Jo
                lt=lt[6:8]
                shlst[k]=[lt, 'O', 'blue darken-4']
                daylist[k]=[data.id, shipper, book, container, pol, pod, data.Jo, data.Status, data.Driver, phone, trk, plate, doccut, cb]

#___Trucking Part________________________________________________________________
            tdata = Orders.query.filter((Orders.Date >= dloc) & (Orders.Date < dloc2)).all()
            for j2,data in enumerate(tdata):
                k=12*i+j1+j2+1


                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=People.query.filter((People.Company==data.Company) & (People.Ptype=='Trucking')).first()
                loc2=People.query.filter((People.Company==data.Company2) & (People.Ptype=='Trucking')).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12=''
                    addr22=''
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                lt=data.Jo
                lt=lt[6:8]
                shlst[k]=[lt, 'T', 'red darken-4']
                daylist[k]=[data.Order, data.Pickup, data.Booking, data.Driver, data.Time, data.Jo, data.Container, data.Status, shipper, data.id, data.Company, addr11, addr21, data.Company2, addr12, addr22, phone, trk, plate, cb]

#___Horizon/Towing Part________________________________________________________________
            adata = db.session.query(Autos.TowCompany).distinct().filter(Autos.Date2==dloc)
            for j3,data in enumerate(adata):


                adat=Autos.query.filter(Autos.TowCompany==data.TowCompany).first()
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==adat.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)
                com=adat.TowCompany
                if com is None or com=='' or len(com)<2:
                    com='FIX'

                if adat is not None:
                    autolist=[]
                    allcars=Autos.query.filter(Autos.TowCompany==adat.TowCompany).all()
                    for car in allcars:
                        autolist.append([car.Year,car.Make,car.Model,car.VIN])


                try:
                    amt=adat.TowCost
                    amt=nononef(amt)
                    ncars=len(autolist)
                    amteach=amt/ncars
                    amteach=dollar(amteach)
                except:
                    amteach='0.00'
                    ncars=0

                k=12*i+j1+j2+j3+2
                shlst[k]=[adat.TowCost, 'H', 'amber accent-4']
                daylist[k]=[adat.id, com, adat.TowCost, adat.Status, autolist, cb, adat.Jo, amteach, ncars]
#___Moving Part________________________________________________________________

            mdata = Moving.query.filter(Moving.Date == dloc).all()
            for j4,data in enumerate(mdata):
                k=12*i+j1+j2+j3+j4+3
                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=Drops.query.filter(Drops.Entity==data.Drop1).first()
                loc2=Drops.query.filter(Drops.Entity==data.Drop2).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12='NF'
                    addr22='NF'
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                lt=data.Jo
                lt=lt[6:8]
                shlst[k]=[lt, 'M']
                daylist[k]=[data.id, data.Jo, shipper, data.Drop1, addr11, addr21, data.Time, data.Drop2, addr12, addr22, data.Time2, data.Container, data.Driver, data.Status, phone, trk, plate, cb, data.Amount]





#___Billing Part________________________________________________________________
            adata= Accounts.query.all()
            bdata = FELBills.query.filter(FELBills.bDate == dloc)
            for j5,data in enumerate(bdata):
                k=12*i+j1+j2+j3+j4+j5+4

                billno='Bill'+str(data.id)
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==billno).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                shlst[k]=[data.bAmount, 'B', 'green darken-4']
                daylist[k]=[data.id, data.Company, data.bAmount, data.Account, data.Status, data.bType, data.bClass, cb]


    return caldays,daylist,weeksum,shlst
