from runmain import db
from models import Driverlog, users, JO, Gledger
from flask import session, logging, request
import datetime
from CCC_system_setup import scac

def dataget_Driverlog(thismuch):
    # 0=order,#1=proofs,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    odata = Driverlog.query.all()
    return odata

def isoDriver():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec, numcheckv

        #Zero and blank items for default
        username = session['username'].capitalize()
        cache=request.values.get('cache')
        cache=nonone(cache)

        modata=0
        modlink=0
        docref=''
        oderstring=''
        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=10

        match    =  request.values.get('Match')
        modify   =  request.values.get('Qmod')
        vmod   =  request.values.get('Vmod')
        viewo     =  request.values.get('View')
        print    =  request.values.get('Print')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        delfile = request.values.get('DELF')
        # hidden values
        update   =  request.values.get('Update')
        newact=request.values.get('NewA')
        thisjob=request.values.get('ThisJob')
        oder=request.values.get('oder')
        modlink = request.values.get('modlink')
        thismuch = request.values.get('thismuch')

        oder=nonone(oder)
        modlink=nonone(modlink)

        leftscreen=1
        err=['All is well', ' ', ' ', ' ', ' ']

        if returnhit is not None:
            modlink=0
            depojo=0
            depdata=[0,0,0]


# ____________________________________________________________________________________________________________________E.FormVariables.General
# ____________________________________________________________________________________________________________________B.DataUpdates.General

        if modlink==1:
            if oder > 0:
                modata=Driverlog.query.get(oder)
                vals=['cn', 'co', 'gi', 'go', 'ostr', 'osto', 'over', 'tstr', 'tstp', 'drv', 'locstr', 'locstp']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)

                modata.Clockin=a[0]
                modata.Clockout=a[1]
                modata.GPSin=a[2]
                modata.GPSout=a[3]
                modata.Odomstart=a[4]
                modata.Odomstop=a[5]
                modata.Odverify=a[6]
                modata.Truckstart=a[7]
                modata.Truckstop = a[8]
                modata.Driver = a[9]
                modata.Locationstart = a[10]
                modata.Locationstop = a[11]
                db.session.commit()
                err[3]= 'Modification to Driverlog' + str(modata.id) + ' completed.'
                if update is not None:
                    modlink=0
                    leftsize=10
                else:
                    leftsize=6
                    leftscreen=0
                    modata=Driverlog.query.get(oder)

# ____________________________________________________________________________________________________________________B.GetData.General
        #odata = Driverlog.query.all()
        odata = dataget_Driverlog(thismuch)
# ____________________________________________________________________________________________________________________B.Search.General

        if modlink==0:
            oder,numchecked=numcheck(1,odata,0,0,0,0,['oder'])

# ____________________________________________________________________________________________________________________E.Search.General

# ____________________________________________________________________________________________________________________B.Modify.General
        if (modify is not None or vmod is not None) and numchecked==1 :
            modlink=1
            leftsize=6
            if vmod is not None:
                leftscreen=0

            if oder>0:
                modata=Driverlog.query.get(oder)
                docref=modata.Maintrecord

        if (modify is not None or vmod is not None) and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.Modify.General

# ____________________________________________________________________________________________________________________B.Delete.General
        if deletehit is not None and numchecked==1:
            if oder>0:
                #This section is to determine if we can delete the source file along with the data.  If other data is pointing to this
                #file then we need to keep it.
                modata=Driverlog.query.get(oder)

                Driverlog.query.filter(Driverlog.id == oder).delete()
                db.session.commit()
                odata = dataget_Driverlog(thismuch)


        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']



        if viewo is not None and numchecked == 1:
            if oder>0:
                modata=Driverlog.query.get(oder)
                docref = f'tmp/{scac}/data/vmaint/' + str(modata.id) + '.pdf'
                leftscreen = 0


        if cache is not None:
            #Save the current cache so we do not start from bad place in future
            udat=users.query.filter(users.name=='cache').first()
            udat.username=str(cache)
            udat.email=oderstring
            db.session.commit()

    else:
        from viewfuncs import popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder=0
        modata=0
        modlink=0
        odata = Driverlog.query.all()
        leftscreen=1
        leftsize=10
        docref=''
        err=['All is well', ' ', ' ', ' ',  ' ']
        thismuch = '2'
        udat=users.query.filter(users.name=='Cache').first()
        cache=udat.username
        cache=nonone(cache)
        depdata = [0,0,0]
        odata = dataget_Driverlog(thismuch)

    leftsize = 8


    return odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,docref,cache,thismuch
