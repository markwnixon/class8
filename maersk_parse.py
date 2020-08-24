from runmain import db
from models import Vehicles, Invoices, JO, Income, Orders, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Services, Drops
from flask import render_template, flash, redirect, url_for, session, logging, request

import numpy as np
import subprocess
import fnmatch
import os
import json
import shutil
from collections import Counter
import datetime
import re
from CCC_system_setup import addpath, addpath2

def maerskparser():

    #Move all files in the originals_bin/pdf to the processing/pdf_bin
    s=addpath('originals_bin/pdf/maersk/')
    t=addpath('processing/pdf_bin/')
    u=addpath('originals_processed/pdf')
    for file in os.listdir(s):
        if fnmatch.fnmatch(file, '*.pdf'):
            shutil.copy(s+file,u)
            shutil.move(s+file,t+file)

    wk=addpath('processing/tmp/')
    data=addpath('processing/pdf_bin/')
    viewloc=addpath('tmp/data/vbookings/')

    hitems=['booking:Booking', 'reference:ExportRef', 'vessel:Vessel', 'cy/cy:LoadPort', 'total:Amount']

    date_y4=re.compile(r'\d{4}[-](?:0[1-9]|1[012])[-](?:0[1-9]|[12][0-9]|3[01])')
    date_y42=re.compile(r'(?:0[1-9]|1[012])[-](?:0[1-9]|[12][0-9]|3[01])[-]\d{4}')
    amount_p = re.compile(r'(?:[0-9]|[0-9]{2}|[0-9]{3}|[1-9],[0-9]{3}|[0-9]{4})\.[0-9]{2}')

    dictdata = []
    fcount=0
    for file2 in os.listdir(data):
        if fnmatch.fnmatch(file2, '*.pdf'):
            fcount=fcount+1
            base=os.path.splitext(file2)[0]
            base=base.replace('-', '')
            base=base.replace(' ', '')
            file1=file2.replace('-','')
            file1=file1.replace(' ','')
            #shutil.copy(data+file2,viewloc+file1)


            #print (subprocess.check_output(['pdf2txt.py', '-o', done+base+'.txt', wk+file2]))
            tj=subprocess.check_output(['pdf2txt.py', '-o', wk+base+'.txt', data+file2])
            mysetlist={'Jo':'NAY'}
            mysetlist.update({'Booking':''})
            mysetlist.update({'ExportRef':''})
            mysetlist.update({'Vessel': ''})
            mysetlist.update({'Line': 'Maersk'})
            mysetlist.update({'PortCut': ''})
            mysetlist.update({'DocCut': ''})
            mysetlist.update({'SailDate': ''})
            mysetlist.update({'EstArr': ''})
            mysetlist.update({'AES': 'NAY'})
            mysetlist.update({'Original': file1})
            mysetlist.update({'Amount': ''})
            mysetlist.update({'LoadPort': ''})
            mysetlist.update({'Dest': ''})
            mysetlist.update({'Status': 'Unmatched'})
            datecut=None
            datesail=None
            datearr=None

            with open(wk+base+'.txt') as openfile:
                for line in openfile:
                    if 'latest' in line.lower():
                        datep=date_y42.findall(line)
                        if datep:
                            datecut=datetime.datetime.strptime(datep[0], '%m-%d-%Y').strftime('%Y/%m/%d')
                    if 'etd' in line.lower():
                        testline=line+next(openfile)
                        datep=date_y4.findall(testline)
                        if datep:
                            datesail=datetime.datetime.strptime(datep[0], '%Y-%m-%d').strftime('%Y/%m/%d')
                    if 'eta' in line.lower():
                        testline=line+next(openfile)
                        datep=date_y4.findall(testline)
                        if datep:
                            datearr=datetime.datetime.strptime(datep[0], '%Y-%m-%d').strftime('%Y/%m/%d')

            mysetlist.update({'PortCut': datecut})
            mysetlist.update({'DocCut': datecut})
            mysetlist.update({'SailDate': datesail})
            mysetlist.update({'EstArr': datearr})

            for item in hitems:
                list=[]
                label = item.split(':',1)[1]
                item  = item.split(':',1)[0]

                with open(wk+base+'.txt') as openfile:
                    for line in openfile:
                        if item.lower() in line.lower():
                            if(item in 'vesselcy/cy'):
                                line=line+next(openfile)
                            rest=line.lower().split(item.lower(),1)[1]
                            rest=line[-len(rest):]
                            if ':' in rest:
                                rest=rest.split(':',1)[1]
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
                            phrase=phrase.strip()

                            if item in 'booking':
                                if len(phrase)>0:
                                    nratio=len(re.sub("\D","",phrase))/len(phrase)
                                    if nratio > .6:
                                        list.append(phrase)
                            elif item in 'vessel':
                                if 'MAERSK' in phrase:
                                    if len(phrase)>50:
                                        phrase=phrase[0:49]
                                    list.append(phrase)
                            elif item in 'cy/cy':
                                list.append(phrase)
                                nextphrase=next(openfile).strip()
                                mysetlist.update({'Dest' : nextphrase})

                            else:
                                if len(phrase)>25:
                                    phrase=phrase[0:24]
                                list.append(phrase)


                if len(list)>0:
                    best=max(list,key=list.count)
                else:
                    best=''
                mysetlist.update({label : best})

            longs = open(wk+base+'.txt').read()
            amount=amount_p.findall(longs)
            if amount:
                amount = [w.replace('$','') for w in amount]
                amount = [w.replace(',','') for w in amount]
                #amt=[float(i) for i in amount]
                #newamount="{:.2f}".format(max(amt))
                mysetlist.update({'Amount': amount[0]})

            print(mysetlist)
            dictdata.append(mysetlist)

            shutil.move(data+file2,viewloc+file1)

    if dictdata:
        for index in range(len(dictdata)):
            obj=dictdata[index]
            Booking=obj.get("Booking")
            #Convert all dates to Database Storage format:
            portcut=obj.get("PortCut")
            doccut=obj.get("DocCut")
            saildate=obj.get("SailDate")
            estarr=obj.get("EstArr")
            if portcut is not None:
                portcut=datetime.datetime.strptime(portcut, '%Y/%m/%d')
            if doccut is not None:
                doccut=datetime.datetime.strptime(doccut, '%Y/%m/%d')
            if saildate is not None:
                saildate=datetime.datetime.strptime(saildate, '%Y/%m/%d')
            if estarr is not None:
                estarr=datetime.datetime.strptime(estarr, '%Y/%m/%d')

            bdata = Bookings.query.filter(Bookings.Booking == Booking).first()
            if bdata is None:
                input = Bookings(Jo=None, Booking=Booking, ExportRef=obj.get("ExportRef"), Line=obj.get("Line"),
                                 Vessel=obj.get("Vessel"), PortCut=portcut, DocCut=doccut, SailDate=saildate, EstArr=estarr,
                                 RelType=None, AES=None, Original=obj.get("Original"), Amount=obj.get("Amount"),
                                 LoadPort=obj.get("LoadPort"), Dest=obj.get("Dest"), Status="Unmatched")

                print ('Data part ', index+1, ' of ', len(dictdata), 'is being added to database: Bookings')
                db.session.add(input)
            else:
            # The data already exists for the Booking.  Update select parameters inside it.
                if bdata.Status != "Locked":
                    bdata.ExportRef=obj.get("ExportRef")
                    bdata.Line=obj.get("Line")
                    bdata.Vessel=obj.get("Vessel")
                    bdata.PortCut=portcut
                    bdata.DocCut=doccut
                    bdata.SailDate=saildate
                    bdata.EstArr=estarr
                    bdata.Original=obj.get("Original")
                    bdata.Amount=obj.get("Amount")
                    bdata.LoadPort=obj.get("LoadPort")
                    bdata.Dest=obj.get("Dest")

            db.session.commit()

    print('Total # pdf files found: ', fcount)
