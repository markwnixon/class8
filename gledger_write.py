from runmain import db
from models import Gledger, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, People, Interchange, Drivers, ChalkBoard, Services, Drops
import datetime

def gledger_app_write(sapp,jo,cofor,id1,id2,amt):
    dt = datetime.datetime.now()
    bdat = Bills.query.filter(Bills.Jo == jo).first()
    co = bdat.Company
    pid = bdat.Pid
    if sapp == 'app1':
        ad = 'AD'
        ac = 'AC'
    elif sapp == 'app2':
        ad = 'BD'
        ac = 'BC'

    adb = Accounts.query.get(id1)
    acr = Accounts.query.get(id2)
    acctdb = adb.Name
    acctcr = acr.Name
    amt = int(float(amt) * 100)

    gdat = Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == ad)).first()
    if gdat is not None:
        gdat.Debit = amt
        gdat.Recorded = dt
    else:
        input1 = Gledger(Debit=amt, Credit=0, Account=acctdb, Aid=adb.id, Source=co, Sid=pid, Type=ad, Tcode=jo,
                         Com=cofor, Recorded=dt, Reconciled=0)
        db.session.add(input1)
    db.session.commit()

    gdat = Gledger.query.filter((Gledger.Tcode == jo) & (Gledger.Type == ac)).first()
    if gdat is not None:
        gdat.Credit = amt
        gdat.Recorded = dt
    else:
        input2 = Gledger(Debit=0, Credit=amt, Account=acctcr, Aid=acr.id, Source=co, Sid=pid, Type=ac, Tcode=jo,
                         Com=cofor, Recorded=dt, Reconciled=0)
        db.session.add(input2)
    db.session.commit()


