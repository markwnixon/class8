from runmain import db
from models import Vehicles, Invoices, JO, Income, Bills, Accounts, OverSeas, Orders, Moving, Storage
from models import Autos, People, Interchange, Drivers, ChalkBoard, Proofs, Services, Moving, Drops
from flask import session, logging, request
import datetime
import calendar
import re
import os
import subprocess

#Create a Bill of Lading
def make_T_manifest_edit(oder):

    if request.method == 'POST':
        retval=0
        incoming=request.values.get('incoming')
        manview=request.values.get('VIEW')
        manprint=request.values.get('PRNT')
        manemail=request.values.get('EMAIL')
        update=request.values.get('UP')
        retrn=request.values.get('RET')
        retrnO=request.values.get('RETO')
        manviewo=request.values.get('OVIEW')
        if jtype is not None:
            incoming=1
        if jtype is None:
            jtype=request.values.get('jtype')
        print('inside isoL oder,jtype,incoming:',oder,jtype,incoming)



        if retrn is not None:
            retval='T'
        if retrnO is not None:
            retval='O'

        print(retval)
        #return redirect('/Trucking')
        def nonone(input):
            if input is not None:
                output=int(input)
            else:
                output=0
            return output

        if incoming is not None:
            jo=request.values.get('order2')
            location=''

            if jtype=='Trucking':
                #odata=Orders.query.filter(Orders.Jo==jo).first()
                odata=Orders.query.get(oder)
                jo = odata.Jo
                company1=odata.Company
                company2=odata.Company2
                driver=odata.Driver
                bol=odata.BOL
                location=odata.Location
                description=odata.Description
                date=odata.Date
                date2=odata.Date2
                time=odata.Time
                time2=odata.Time2

            if jtype=='Overseas':
                print(jo)
                odata=OverSeas.query.filter(OverSeas.Jo==jo).first()
                company1=odata.Origin
                company2=odata.Pol
                driver=odata.Driver
                description=odata.Description
                bol=''
                time=datetime.datetime.now().strftime('%H:%M')
                time2=datetime.datetime.now().strftime('%H:%M')
                date=odata.PuDate
                date2=odata.RetDate
                if description is None or description=='' or description=='None' or len(description)<1 or description=='Automobiles':
                    description='Unspecified'
                    adat=Autos.query.filter(Autos.Jo==odata.Jo).first()
                    if adat is not None:
                        ncars=str(adat.Ncars)
                        description='Automobiles'
                        location=ncars + ' Units'
                else:
                    location=''

            if jtype=='Moving':
                order=nonone(order)
                odata=Moving.query.get(order)
                company1=odata.Drop1
                company2=odata.Drop2
                driver=odata.Driver
                description=odata.Description
                location=''

            if jtype == 'Overseas':
                cdata1=People.query.filter((People.Company == company1) & (People.Ptype=='Overseas')).first()
                cdata2=People.query.filter((People.Company == company2) & (People.Ptype=='Overseas')).first()

            if jtype == 'Moving' or jtype == 'Trucking':
                cdata1=Drops.query.filter(Drops.Entity == company1).first()
                cdata2=Drops.query.filter(Drops.Entity == company2).first()

            try:
                tdata=Drivers.query.filter(Drivers.Name == driver).first()
                vdata=FELVehicles.query.filter(FELVehicles.Unit == tdata.Truck).first()
                drv_email=tdata.Email
                truck=tdata.Truck
                tag=vdata.Plate
            except:
                truck='unknown'
                tag='unknown'
                drv_email='unknown'

            pdata=People.query.filter((People.Ptype=='Trucking')|(People.Ptype=='Overseas')|(People.Ptype=='Moving')).order_by(People.Company).all()
            alltdata=Drivers.query.all()
            allvdata=FELVehicles.query.all()
            pval=0

        else:
            print('jtype',jtype,oder)
            if jtype=='Trucking':
                odata=Orders.query.get(oder)
                order=odat.Order
                date=odat.Date
            pval=1
            print('jtype',jtype,order)

            if jtype=='Overseas':
                odata=OverSeas.query.filter(OverSeas.Booking==order).first()
            if jtype=='Moving':
                tid=request.values.get('tid')
                tid=nonone(tid)
                odata=Moving.query.get(tid)

            driver=request.values.get('driver')
            date=request.values.get('date')
            date1dt = datetime.datetime.strptime(date, '%Y-%m-%d')
            time=request.values.get('time')
            date2=request.values.get('date2')
            date2dt = datetime.datetime.strptime(date2, '%Y-%m-%d')
            time2=request.values.get('time2')
            truck=request.values.get('truck')
            drv_email=request.values.get('drv_email')
            laddr1=request.values.get('laddr1')
            laddr2=request.values.get('laddr2')
            daddr1=request.values.get('daddr1')
            daddr2=request.values.get('daddr2')

            company=request.values.get('company')
            company2=request.values.get('company2')

            container=request.values.get('container')
            type=request.values.get('type')
            book=request.values.get('book')
            shipper=request.values.get('shipper')
            pickup=request.values.get('pickup')
            location=request.values.get('location')
            description=request.values.get('description')
            seal=request.values.get('seal')
            bol=request.values.get('bol')

            if container == 'None' or container is None:
                if type=='' or type=='None' or type is None:
                    type='53 Dry'

            if jtype == 'Overseas':
                cdata1=People.query.filter(People.Company == company).first()
                if cdata1 is not None:
                    cdata1.Addr1=laddr1
                    cdata1.Addr2=laddr2

                cdata2=People.query.filter(People.Company == company2).first()
                if cdata2 is not None:
                    cdata2.Addr1=daddr1
                    cdata2.Addr2=daddr2
            else:
                cdata1=Drops.query.filter(Drops.Entity == company).first()
                cdata2=Drops.query.filter(Drops.Entity == company2).first()

           # if update is None:

        if jtype=='Trucking' or jtype=='Moving':
            docref=odata.Path
        elif jtype=='Overseas':
            docref=odata.Apath

        try:
            doctxt=docref.split('.',1)[0]+'.txt'
        except:
            doctxt=None

        try:
            tdata=Drivers.query.filter(Drivers.Name == driver).first()
            drv_email=tdata.Email
            tdata.Tag=tag
            tdata.Truck=truck
        except:
            drv_email='NoDriver'
        try:
            vdata=FELVehicles.query.filter(FELVehicles.Unit == truck).first()
            tag=vdata.Plate
        except:
            tag='NoUnit'


        pdata=People.query.filter((People.Ptype=='Trucking')|(People.Ptype=='Overseas')).order_by(People.Company).all()
        alltdata=Drivers.query.all()
        allvdata=FELVehicles.query.all()

        if incoming is None and jtype=='Trucking':
            odata.Driver=driver
            odata.Date=date
            odata.Time=time
            odata.Date2=date2dt
            odata.Time2=time2
            odata.Company=company
            odata.Company2=company2
            odata.Container=container
            odata.Type=type
            odata.Booking=book
            odata.Shipper=shipper
            odata.Pickup=pickup
            odata.Location=location
            odata.Seal=seal
            odata.BOL=bol
            odata.Description=description
            db.session.commit()

        if incoming is None and jtype=='Moving':
            odata.Driver=driver
            odata.Date=date
            odata.Time=time
            odata.Date2=date2dt
            odata.Time2=time2
            odata.Container=container
            odata.Type=type
            odata.Booking=book
            odata.Shipper=shipper
            odata.Pickup=pickup
            odata.Seal=seal
            odata.BOL=bol
            odata.Description=description
            db.session.commit()

        if incoming is None and jtype=='Overseas':
            odata.Driver=driver
            odata.PuDate=date
            odata.RetDate=date2
            odata.Origin=company
            odata.Pol=company2
            odata.Container=container
            odata.ContainerType=type
            odata.Booking=book
            odata.Seal=seal
            odata.Description=description
            db.session.commit()

        if manview is not None or update is not None or manviewo is not None:
            if jtype=='Trucking':
                cache=odata.Storage
                cache=nonone(cache)+1
                pdata1=People.query.filter(People.Company==odata.Shipper).first()
                pdata2=Drops.query.filter(Drops.Entity==odata.Company).first()
                pdata3=Drops.query.filter(Drops.Entity==odata.Company2).first()
            #import pdfmaker1
            #pdfmaker1.main(odata, cdata1, cdata2, tdata)
                import makemanifest2
                makemanifest2.main(odata, pdata1, pdata2, pdata3, tdata, cache, jtype, time, time2, location, description, bol)

                docref='tmp/data/vmanifest/Manifest'+odata.Jo+'c'+str(cache)+'.pdf'

                odata.Path=docref
                odata.Storage=cache
                db.session.commit()
                pval=1

            if jtype=='Overseas':
                cache=odata.Cache
                cache=nonone(cache)+1
                pdata1=People.query.filter(People.Company==odata.BillTo).first()
                pdata2=People.query.filter(People.Company==odata.Origin).first()
                pdata3=People.query.filter(People.Company==odata.Pol).first()
            #import pdfmaker1
            #pdfmaker1.main(odata, cdata1, cdata2, tdata)
                import makemanifest2
                makemanifest2.main(odata, pdata1, pdata2, pdata3, tdata, cache, jtype, time, time2, description, location, bol)

                docref='tmp/data/vmanifest/Manifest'+odata.Jo+'c'+str(cache)+'.pdf'

                odata.Apath=docref
                odata.Cache=cache
                db.session.commit()
                pval=1

            if jtype=='Moving':
                cache=odata.Cache
                cache=nonone(cache)+1
                pdata1=People.query.filter(People.Company==odata.Shipper).first()
                pdata2=Drops.query.filter(Drops.Entity==odata.Drop1).first()
                pdata3=Drops.query.filter(Drops.Entity==odata.Drop2).first()
            #import pdfmaker1
            #pdfmaker1.main(odata, cdata1, cdata2, tdata)
                import makemanifest2
                makemanifest2.main(odata, pdata1, pdata2, pdata3, tdata, cache, jtype, time, time2, description, location, bol)

                docref='tmp/data/vmanifest/Manifest'+odata.Jo+'c'+str(cache)+'.pdf'

                odata.Path=docref
                odata.Cache=cache
                db.session.commit()
                pval=1

            #Just for viewing we want to see the source document
            if manviewo is not None and jtype=='Trucking':
                docref='tmp/data/vorders/'+odata.Original

            if manviewo is not None and jtype=='Overseas':
                docref='tmp/data/vdockr/'+odata.Dpath

        if manemail is not None:
            import mimemail_pdfmaker1
            mimemail_pdfmaker1.main(odata, cdata1, cdata2, tdata)
            pval=1

        if manprint is not None:
            ckj=subprocess.check_output(['lpr', docref])
            pval=1


    return odata,jtype,cdata1,cdata2,tdata,pdata,pval,alltdata,allvdata,description,location,docref,bol,time,time2,date2,retval
