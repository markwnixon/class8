from runmain import db
from models import Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Orders, Drops
from flask import session, logging, request
from viewfuncs import newjo,dropupdate
import datetime
import calendar
import re
import os
import numpy as np
import subprocess
import fnmatch
import json
import shutil
from collections import Counter
from CCC_system_setup import addpath, addpath2

def huntparse():
    s=addpath('originals_bin/pdf/hunt/')
    t=addpath('processing/pdf_bin/hunt/')
    u=addpath('originals_processed/pdf')
    for file in os.listdir(s):
        if fnmatch.fnmatch(file, '*.pdf'):
            shutil.copy(s+file,u)
            shutil.move(s+file,t+file)

    data=addpath('processing/pdf_bin/hunt')
    done=addpath('processing/pdforder/')
    viewloc=addpath('tmp/data/vorders/')

    #Using new format here the left item is what we are looking for (keyword) and right side is the Label
    hitems=['Total Rate:Amount', 'Commodity:commodity']

    # These items we look to see if there are load and delivery points to add to database
    vadditems=['Pickup', 'Shipper', 'Consignee', 'Delivery']

    today = datetime.datetime.today()
    todaydate = today.date()
    todaynow = today.time()
    todaystr = datetime.datetime.today().strftime('%Y-%m-%d')
    year= str(today.year)
    day=str(today.day)
    month=str(today.month)
    #print(month,day,year)
    datestr='label:'+month+'/'+day+'/'+year

    pyr=year[2]+year[3]
    date_p1=re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\s?\d{1,2},?\s?\d{4}')
    date_y2=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2}')
    date_y4=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}')
    date_p3=re.compile(r'\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{4}')
    date_p4=re.compile(r'\s'+pyr+'(?:0[1-9]|1[012])(?:0[1-9]|[12][0-9]|3[01])')
    time_p24=re.compile(r'(?:[1-9]|0[0-9]|1[0-9]|2[01234])[:](?:0[0-9]|[12345][0-9])')
    container_p = re.compile(r'[A-Z,a-z]{4}\s?[Ool0123456789]{7}')
    amount_p = re.compile(r'\$(?:[0-9]|[0-9]{2}|[0-9]{3}|[1-9],[0-9]{3})\.[0-9]{2}')

    fcount=0
    for file2 in os.listdir(addpath('processing/pdf_bin/hunt')):
        if fnmatch.fnmatch(file2, '*.pdf'):
            fcount=fcount+1
            base=os.path.splitext(file2)[0]
            #print(base)
            load=base.replace('Tender_','')
            print('Load=',load)
            if not load:
                load='000000'
            #print(file2,base,load)

            print ('Running file: ',file2)
            print (subprocess.check_output(['pdf2txt.py', '-o', done+load+'.txt', addpath('processing/pdf_bin/hunt/'+file2)]))

            #See if the order exists already:
            o=Orders.query.filter(Orders.Original==file2).first()
            if o is None:
                jtype='T'
                nextjo=newjo(jtype,todaystr)
                #add some default values here for database:
                input = Orders(Status='A0', Jo=nextjo, Load=load,Order=load, Company=None,Location=None,Booking=None,BOL=None,Container=None,
                               Date=None,Driver=None,Company2=None, Time=None, Date2=None, Time2=None, Seal=None, Pickup=None, Delivery=None,
                               Amount=None, Path=None, Original=file2, Description='Load Broker Line Haul', Chassis=None, Detention='0', Storage='0',
                               Release=0, Shipper='JB Hunt', Type=None, Time3=None, Bid=0, Lid=0, Did=0, Label=None, Dropblock1=None,Dropblock2=None,
                               Commodity=None, Packing=None, Links=None, Hstat=-1,
                               Istat=-1, Proof=None, Invoice=None, Gate=None, Package=None, Manifest=None, Scache=0,
                               Pcache=0, Icache=0, Mcache=0, Pkcache=0, QBi=0
                               )
                db.session.add(input)
                db.session.commit()
                o=Orders.query.filter(Orders.Jo==nextjo).first()

            # Find and add load and delivery points to database
            for j,item in enumerate(vadditems):
                with open(done+load+'.txt') as openfile:
                    for line in openfile:
                        if len(line)>3:
                            linelist=line.split()
                            word1=linelist[0]
                            if item == word1:
                                line1=line
                                line2=next(openfile)
                                line3=next(openfile)
                                line4=next(openfile)
                                line5=next(openfile)


                                if j==0:
                                    pickupdate=line2
                                    print('pickupdate',pickupdate)
                                    linelist2=line2.split()
                                    print('DATE',linelist2[0],flush=True)
                                    try:
                                        date1 = datetime.datetime.strptime(linelist2[0], '%Y-%m-%d')
                                    except:
                                        print('Could not convert:',date1,flush=True)
                                        date1 = todaydate
                                    try:
                                        time1 = datetime.datetime.strptime(linelist2[1], '%H:%M').time()
                                    except:
                                        time1 = todaynow
                                    o.Date=date1
                                    o.Time=time1
                                    db.session.commit()

                                if j==1:
                                    shipperlines=line2+line3+line4+line5
                                    print('shipperlines: ',shipperlines)
                                    o.Dropblock1=shipperlines
                                    company=dropupdate(shipperlines)
                                    addr1=line3.strip()
                                    cdat=Drops.query.filter((Drops.Entity==company) & (Drops.Addr1==addr1)).first()
                                    if cdat is not None:
                                        lid=cdat.id
                                    else:
                                        lid=0
                                    o.Company=company
                                    o.Lid=lid
                                    db.session.commit()

                                if j==2:
                                    consigneelines=line2+line3+line4+line5
                                    print('consigneelines: ',consigneelines)
                                    o.Dropblock2=consigneelines
                                    company2=dropupdate(consigneelines)
                                    addr1=line3.strip()
                                    cdat=Drops.query.filter((Drops.Entity==company2) & (Drops.Addr1==addr1)).first()
                                    if cdat is not None:
                                        did=cdat.id
                                    else:
                                        did=0
                                    o.Company2=company2
                                    o.Did=did
                                    db.session.commit()

                                if j==3:
                                    deliverydate=line2
                                    print('deliverydate',deliverydate)
                                    linelist2=line2.split()
                                    #print('DATE',linelist2[0])
                                    date2 = datetime.datetime.strptime(linelist2[0], '%Y-%m-%d')
                                    print(date1)
                                    time2 = datetime.datetime.strptime(linelist2[1], '%H:%M').time()
                                    o.Date2=date2
                                    o.Time2=time2
                                    db.session.commit()




            for item in hitems:
                list=[]
                label = item.split(':',1)[1]
                item  = item.split(':',1)[0]
                with open(done+load+'.txt') as openfile:
                    for line in openfile:
                        if item.lower() in line.lower():
                            rest=line.lower().split(item.lower(),1)[1]
                            rest=line[-len(rest):]

                            if ':' in rest:
                                rest=rest.split(':',1)[1]
                            elif '#' in rest:
                                rest=rest.split('#',1)[1]
                            elif 'NUMBER' in rest:
                                rest=rest.split('NUMBER',1)[1]


                            rest=rest.replace('#', '')
                            rest=rest.replace(':', '')
                            rest=rest.replace('-', '')
                            rest=rest.strip()

                            #Could have multiple space inside words which we do not want to store in database:
                            pieces=rest.split()
                            phrase=''
                            for piece in pieces:
                                piece=piece.strip()
                                phrase=phrase + ' ' + piece
                            rest=phrase.strip()

                            #print('item=',item,'rest=',rest,'line=',line)

                            lofrest=len(rest)
                            if lofrest > 0:
                                numbers = sum(c.isdigit() for c in rest)
                                keyratio = float(numbers)/float(lofrest)
                            else:
                                keyratio = 0.0

                            if keyratio > .4:
                                list.append(rest)
                if len(list)>0:
                        best=max(list,key=list.count)
                else:
                    best=None

                if label=='Amount':
                    o.Amount=best
                    db.session.commit()

                if label=='commodity':
                    o.Location=best
                    db.session.commit()

                pdat=People.query.filter(People.Company=='JB Hunt').first()
                if pdat is not None:
                    bid=pdat.id
                else:
                    bid=0
                book='JBHunt '+load
                o.Booking=book
                o.Bid=bid
                o.Type='53 Dry Van'
                db.session.commit()


            os.rename(addpath('processing/pdf_bin/hunt/')+file2,viewloc+file2)
            print('File ',fcount)
    return
