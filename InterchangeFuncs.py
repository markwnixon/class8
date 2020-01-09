from runmain import db
from models import OverSeas, Orders, People, Interchange, Bookings
from flask import session, request
from viewfuncs import d2s, stat_update
import datetime
import pytz

my_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
today = my_datetime.date()
now = my_datetime.time()

def InterStrip(id):
    data = Interchange.query.get(id)
    release=data.RELEASE
    contain=data.CONTAINER
    chassis=data.CHASSIS
    if chassis is None:
        chassis='Own'
    if release is None:
        release='TBD'
    if contain is None:
        contain='TBD'
    release=release.strip()
    contain=contain.strip()
    chassis=chassis.strip()
    data.RELEASE=release
    data.CONTAINER=contain
    data.CHASSIS=chassis
    db.session.commit()

def InterRestart():
    idata=Interchange.query.filter( (Interchange.Status != 'AAAAAA') ).all()
    for data in idata:
        data.Status='Unmatched'
        db.session.commit()

def InterMatchV2():
    kdata = db.session.query(Interchange.CONTAINER).distinct()
    for data in kdata:
        container=data.CONTAINER
        idat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.CONTAINER==container) ).first()
        if idat is not None:
            testid=idat.id
            type=idat.TYPE
            if 'In' in type:
                matcher='Out'
            else:
                matcher='In'
            mdat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.TYPE.contains(matcher)) & (Interchange.CONTAINER==container)).first()
            if mdat is not None:
                idat.Status='IO'
                mdat.Status='IO'
                db.session.commit()

def InterMatchThis(id):
    idat=Interchange.query.get(id)
    container=idat.CONTAINER
    release=idat.RELEASE
    type=idat.TYPE
    if 'In' in type:
        matcher='Out'
    else:
        matcher='In'
    mdat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.TYPE.contains(matcher)) & (Interchange.CONTAINER==container)).first()
    if mdat is not None:
        idat.Status='IO'
        mdat.Status='IO'
        db.session.commit()
    odat=Orders.query.filter( (Orders.Container==container) | (Orders.Booking==release) ).first()
    if odat is not None:
        hstat = odat.Hstat
        if hstat==0 and 'Out' in type:
            if(odat.Container)=='TBD':
                odat.Container=idat.CONTAINER
            odat.Hstat = 1
            db.session.commit()
        if hstat==1 and 'In' in type:
            odat.Hstat = 2
            db.session.commit()
    odat=OverSeas.query.filter( (OverSeas.Container==container) | (OverSeas.Booking==release) ).first()
    if odat is not None:
        status=odat.Status
        bit1=status[0]
        if bit1=='0' and 'Out' in type:
            if(odat.Container)=='TBD':
                odat.Container=idat.CONTAINER
            newstatus=stat_update(status,'1',0)
            odat.Status=newstatus
            db.session.commit()
        if bit1=='1' and 'In' in type:
            newstatus=stat_update(status,'2',0)
            odat.Status=newstatus
            db.session.commit()

def Remove_Dup_Jobs():
    odata=OverSeas.query.all()
    for odat in odata:
        container=odat.Container
        booking=odat.Booking
        tdat=Orders.query.filter( (Orders.Container==container) | (Orders.Booking == booking) ).first()
        if tdat is not None:
            Orders.query.filter(Orders.id == tdat.id).delete()
            #Now change any interchange tickets that may have wrong company data
            idata=Interchange.query.filter( (Interchange.CONTAINER==container)|(Interchange.RELEASE==booking) ).all()
            for idat in idata:
                idat.Company = odat.BillTo
    db.session.commit()



