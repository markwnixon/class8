from runmain import db
from models import Accounts, Divisions, Accttypes, Focusareas, Taxmap
from flask import session, logging, request
import datetime, json

def isoAM():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef, stripper, check_shared, check_mirror_exp
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec, erud, hasinput, get_tmap, get_qmap

        #Zero and blank items for default
        username = session['username'].capitalize()
        cache=0
        modata=0
        modlink=0
        scdata=0
        tmap = None
        fmap = None
        qmap = None
        gmap = None

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        modify   =  request.values.get('Qmod')
        shared = request.values.get('Shared')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')


        # hidden values
        update   =  request.values.get('Update')
        newact=request.values.get('NewA')
        thisjob=request.values.get('ThisJob')
        oder=request.values.get('oder')
        modlink = request.values.get('modlink')
        companyon = request.values.get('actype')
        if companyon is None:
            companyon='Show All Accounts'

        oder=nonone(oder)
        modlink=nonone(modlink)

        leftscreen=1
        err=[]

        if returnhit is not None:
            modlink=0


# ____________________________________________________________________________________________________________________E.FormVariables.General
# ____________________________________________________________________________________________________________________B.DataUpdates.General

        if modlink==1:
            if oder > 0:
                modata=Accounts.query.get(oder)
                vals=['acctname','accttype','acctcat','acctsub','acctnumb','acctrout','acctpaye','acctdesc','accttax','acctco','qbmap']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)


                modata.Name=a[0]
                modata.Type=a[1]
                if a[1] is not None:
                    adat = Accttypes.query.filter(Accttypes.Name==a[1]).first()
                    if adat is not None:
                        defcat = adat.Category
                        defsub = adat.Subcategory

                if a[2] is None:
                    modata.Category = defcat
                else:
                    modata.Category=a[2]

                if a[3] is None:
                    modata.Subcategory = defsub
                else:
                    modata.Subcategory=a[3]

                modata.AcctNumber=a[4]
                modata.Routing=a[5]
                modata.Payee=a[6]
                modata.Description=a[7]
                modata.Taxrollup=a[8]
                modata.Co=a[9]
                modata.QBmap = a[10]

                db.session.commit()
                err.append('Modification to Account id ' + str(modata.id) + ' completed.')

                # Narrow the selection boxes for company and type
                print('a[1]', a[1])
                print(hasinput(a[1]))
                if hasinput(a[1]):
                    fmap = Focusareas.query.filter(Focusareas.Co == a[9]).all()
                    gmap = Taxmap.query.filter(Taxmap.Category.contains('deductions')).all()
                    tmap = get_tmap(a[1], a[2])
                    qmap = get_qmap(a[1], a[2])


                if update is not None:
                    modlink=0
                    leftsize=10
                else:
                    leftsize=6
                    modata=Accounts.query.get(oder)

# ____________________________________________________________________________________________________________________B.GetData.General
        if companyon == 'Show All Accounts':
            odata = Accounts.query.all()
        elif companyon == 'Show Shared Accounts':
            odata = Accounts.query.filter(Accounts.Shared != None).all()
        else:
            odata = Accounts.query.filter((Accounts.Co.contains(companyon))).all()
# ____________________________________________________________________________________________________________________B.Search.General

        if modlink==0:
            oder,numchecked=numcheck(1,odata,0,0,0,0,['oder'])
        else:
            numchecked = 0

# ____________________________________________________________________________________________________________________E.Search.General

        if shared is not None:
            if oder > 0 and numchecked == 1:
                odat = Accounts.query.get(oder)
                atype = odat.Type
                if atype == 'Expense':
                    co1 = odat.Co
                    thisdat = Divisions.query.filter(Divisions.Co == co1).first()
                    co1name = thisdat.Name
                    otherdat = Divisions.query.filter(Divisions.Co != co1).first()
                    sid = otherdat.id
                    co2 = otherdat.Co
                    co2name = otherdat.Name
                    err.append(f'Account **{odat.Name}** owned by code {odat.Co}')
                    err.append(f'Is now set up for share with {otherdat.Name} code {otherdat.Co}')

                    # Now check to see if the sharing accounts exist and if not create them
                    fromtoid, err = check_shared(co1,co2name, err)
                    tofromid, err = check_shared(co2,co1name, err)
                    mirrorexpid, err = check_mirror_exp(co2,odat.id,odat.Name,err)


                    slist = json.dumps([sid,fromtoid,tofromid,mirrorexpid])
                    odat.Shared = slist
                    db.session.commit()
                    mirrordat = Accounts.query.get(mirrorexpid)
                    mirrordat.Shared = slist
                    db.session.commit()

                    if companyon == 'Show All Accounts':
                        odata = Accounts.query.all()
                    elif companyon == 'Show Shared Accounts':
                        odata = Accounts.query.filter(Accounts.Shared != None).all()
                    else:
                        odata = Accounts.query.filter((Accounts.Co.contains(companyon))).all()

                else:
                    err.append(f'Cannot share: {odat.Name} of type {atype}')
                    err.append(f'Can only share and apportion **Expense** accounts')
            else:
                err.append(f'Must select one account to use this option')



