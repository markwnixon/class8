from runmain import db
from models import Accounts
from flask import session, logging, request
import datetime

def isoAM():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec

        #Zero and blank items for default
        username = session['username'].capitalize()
        cache=0
        modata=0
        modlink=0
        scdata=0

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=10

        match    =  request.values.get('Match')
        modify   =  request.values.get('Qmod')
        viewo     =  request.values.get('ViewO')
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
        companyon = request.values.get('actype')
        if companyon is not None:
            tester=companyon[0]
        else:
            tester='A'
            companyon='Show All Accounts'

        oder=nonone(oder)
        modlink=nonone(modlink)

        leftscreen=1
        err=['All is well', ' ', ' ', ' ', ' ']

        if returnhit is not None:
            modlink=0


# ____________________________________________________________________________________________________________________E.FormVariables.General
# ____________________________________________________________________________________________________________________B.DataUpdates.General

        if modlink==1:
            if oder > 0:
                modata=Accounts.query.get(oder)
                vals=['acctname','accttype','acctcat','acctsub','acctnumb','acctrout','acctpaye','acctdesc','accttax','acctco']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)

                modata.Name=a[0]
                modata.Type=a[1]
                modata.Category=a[2]
                modata.Subcategory=a[3]
                modata.AcctNumber=a[4]
                modata.Routing=a[5]
                modata.Payee=a[6]
                modata.Description=a[7]
                modata.Taxrollup=a[8]
                modata.Co=a[9]

                if a[3] == 'New' or a[3] is None:
                    getnewsub=request.values.get('newgaexpense')
                    modata.Subcategory=getnewsub

                db.session.commit()
                err[3]= 'Modification to Account id ' + str(modata.id) + ' completed.'
                if update is not None:
                    modlink=0
                    leftsize=10
                else:
                    leftsize=6
                    modata=Accounts.query.get(oder)

# ____________________________________________________________________________________________________________________B.GetData.General
        if tester=='S':
            odata = Accounts.query.all()
        elif tester=='O':
            odata = Accounts.query.filter(Accounts.Co=='K').all()
        else:
            odata = Accounts.query.filter(Accounts.Co=='J').all()
# ____________________________________________________________________________________________________________________B.Search.General

        if modlink==0:
            oder,numchecked=numcheck(1,odata,0,0,0,0,['oder'])

# ____________________________________________________________________________________________________________________E.Search.General

# ____________________________________________________________________________________________________________________B.Modify.General
        if modify is not None and numchecked==1 :
            modlink=1
            leftsize=6

            if oder>0:
                modata=Accounts.query.get(oder)

        if modify is not None and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.Modify.General

# ____________________________________________________________________________________________________________________B.Delete.General
        if deletehit is not None and numchecked==1:
            if oder>0:
                #This section is to determine if we can delete the source file along with the data.  If other data is pointing to this
                #file then we need to keep it.
                modata=Accounts.query.get(oder)

                Accounts.query.filter(Accounts.id == oder).delete()
                db.session.commit()

        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.General

# ____________________________________________________________________________________________________________________B.Newjob.General
        if newact is not None:
            modlink=10
            leftsize=6
            modata=Accounts.query.get(1)
            if modata is not None:
                modata.Name=''


        if newact is None and modlink==10:
            #Create the new database entry for the source document
            acctname=request.values.get('acctname')
            acctnumb=request.values.get('acctnumb')
            acctrout=request.values.get('acctrout')
            acctpaye=request.values.get('acctpaye')
            accttype=request.values.get('accttype')
            acctdesc=request.values.get('acctdesc')
            acctcat=request.values.get('acctcat')
            acctsub=request.values.get('acctsub')
            accttax=request.values.get('accttax')
            acctco=request.values.get('acctco')

            input = Accounts(Name=acctname,Balance=0.00,AcctNumber=acctnumb,Routing=acctrout,Payee=acctpaye,Type=accttype,Description=acctdesc,Category=acctcat,Subcategory=acctsub,Taxrollup=accttax,Co=acctco)
            db.session.add(input)
            db.session.commit()
            db.session.close()

            odata = Accounts.query.all()
            modata = odata[-1]
            oder=modata.id

            modlink=1
            leftsize=6
            err=['All is well', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Newjob.General

    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder=0
        cache=0
        modata=0
        modlink=0
        scdata=0
        odata = Accounts.query.all()
        companyon = 'Show All Accounts'
        leftscreen=1
        leftsize=10
        err=['All is well', ' ', ' ', ' ',  ' ']
    scdata=[]
    for odat in odata:
        catitem=odat.Category
        additem=odat.Subcategory
        if additem is not None and catitem is not None:
            if catitem=='G-A' and additem not in scdata:
                scdata.append(additem)
    scdata.sort()
    leftsize = 8


    return odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,scdata,companyon