def Matched_Now():
    odata=Orders.query.filter(Orders.Hstat < 2).all()
    for data in odata:
        container=data.Container
        if container is None:
            container='TBD'
        idat = Interchange.query.filter((Interchange.Status=='IO') & ( (Interchange.RELEASE==data.Booking) | (Interchange.CONTAINER==data.Container) ) ).first()
        idatO = Interchange.query.filter((Interchange.Status == 'BBBBBB') & ((Interchange.RELEASE == data.Booking) | (Interchange.CONTAINER == data.Container))).first()

        if idat is not None:
            hstat=data.Hstat
            if hstat < 2:
                data.Hstat = 2
            if container=='TBD':
                data.Container=idat.CONTAINER
                db.session.commit()
        elif idatO is not None:
            hstat=data.Hstat
            if hstat < 2:
                data.Hstat = 1
            if container=='TBD':
                data.Container=idatO.CONTAINER
                db.session.commit()
        else:
            idat2=Interchange.query.filter((Interchange.Status=='BBBBBB') & ( (Interchange.RELEASE==data.Booking) | (Interchange.CONTAINER==data.Container) ) ).first()
            if idat2 is not None:
                type=idat2.TYPE
                if 'Out' in type:
                    hstat = data.Hstat
                    if hstat == 0:
                        data.Hstat = 1
                        con=data.Container
                        if con is None or len(con<10):
                            data.Container=idat.CONTAINER
                        db.session.commit()

    #idata=Interchange.query.filter(~Interchange.Jo.contains('F')).all()
    idata=Interchange.query.filter(Interchange.Jo=='NAY').all()
    for idat in idata:
        container=idat.CONTAINER
        booking=idat.RELEASE
        tdat=Orders.query.filter( (Orders.Container==container) | (Orders.Booking==booking) ).first()
        if tdat is not None:
            idat.Jo=tdat.Jo
            idat.Company=tdat.Shipper
            if booking is None or len(booking)<5:
                idat.RELEASE=tdat.Booking
            db.session.commit()
        odat=OverSeas.query.filter( (OverSeas.Container==container) | (OverSeas.Booking==booking) ).first()
        if tdat is None and odat is not None:
            idat.Jo=odat.Jo
            idat.Company=odat.BillTo
            if booking is None or len(booking)<5:
                idat.RELEASE=odat.Booking
            db.session.commit()
        if odat is None and tdat is None:
            chassis=idat.CHASSIS
            if chassis is not None:
                if 'jay' in chassis.lower():
                    idat.Jo='Jay'
                    idat.Company='Jays Auto'


def InterRematch():
    for data in kdata:
        container=data.CONTAINER
        idat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (Interchange.CONTAINER==container) ).first()
        if idat is not None:
            testid=idat.id
            type=idat.TYPE
            if 'In' in type:
                matcher='Out'
            else:
                matcher='In'
            mdat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (Interchange.TYPE.contains(matcher)) & (Interchange.CONTAINER==container)).first()
            if mdat is not None:
                idat.Status='IO'
                mdat.Status='IO'
                db.session.commit()

def InterDups():
    kdata = db.session.query(Interchange.CONTAINER).distinct()
    for data in kdata:
        container=data.CONTAINER
        idat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.CONTAINER==container) ).first()
        if idat is not None:
            testid=idat.id
            type=idat.TYPE
            if 'In' in type:
                matcher='Out'
            else:
                matcher='In'

            #Test if other tickets are duplicate to this one:
            dupdata=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.id != testid) & (Interchange.TYPE==type) & (Interchange.CONTAINER==container)).all()
            for dup in dupdata:
                dup.Status='Dup'+str(testid)
                db.session.commit()

            #Test if this ticket is a duplicate to a match already made:
            dupdata2=Interchange.query.filter( (Interchange.Status.contains('IO')) & (Interchange.id!=testid) & (Interchange.TYPE==type) & (Interchange.CONTAINER==container)).first()
            if dupdata2 is not None:
                idat.Status='Dup to IO'+str(dupdata2.id)
                db.session.commit()

