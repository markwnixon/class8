from felrun import db
from models import Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Orders, Drops
from flask import session, logging, request
import numpy as np
import subprocess
import fnmatch
import os
import json
import shutil
from collections import Counter
import datetime
import re

def hoeghparse():

    #Move all files in the originals_bin/pdf to the processing/pdf_bin
    s='originals_bin/pdf/hoegh/'
    t='processing/pdf_bin/'
    u='originals_processed/pdf'
    for file in os.listdir(s):
        if fnmatch.fnmatch(file, '*.pdf'):
            shutil.copy(s+file,u)
            shutil.move(s+file,t+file)

    wk='processing/static/'
    data='processing/pdf_bin/'
    viewloc='static/data/vbookings/'

    hitems=['booking:Booking', 'reference:ExportRef', 'vessel:Vessel', 'loading:LoadPort',
            'discharge:Dest', 'total:Amount']

    date_p5=re.compile(r'\d{1,2}-(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-\d{4}')
    amount_p = re.compile(r'(?:[0-9]|[0-9]{2}|[0-9]{3}|[1-9],[0-9]{3}|[0-9]{4})\.[0-9]{2}')
    date_y4=re.compile(r'\d{1,2}[/]\d{1,2}[/]\d{4}')

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
            shutil.copy(data+file2,viewloc+file1)

            #print (subprocess.check_output(['pdf2txt.py', '-o', done+base+'.txt', wk+file2]))
           # tj=subprocess.check_output(['pdf2txt.py', '-o', wk+base+'.txt', data+file2])
            # The pdf file from Troy loses its keywork proximity, so have to convert to image and OCR to preserve locations
            chgpdf=subprocess.check_output(['convert', '-trim', '-density', '300', data+file2, '-depth', '8', '-strip', '-background',
                                                'white', '-alpha', 'off', wk+'test.tiff'])
            tout=subprocess.check_output(['tesseract', wk+'test.tiff' , wk+base,'quiet'])
            mysetlist={'Jo':'NAY'}
            mysetlist.update({'Booking':''})
            mysetlist.update({'ExportRef':''})
            mysetlist.update({'Vessel': ''})
            mysetlist.update({'Line': 'Hoegh'})
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
                    if 'docs cut' in line.lower():
                        datep=date_y4.findall(line)
                        if datep:
                            datecut=datetime.datetime.strptime(datep[0], '%m/%d/%Y').strftime('%Y/%m/%d')
                    if 'etd' in line.lower():
                        datep=date_y4.findall(line)
                        if datep:
                            datesail=datetime.datetime.strptime(datep[0], '%m/%d/%Y').strftime('%Y/%m/%d')
                    if 'eta' in line.lower():
                        datep=date_y4.findall(line)
                        if datep:
                            datearr=datetime.datetime.strptime(datep[0], '%m/%d/%Y').strftime('%Y/%m/%d')

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
                            rest=line.lower().split(item.lower(),1)[1]
                            rest=line[-len(rest):]
                            if ':' in rest:
                                rest=rest.split(':',1)[1]
                            else:
                                rest=''

                            rest=rest.replace('#', '')
                            rest=rest.replace(':', '')
                            rest=rest.replace('-', '')
                            rest=rest.strip()
                            #Could have multiple space inside words which we do not want to store in database:
                            pieces=rest.split()
                            print(item,pieces)

                            if pieces and item == 'booking':
                                phrase=pieces[0]
                            elif pieces and item == 'loading':
                                phrase=pieces[0]
                            elif pieces and item == 'discharge':
                                phrase=pieces[0]+' '+pieces[1]
                            elif pieces and item == 'vessel':
                                if len(pieces)>1:
                                    phrase=pieces[0]+' '+pieces[1]
                            else:
                                phrase=''
                                for piece in pieces:
                                    piece=piece.strip()
                                    phrase=phrase+piece
                                phrase=phrase.strip()

                            if len(phrase)>3:
                                if len(phrase)>25:
                                    phrase=phrase[0:24]
                                print(item,phrase)
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
            os.remove(data+file2)

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
    return
