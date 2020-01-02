from runmain import db
from models import Gledger, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, People, Interchange, Drivers, ChalkBoard, Proofs, Services, Drops
from flask import render_template, flash, redirect, url_for, session, logging, request
from InterchangeFuncs import Order_Container_Update, Matched_Now
from iso_InvM import updateinvo

import math
from decimal import Decimal
import datetime
import calendar
import os
import subprocess
import shutil
import re
from func_cal import calmodalupdate
from PyPDF2 import PdfFileReader

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
            input1 = Gledger(Debit=0,Credit=amt,Account='Cash',Aid=acr.id,Source=comp,Sid=pid,Type='DC',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
            input2 = Gledger(Debit=amt,Credit=0,Account=acctdb,Aid=adb.id,Source=comp,Sid=pid,Type='DD',Tcode=jo,Com=cc,Recorded=dt,Reconciled=0)
            db.session.add(input1)
            db.session.add(input2)
            db.session.commit()

        if bus=='newbill':
            bdat=Bills.query.filter(Bills.Jo==jo).first()
            amt=int(float(bdat.bAmount)*100)
            pid=bdat.Pid
            cdat=People.query.get(pid)
            co=cdat.Company
            acctcr = 'Accounts Payable'
            print(acctdb,cc)

            adb=Accounts.query.filter((Accounts.Name==acctdb) & (Accounts.Co ==cc)).first() #the expense account
            acr=Accounts.query.filter((Accounts.Name==acctcr) & (Accounts.Co ==cc)).first() #the asset account

            gdat = Gledger.query.filter((Gledger.Tcode==jo) &  (Gledger.Type=='ED')).first()
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

            if (adb.Type=='Asset' or adb.Type=='Bank') and (acr.Type=='Asset' or acr.Type=='Bank'):

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
    if 1 == 2:
        print('Warning could not write to gledger')
