from runmain import db
from models import Income, Accounts, users, JO, Gledger
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import json
import subprocess
from report_maker import reportmaker
from CCC_system_setup import scac

def dataget_Inc(thismuch):
    # 0=order,#1=proofs,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    if thismuch == '1':
        odata = Income.query.filter((Income.SubJo=='Mcheck') | (Income.SubJo=='Cash') | (Income.SubJo=='Mremit')).all()
    elif thismuch == '2':
        stopdate = today-datetime.timedelta(days=45)
        odata = Income.query.filter(Income.Date > stopdate).all()
    elif thismuch == '3':
        stopdate = today-datetime.timedelta(days=60)
        odata = Income.query.filter(Income.Date > stopdate).all()
    else:
        odata = Income.query.all()
    return odata

def isoIncM():

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
        acdeposit = request.values.get('acdeposit')
        if acdeposit is None:
            acdeposit = request.values.get('actype')
        depojo = request.values.get('depojo')
        cofor = request.values.get('cofor')
        depdata = [acdeposit,cofor,depojo]


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
        depositmake = request.values.get('depositmake')
        recdeposit = request.values.get('recdeposit')
        unrecord = request.values.get('unrecord')
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
                modata=Income.query.get(oder)
                vals=['jo','subjo','pid','description','amount','ref','pdate','original']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)

                modata.Jo=a[0]
                modata.SubJo=a[1]
                modata.Pid=a[2]
                modata.Description=a[3]
                modata.Amount=a[4]
                modata.Ref=a[5]
                modata.Date=a[6]
                modata.Original=a[7]
                db.session.commit()
                err[3]= 'Modification to Income id ' + str(modata.id) + ' completed.'
                if update is not None:
                    modlink=0
                    leftsize=10
                else:
                    leftsize=6
                    leftscreen=0
                    modata=Income.query.get(oder)

# ____________________________________________________________________________________________________________________B.GetData.General
        #odata = Income.query.all()
        odata = dataget_Inc(thismuch)
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
                modata=Income.query.get(oder)
                docref=modata.Original

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
                modata=Income.query.get(oder)

                Income.query.filter(Income.id == oder).delete()
                db.session.commit()
                odata = dataget_Inc(thismuch)


        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']


        acctsel = request.values.get('actype')
        if depojo is None or acdeposit != acctsel:
            acdat = Accounts.query.filter(Accounts.Name==acctsel).first()
            if acdat is not None:
                cofor=acdat.Co
                todayyf = datetime.datetime.today().strftime('%Y-%m-%d')
                nextjo = newjo(cofor, todayyf)
                depojo =nextjo.replace('KT','KD').replace('JA','JD')
                jdat=JO.query.filter(JO.jo==nextjo).first()
                jdat.jo=depojo
                depdata = [acctsel,cofor,depojo]
                db.session.commit()

# ____________________________________________________________________________________________________________________E.Delete.General
        if (depositmake is not None or recdeposit is not None) and depojo is not None:
            err=['Must have exactly one item checked to use this option', ' ',  ' ']

            odervec = numcheckv(odata)
            if len(odervec)>0:
                oderstring = json.dumps(odervec)
            else:
                udat=users.query.filter(users.name=='cache').first()
                oderstring = udat.email
                odervec = json.loads(oderstring)

            if odervec is not None:
                cache = request.values.get('cache')
                if cache is None:
                    cache = 2

                if recdeposit is not None:
                    cache,docref=reportmaker('recdeposit',odervec)
                    for oder in odervec:
                        idat=Income.query.get(oder)
                        subjo = idat.SubJo
                        ref = idat.Ref
                        idata = Income.query.filter((Income.SubJo==subjo) & (Income.Ref==ref) ).all()
                        for data in idata:
                            data.SubJo = depojo
                            db.session.commit()


                    from gledger_write import gledger_write
                    gledger_write('deposit',depojo,acctsel,0)

                else:
                    cache,docref=reportmaker('deposit',odervec)

                leftscreen = 0

        if unrecord is not None and numchecked == 1:
            if oder>0:
                modata=Income.query.get(oder)
                subjo = modata.SubJo
                idata = Income.query.filter(Income.SubJo==subjo).all()
                for idat in idata:
                    idat.SubJo = 'Mremit'
                    db.session.commit()
                jdat = JO.query.filter(JO.jo==subjo).first()
                if jdat is not None:
                    jdat.dinc = '0.00'
                    db.session.commit()
                Gledger.query.filter(Gledger.Tcode == subjo).delete()
                db.session.commit()

        if viewo is not None and numchecked == 1:
            if oder>0:
                modata=Income.query.get(oder)
                depojo = modata.SubJo
                docref = f'tmp/{scac}/data/vdeposits/' + depojo + '.pdf'
                leftscreen = 0



        if unrecord is not None and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'



        if cache is not None:
            #Save the current cache so we do not start from bad place in future
            udat=users.query.filter(users.name=='cache').first()
            udat.username=str(cache)
            udat.email=oderstring
            db.session.commit()

    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder=0
        modata=0
        modlink=0
        odata = Income.query.all()
        leftscreen=1
        leftsize=10
        docref=''
        err=['All is well', ' ', ' ', ' ',  ' ']
        thismuch = '2'
        udat=users.query.filter(users.name=='Cache').first()
        cache=udat.username
        cache=nonone(cache)
        depdata = [0,0,0]
        odata = dataget_Inc(thismuch)

    leftsize = 8
    acdata = Accounts.query.filter(Accounts.Type=='Bank').all()


    return odata,oder,err,modata,modlink,leftscreen,leftsize,today,now,docref,cache,acdata,thismuch,depdata