def InterDupThis(id):
    idat=Interchange.query.get(id)
    container=idat.CONTAINER
    testid=idat.id
    type=idat.TYPE

    #Test if ticket is a duplicate to other match eligible tickets:
    dupdata=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('IO')) & (Interchange.id != testid) & (Interchange.TYPE==type) & (Interchange.CONTAINER==container)).first()
    if dupdata is not None:
        idat.Status='Dup'+str(dupdata.id)
        db.session.commit()

    #Test if this ticket is a duplicate to a match already made:
    dupdata2=Interchange.query.filter( (Interchange.Status.contains('IO')) & (Interchange.id != testid) & (Interchange.TYPE==type) & (Interchange.CONTAINER==container)).first()
    if dupdata2 is not None:
        idat.Status='Dup to IO'+str(dupdata2.id)
        db.session.commit()



def Push_Overseas():
    kdata = db.session.query(Interchange.CONTAINER).distinct()
    for data in kdata:
        container=data.CONTAINER
        idat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('Lock')) & (Interchange.CONTAINER==container) & (Interchange.TYPE.contains('Out')) ).first()
        if idat is not None:
            testid=idat.id
            type=idat.TYPE
            booking=idat.RELEASE

            odat=OverSeas.query.filter(OverSeas.Booking==booking).first()
            if odat is not None:
                odat.Container=container
                idat.Company=odat.BillTo
                idat.Jo=odat.Jo
                status=odat.Status
                bit1=status[0]
                if bit1=='0':
                    newstatus=stat_update(status,'1',0)
                    odat.Status=newstatus
                #See if there is a matching interchange ticket to update as well
                mdat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('Lock')) & (Interchange.CONTAINER==container) & (Interchange.TYPE.contains('In')) ).first()
                if mdat is not None:
                    mdat.Company=odat.BillTo
                    mdat.Jo=odat.Jo
                    if bit1=='0' or bit1=='1':
                        newstatus=stat_update(status,'2',0)
                        odat.Status=newstatus

                db.session.commit()

def Push_Orders():
    kdata = db.session.query(Interchange.CONTAINER).distinct()
    for data in kdata:
        container=data.CONTAINER
        idat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('Lock')) & (Interchange.CONTAINER==container) & (Interchange.TYPE.contains('Out')) ).first()
        if idat is not None:
            testid=idat.id
            type=idat.TYPE
            booking=idat.RELEASE

            odat=Orders.query.filter( (Orders.Booking==booking) | (Orders.Container==container) ).first()
            if odat is not None:
                idat.Company=odat.Shipper
                idat.Jo=odat.Jo
                hstat = odat.Hstat
                if hstat == 0:
                    odat.Hstat = 1
                db.session.commit()

                #See if there is a matching interchange ticket to update as well
                mdat=Interchange.query.filter( (Interchange.Status != 'AAAAAA') & (~Interchange.Status.contains('Lock')) & (Interchange.CONTAINER==container) & (Interchange.TYPE.contains('In')) ).first()
                if mdat is not None:
                    mdat.Company=odat.Shipper
                    mdat.Jo=odat.Jo
                    if hstat<2:
                        odat.Hstat=2
                    db.session.commit()

def Order_Container_Update(oder):
    odat = Orders.query.get(oder)
    booking=odat.Booking
    container=odat.Container
    idata=Interchange.query.filter( (Interchange.RELEASE==booking) | (Interchange.CONTAINER==container)).all()
    for idat in idata:
        type=idat.TYPE
        print(odat.Shipper)
        idat.Company=odat.Shipper
        idat.Jo=odat.Jo
        hstat=odat.Hstat
        if hstat is None:
            hstat = 0
        if 'Out' in type and hstat<1:
            odat.Hstat = 1
            db.session.commit()
        if 'In' in type:
            odat.Hstat = 2
            db.session.commit()