def gledger_write(bus,jo,acctdb,acctcr):
    if 1 == 1:
        dt = datetime.datetime.now()
        cc=jo[0] # this is the company we will be working on
        if bus=='invoice':
            acctdb='Accounts Receivable'
            acctcr='Revenues'
            idat=Invoices.query.filter(Invoices.Jo==jo).first()
            amt=int(float(idat.Total)*100)
            pid=idat.Pid
            cdat=People.query.get(pid)
            co=cdat.Company

            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first()
            acr=Accounts.query.filter((Accounts.Name==acctcr) & (Accounts.Co ==cc)).first()

            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='VD')).first()
            if gdat is not None:
                gdat.Debit=amt
                gdat.Recorded=dt
            else:
                input1 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=co,Sid=pid,Type='VD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input1)
            db.session.commit()
            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='VC')).first()
            if gdat is not None:
                gdat.Credit=amt
                gdat.Recorded=dt
            else:
                input2 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=co,Sid=pid,Type='VC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input2)
            db.session.commit()

        if bus=='income':

            if 'Cash' in acctdb or 'Check' in acctdb or 'Mcheck' in acctdb or 'Undeposited' in acctdb:
                acctdb='Cash'
                dtype = 'ID'
            else:
                dtype = 'DD'
                # Else we will write directly to the bank account
            acctcr='Accounts Receivable'
            idat=Income.query.filter(Income.Jo==jo).first()
            amt=int(float(idat.Amount)*100)
            pid=idat.Pid
            cdat=People.query.get(pid)
            co=cdat.Company

            print('62 acctdb=', acctdb)

            acr=Accounts.query.filter((Accounts.Name==acctcr) & (Accounts.Co ==cc)).first()
            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first()

            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='IC')).first()
            if gdat is not None:
                gdat.Account=acctcr
                gdat.Credit=amt
                gdat.Recorded=dt
                gdat.Aid=acr.id
            else:
                input1 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=co,Sid=pid,Type='IC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input1)
            db.session.commit()
            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type==dtype)).first()
            if gdat is not None:
                gdat.Account=acctdb
                gdat.Debit=amt
                gdat.Recorded=dt
                gdat.Aid=adb.id
            else:
                input2 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=co,Sid=pid,Type=dtype,Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input2)
            db.session.commit()

        if bus=='deposit':
            idat=JO.query.filter(JO.jo==jo).first()
            amt=int(float(idat.dinc)*100)
            comp=idat.dexp
            cdat=People.query.filter(People.Company==comp).first()
            if cdat is not None:
                pid=cdat.id
            else:
                pid=0

            acr=Accounts.query.filter((Accounts.Name=='Cash') & (Accounts.Co ==cc)).first()
            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first()
            # In this case jo is the deposit ticket code
            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='DC')).first()
            if gdat is not None:
                gdat.Account=acctcr
                gdat.Credit=amt
                gdat.Recorded=dt
                gdat.Aid=acr.id
            else:
                input1 = Gledger(Debit=0,Credit=amt,Account='Cash',Aid=acr.id,Source=comp,Sid=pid,Type='DC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input1)

            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='DD')).first()
            if gdat is not None:
                gdat.Account=acctdb
                gdat.Debit=amt
                gdat.Recorded=dt
                gdat.Aid=adb.id
            else:
                input2 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=comp,Sid=pid,Type='DD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input2)
            db.session.commit()

        print('bus=',bus)
        if bus=='newbill':
            bdat=Bills.query.filter(Bills.Jo==jo).first()
            amt=int(float(bdat.bAmount)*100)
            pid=bdat.Pid
            cdat=People.query.get(pid)
            if cdat is not None:
                co=cdat.Company
            else:
                co = 'Not There'
                print('Problem finding vendor')

            acctcr = 'Accounts Payable'
            print(acctdb,cc)

            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first() #the expense account
            acr=Accounts.query.filter((Accounts.Name==acctcr) & (Accounts.Co ==cc)).first() #the asset account

            gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='ED')).first()
            if gdat is not None:
                gdat.Debit=amt
                gdat.Recorded=dt
            else:
                input1 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=co,Sid=pid,Type='ED',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input1)
            db.session.commit()

            gdat = Gledger.query.filter((Gledger.Tcode==jo) &  (Gledger.Type=='EC')).first()
            if gdat is not None:
                gdat.Credit=amt
                gdat.Recorded=dt
            else:
                input2 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=co,Sid=pid,Type='EC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input2)
            db.session.commit()


        if bus=='paybill':
            bdat=Bills.query.filter(Bills.Jo==jo).first()
            amt=int(float(bdat.bAmount)*100)
            pid=bdat.Pid
            cdat=People.query.get(pid)
            co=cdat.Company
            acctdb = 'Accounts Payable'
            print(acctcr,cc)

            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first() #the expense account
            acr=Accounts.query.filter((Accounts.Name==acctcr) & (Accounts.Co ==cc)).first() #the asset account

            if acr is None:
                #This account must be for another company and we have a cross bill situation
                acr = Accounts.query.filter(Accounts.Name == acctcr).first()
                if acr is not None:
                    acrco = acr.Co
                    if acrco != cc:
                        print('Mismatched Bills')
                        newcc = acr.Co

                adat1 = Accounts.query.filter( (Accounts.Name.contains('Due to')) & (Accounts.Name.contains(cc)) & (Accounts.Co == newcc)).first()
                duetodb = adat1.Name
                duetodbid = adat1.id
                adat2 = Accounts.query.filter( (Accounts.Name.contains('Due to')) & (Accounts.Name.contains(newcc)) & (Accounts.Co == cc)).first()
                duetocr = adat2.Name
                duetocrid = adat2.id

                gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Aid==duetoid) & (Gledger.Type=='PD')).first()
                if gdat is not None:
                    gdat.Debit=amt
                    gdat.Recorded=dt
                else:
                    input1 = Gledger(Debit=amt,Credit=0,Account=duetodb,Aid=duetodbid,Source=co,Sid=pid,Type='PD',Tcode=jo,Com=newcc,Recorded=dt,Reconciled=0)
                    db.session.add(input1)
                db.session.commit()
                gdat = Gledger.query.filter((Gledger.Tcode==jo) &  (Gledger.Type=='PC')).first()
                if gdat is not None:
                    gdat.Credit=amt
                    gdat.Recorded=dt
                else:
                    input2 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=co,Sid=pid,Type='PC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                    db.session.add(input2)
                db.session.commit()

                gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Aid==adb.id) & (Gledger.Type=='QD')).first()
                if gdat is not None:
                    gdat.Debit=amt
                    gdat.Recorded=dt
                else:
                    input1 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=co,Sid=pid,Type='QD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                    db.session.add(input1)
                db.session.commit()
                gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Type=='QC')).first()
                if gdat is not None:
                    gdat.Credit=amt
                    gdat.Recorded=dt
                else:
                    input2 = Gledger(Debit=0,Credit=amt,Account=duetocr,Aid=duetocrid,Source=co,Sid=pid,Type='QC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                    db.session.add(input2)
                db.session.commit()



            else:



                gdat = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Aid==adb.id) & (Gledger.Type=='PD')).first()
                if gdat is not None:
                    gdat.Debit=amt
                    gdat.Recorded=dt
                else:
                    input1 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=co,Sid=pid,Type='PD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                    db.session.add(input1)
                db.session.commit()
                gdat = Gledger.query.filter((Gledger.Tcode==jo) &  (Gledger.Type=='PC')).first()
                if gdat is not None:
                    gdat.Credit=amt
                    gdat.Recorded=dt
                else:
                    input2 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=co,Sid=pid,Type='PC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                    db.session.add(input2)
                db.session.commit()

        if bus=='xfer':
            bdat=Bills.query.filter(Bills.Jo==jo).first()
            amt=int(float(bdat.bAmount)*100)

            adb=Accounts.query.filter((Accounts.Name==acctdb)).first() #the expense account
            acr=Accounts.query.filter((Accounts.Name==acctcr)).first() #the asset account

            #if (adb.Type=='Asset' or adb.Type=='Bank') and (acr.Type=='Asset' or acr.Type=='Bank'):

            gdat1 = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Aid==adb.id) & (Gledger.Type=='XD')).first()
            gdat2 = Gledger.query.filter((Gledger.Tcode==jo) & (Gledger.Aid==acr.id) & (Gledger.Type=='XC')).first()
            if gdat1 is not None:
                gdat1.Debit=amt
                gdat1.Recorded=dt
            else:
                input1 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=acctcr,Sid=acr.id,Type='XD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input1)
            db.session.commit()

            if gdat2 is not None:
                gdat2.Credit=amt
                gdat2.Recorded=dt
            else:
                input2 = Gledger(Debit=0,Credit=amt,Account=acctcr,Aid=acr.id,Source=acctdb,Sid=adb.id,Type='XC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
                db.session.add(input2)
            db.session.commit()
