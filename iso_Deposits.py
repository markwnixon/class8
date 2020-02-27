from runmain import db
from models import Deposits, Accounts, users, JO, Gledger, People
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

def dataget_Dep(thismuch):
    # 0=order,#1=proofs,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    if thismuch == '1':
        odata = Deposits.query.all()
    elif thismuch == '2':
        stopdate = today-datetime.timedelta(days=45)
        odata = Deposits.query.filter(Deposits.Date > stopdate).all()
    elif thismuch == '3':
        stopdate = today-datetime.timedelta(days=60)
        odata = Deposits.query.filter(Deposits.Date > stopdate).all()
    else:
        odata = Deposits.query.all()
    return odata


def undeposited(thismuch):
    gdata = Gledger.query.filter((Gledger.Type == 'ID') & (Gledger.Reconciled == 0)).all()
    return gdata

def isoDeposit():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef, erud, hasinput
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec, numcheckv, d2s

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
        depdate = request.values.get('depdate')
        print(depdate,hasinput(depdate))
        if not hasinput(depdate): depdate = datetime.datetime.today().strftime('%Y-%m-%d')
        depdata = [acdeposit,cofor,depojo,depdate]
        print(depdata)

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=10

        match    =  request.values.get('Match')
        modify   =  request.values.get('Qmod')
        vmod   =  request.values.get('Vmod')
        viewo     =  request.values.get('View')
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
        err=[]

        if returnhit is not None:
            modlink=0
            depojo=0
            depdata=[0,0,0,depdate]


# ____________________________________________________________________________________________________________________E.FormVariables.General
# ____________________________________________________________________________________________________________________B.DataUpdates.General

# ____________________________________________________________________________________________________________________B.GetData.General
        odata = dataget_Dep(thismuch)
        gdata = undeposited(thismuch)
# ____________________________________________________________________________________________________________________B.Search.General

        if modlink==0:
            oder,numchecked=numcheck(1,gdata,0,0,0,0,['oder'])

# ____________________________________________________________________________________________________________________E.Search.General

        acctsel = request.values.get('actype')
        if acctsel is not None and not hasinput(depojo):
            print(f'Getting depojo acctsel {acctsel}')
            cofor = 0
            if oder > 0:
                inc = Gledger.query.get(oder)
                jo = inc.Tcode
                cofor = jo[0]+'D'
            else:
                acdat = Accounts.query.filter(Accounts.Name==acctsel).first()
                if acdat is not None:
                    cofor=acdat.Co + 'D'
            if cofor != 0:
                todayyf = datetime.datetime.today().strftime('%Y-%m-%d')
                depojo = newjo(cofor, todayyf)
                depdata = [acctsel,cofor,depojo,depdate]

# ____________________________________________________________________________________________________________________E.Delete.General
        if (depositmake is not None or recdeposit is not None) and depojo is not None:
            err.append('Must have exactly one item checked to use this option')

            odervec = numcheckv(gdata)
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
                    depojo = request.values.get('depojo')
                    sourcelist=[]
                    total = 0.00
                    for oder in odervec:
                        idat=Gledger.query.get(oder)
                        amount = float(idat.Debit) / 100.
                        total = total + amount

                    for oder in odervec:
                        idat = Gledger.query.get(oder)
                        fromco = idat.Source
                        amount = d2s(float(idat.Debit)/100.)
                        sid = idat.Sid
                        jo = idat.Tcode
                        ref = idat.Ref

                        if fromco is None:
                            cdat = People.query.get(idat.Sid)
                            if cdat is not None:
                                fromco = cdat.Company
                            else: fromco = 'Unknown Source'
                        if fromco not in sourcelist: sourcelist.append(fromco)

                        acct = idat.Account
                        bank = request.values.get('acdeposit')
                        date2 = request.values.get('depdate')
                        ddat = Deposits.query.filter(Deposits.Jo == idat.Tcode  ).first()
                        if ddat is None:
                            input = Deposits(Jo=jo,Account=acct,Pid=sid,Amount=amount,Total=d2s(total),Ref=ref,Date=date2,Original=os.path.basename(docref),From=fromco,Bank=bank,Date2=today,Depositnum=depojo)
                            db.session.add(input)
                            db.session.commit()
                        else:
                            ddat.Depositnum = depojo
                            ddat.Bank = bank
                            ddat.Date2 = date2
                            ddat.From = fromco
                            ddat.Original = os.path.basename(docref)
                            db.session.commit()

                    print('Here',depojo,acctsel)
                    if len(sourcelist)==1:
                        sendsource = sourcelist[0]
                    else:
                        sendsource = json.dumps(sourcelist)
                        if len(sendsource)>49:
                            sendsource = 'Multiple Sources'

                    from gledger_write import gledger_write
                    gledger_write('deposit',depojo,acctsel,sendsource)

                else:
                    print(odervec)
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
                filename = modata.Depositnum
                docref = f'tmp/{scac}/data/vdeposits/' + filename + '.pdf'
                leftscreen = 0



        if unrecord is not None and numchecked!=1:
            modlink=0
            err.append('Must check exactly one box to use this option')



        if cache is not None:
            #Save the current cache so we do not start from bad place in future
            udat=users.query.filter(users.name=='cache').first()
            udat.username=str(cache)
            udat.email=oderstring
            db.session.commit()

    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero,erud
        today = datetime.date.today()
        today_str = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder=0
        modata=0
        modlink=0
        leftscreen=1
        leftsize=10
        docref=''
        err=['Ready to make and review account deposits']
        thismuch = '2'
        udat=users.query.filter(users.name=='Cache').first()
        cache=udat.username
        cache=nonone(cache)
        depdata = [0,0,0,today_str]
        gdata = undeposited(thismuch)
        odata = dataget_Dep(thismuch)

    leftsize = 8
    acdata = Accounts.query.filter(Accounts.Type=='Bank').all()
    err = erud(err)


    return odata, gdata, oder,err,modata,modlink,leftscreen,leftsize,today,now,docref,cache,acdata,thismuch,depdata