def PushJobsThis(id):

    idat=Interchange.query.get(id)
    testid=idat.id
    type=idat.TYPE
    booking=idat.RELEASE
    container=idat.CONTAINER

    odat=OverSeas.query.filter(OverSeas.Booking==booking).first()
    if odat is not None:
        odat.Container=container
        idat.Company=odat.BillTo
        idat.Jo=odat.Jo

        status=odat.Status
        bit1=status[0]
        if bit1=='0' and 'Out' in type:
            newstatus=stat_update(status,'1',0)
            odat.Status=newstatus
        if 'Out' in type:
            odat.PuDate=idat.Date

        if (bit1=='1' or bit1=='0') and 'In' in type:
            newstatus=stat_update(status,'2',0)
            odat.Status=newstatus
        if 'In' in type:
            odat.RetDate=idat.Date

        db.session.commit()

    odat=Orders.query.filter( (Orders.Booking==booking) & ( (Orders.Container=='TBD') | (Orders.Container==container) ) ).first()
    if odat is not None:
        idat.Company=odat.Shipper
        idat.Jo=odat.Jo
        odat.Container=container
        hstat = odat.Hstat
        if hstat == 0 and 'Out' in type:
            odat.Hstat=1
        if 'Out' in type:
            odat.Date=idat.Date
        if hstat<2 and 'In' in type:
            odat.Hstat=2
        if 'In' in type:
            odat.Date2=idat.Date
        db.session.commit()


        #And also push back to Interchange in case several new bookings have been created
    odata=OverSeas.query.filter(OverSeas.Container=='TBD')
    for data in odata:
        container=data.Container
        company=data.BillTo
        booking=data.Booking
        idat=Interchange.query.filter((Interchange.RELEASE==booking) & (Interchange.Status != 'AAAAAA') ).first()
        if idat is not None:
            data.Container=idat.CONTAINER
            idat.Company=company
            idat.Jo=data.Jo
            db.session.commit()





def InterMatchOld():
    idata = db.session.query(Interchange.CONTAINER).distinct()
    for data in idata:
        idat=Interchange.query.filter((Interchange.CONTAINER==data.CONTAINER) & (Interchange.Status != 'AAAAAA') & ( ~Interchange.Status.contains('IO') )).first()
        if idat is not None:
            stat1=idat.CONTAINER
            amatch=Interchange.query.filter( (Interchange.CONTAINER==stat1) & (Interchange.id != idat.id) & (Interchange.Status != 'AAAAAA') & ( ~Interchange.Status.contains('IO') )).all()
            t1=len(amatch)
            print('The length of the query is: ',t1)
            if t1==0:
                print('There is no match for Container: ',stat1)
                idat.Status='Unmatched'
                db.session.commit()
            elif t1==1:
                for match in amatch:
                    if ('In' in idat.TYPE and 'Out' in match.TYPE) or ('Out' in idat.TYPE and 'In' in match.TYPE):
                        print('The match is correct for Container: ',stat1,idat.id,idat.Status,match.id,match.Status,'will now become IO')
                        idat.Status='IO'
                        match.Status='IO'
                        db.session.commit()
                    else:
                        print('There are two containers, but mismatch in Type for Container: ',stat1)
                        keystatus='Mismatch'+str(idat.id)
                        match.Status=keystatus
                        idat.Status=keystatus
                        db.session.commit()
            elif t1>0:
                print('There are more than two Containers: ',stat1)
                idat.Status='Multimatch'+str(idat.id)
                db.session.commit()
                for match in amatch:
                    match.Status='Multimatch'+str(idat.id)
                    db.session.commit()

def Check_Sailing():

    odata=OverSeas.query.filter(OverSeas.Status != '999').all()
    for data in odata:
        status=data.Status
        bit1=int(status[0])
        if bit1<6:
            bdat=Bookings.query.filter(Bookings.Booking==data.Booking).first()
            if bdat is not None:
                date1=data.PuDate
                date2=bdat.SailDate
                date3=bdat.EstArr

                if today>date2 and today<date3:
                    bit1=3

                if today>date3:
                    bit1=4

                status=stat_update(status,str(bit1),0)
                print('For booking ',data.Booking, 'status= ',status)

                data.Status=status
                db.session.commit()