# ____________________________________________________________________________________________________________________B.Modify.General
        if modify is not None and numchecked==1 :
            modlink=1
            leftsize=6

            if oder>0:
                modata=Accounts.query.get(oder)
                err.append(f'Modify {modata.Name}:{modata.Co}:{modata.Type}')

                if hasinput(modata.Type):
                    fmap = Focusareas.query.filter(Focusareas.Co == modata.Co).all()
                    gmap = Taxmap.query.filter(Taxmap.Category.contains('deductions')).all()
                    tmap = get_tmap(modata.Type, modata.Category)
                    qmap = get_qmap(modata.Type, modata.Category)

        if modify is not None and numchecked!=1:
            modlink=0
            err.append('Must check exactly one box to use this option')
# ____________________________________________________________________________________________________________________E.Modify.General

# ____________________________________________________________________________________________________________________B.Delete.General
        if deletehit is not None and numchecked==1:
            if oder>0:
                #This section is to determine if we can delete the source file along with the data.  If other data is pointing to this
                #file then we need to keep it.
                modata=Accounts.query.get(oder)

                Accounts.query.filter(Accounts.id == oder).delete()
                db.session.commit()
                if companyon == 'Show All Accounts':
                    odata = Accounts.query.all()
                elif companyon == 'Show Shared Accounts':
                    divdata = Divisions.query.all()
                    tester = ''
                    for div in divdata:
                        tester = tester + div.Co
                    odata = Accounts.query.filter(Accounts.Co.like(tester)).all()

                else:
                    odata = Accounts.query.filter((Accounts.Co.contains(companyon))).all()

        if deletehit is not None and numchecked != 1:
            err.append('Must have exactly one item checked to use this option')
# ____________________________________________________________________________________________________________________E.Delete.General

# ____________________________________________________________________________________________________________________B.Newjob.General
        if newact is not None:
            modlink=10
            leftsize=6
            modata=Accounts.query.get(1)
            if modata is not None:
                modata.Name=''
                modata.Type=None
                modata.Category=None
                modata.Subcategory=None
                modata.AcctNumber=''
                modata.Routing=''
                modata.Payee=''
                modata.Description=''
                modata.Taxrollup=None
                modata.Co=None
                modata.QBmap = None


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
            qbmap = request.values.get('qbmap')

            acctname = stripper(acctname)
            adat = Accounts.query.filter(Accounts.Name==acctname).first()
            if adat is not None:
                err.append(f'Account with name {acctname} already exists')
            else:
                input = Accounts(Name=acctname,Balance=0.00,AcctNumber=acctnumb,Routing=acctrout,Payee=acctpaye,Type=accttype,
                                 Description=acctdesc,Category=acctcat,Subcategory=acctsub,Taxrollup=accttax,Co=acctco,QBmap=qbmap, Shared=None)
                db.session.add(input)
                db.session.commit()

                # Narrow the selection boxes for company and type
                if hasinput(accttype):
                    print('acctco',acctco)
                    fmap = Focusareas.query.filter(Focusareas.Co == acctco).all()
                    gmap = Taxmap.query.filter(Taxmap.Category.contains('deductions')).all()
                    tmap = get_tmap(accttype, 0)
                    qmap = get_qmap(accttype, 0)

                odata = Accounts.query.all()
                modata = odata[-1]
                oder=modata.id
                modlink=1

# ____________________________________________________________________________________________________________________E.Newjob.General

    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero, erud
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
        tmap = None
        fmap = None
        qmap = None
        gmap = None
        err = []

    scdata=[]
    for odat in odata:
        catitem=odat.Category
        additem=odat.Subcategory
        if additem is not None and catitem is not None:
            if catitem=='G-A' and additem not in scdata:
                scdata.append(additem)
    scdata.sort()
    leftsize = 8
    divdata = Divisions.query.all()
    colordict = {}
    for div in divdata:
        colordict.update({div.Co:div.Color})
    print(colordict)
    err = erud(err)
    atypes = Accttypes.query.all()


    return odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,scdata,companyon,divdata,atypes,tmap,fmap,qmap, gmap, colordict
