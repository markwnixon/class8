from runmain import db
from models import Compliance
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import subprocess
import ntpath
from CCC_system_setup import myoslist,addpath,addtxt, scac

def isoC():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.Compliance

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec

        #Zero and blank items for default
        username = session['username'].capitalize()
        cache=0
        modata=0
        modlink=0
        fdata=0
        filesel=''
        docref=''
        doctxt=''
        longs=''


        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=10

        match    =  request.values.get('Match')
        modify   =  request.values.get('Modify')
        vmod     =  request.values.get('Vmod')
        viewo     =  request.values.get('ViewO')
        print    =  request.values.get('Print')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        delfile = request.values.get('DELF')
        # hidden values
        update   =  request.values.get('Update')
        newjob=request.values.get('NewJ')
        thisjob=request.values.get('ThisJob')
        oder=request.values.get('oder')
        modlink = request.values.get('modlink')
        longs=request.values.get(longs)
        searchfind=request.values.get('mastersearch')
        assemble=request.values.get('Assemble')

        oder=nonone(oder)
        modlink=nonone(modlink)
        actype = request.values.get('actype')

        leftscreen=1
        err=['All is well', ' ', ' ', ' ', ' ']

        if returnhit is not None:
            modlink=0
            actype='Choose Compliance Subject'

        if searchfind is not None:
            modlink=20

# ____________________________________________________________________________________________________________________E.FormVariables.Compliance
# ____________________________________________________________________________________________________________________B.DataUpdates.Compliance

        if update is not None and modlink==1:
            if oder > 0:
                modata=Compliance.query.get(oder)
                vals=['subject','category','longs','item','date1','date2']
                a=list(range(len(vals)))
                for i,v in enumerate(vals):
                    a[i]=request.values.get(v)
                datedue=a[4]
                datefiled=a[5]

                if datedue == '':
                    newdate1 = None
                else:
                    newdate1 = datedue

                if datefiled == '':
                    newdate2 = None
                else:
                    newdate2 = datedue

                modata.Subject=a[0]
                modata.Category=a[1]
                modata.Textinfo=a[2]
                modata.Item=a[3]
                modata.Date1=newdate1
                modata.Date2=newdate2

                db.session.commit()
                err[3]= 'Modification to Compliance id ' + str(modata.id) + ' completed.'
                modlink=0



# ____________________________________________________________________________________________________________________B.GetData.Compliance
        if actype == 'Choose Compliance Subject' or actype is None:
            odata = Compliance.query.all()
        else:
            odata = Compliance.query.filter(Compliance.Subject == actype).all()


        if assemble is not None:
            avec=numcheckvec(odata,'oder')
            scommand=['pdfunite']
            if len(avec)>0:
                for a in avec:
                    gdat=Compliance.query.get(a)
                    dot=gdat.File1
                    docref=f'tmp/{scac}/data/vcompliance/' + dot
                    scommand.append(docref)
                scommand.append(f'tmp/{scac}/data/vunknown/assembledoutput.pdf')
                tes=subprocess.check_output(scommand)
# ____________________________________________________________________________________________________________________B.Search.Compliance

        if (newjob is None and modlink<10) or modlink==20:
            oder,numchecked=numcheck(1,odata,0,0,0,0,['oder'])

# ____________________________________________________________________________________________________________________E.Search.Compliance

# ____________________________________________________________________________________________________________________B.Views.Compliance

        if viewo is not None and numchecked==1:
            err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
            if oder>0:
                modata=Compliance.query.get(oder)
                if modata.File1 is not None:
                    dot=modata.File1
                    txt=dot.split('.',1)[0]+'.txt'
                    docref=f'tmp/{scac}/data/vcompliance/' + dot
                    doctxt=docref.replace('.pdf','.txt').replace('.jpg','.txt').replace('.jpeg','.txt')
                    leftscreen=0
                    leftsize=10
                    modlink=0
                    err=[' ', ' ', 'Viewing document '+docref, ' ',  ' ']

        if (viewo is not None) and numchecked!=1:
            err=['Must check exactly one box to use this option', ' ', ' ', ' ',  ' ']

# ____________________________________________________________________________________________________________________E.Views.Compliance
# ____________________________________________________________________________________________________________________B.Modify.Compliance
        if (modify is not None or vmod is not None) and numchecked==1 :
            modlink=1
            leftsize=8

            if oder>0:
                modata=Compliance.query.get(oder)
                if vmod is not None:
                    err=[' ', ' ', 'There is no document available for this selection', ' ',  ' ']
                    if modata.File1 is not None:
                        dot=modata.File1
                        docref=f'tmp/{scac}/data/vcompliance/' + dot
                        doctxt=docref.replace('.pdf','.txt').replace('.jpg','.txt').replace('.jpeg','.txt')


                        leftscreen=0

                        err=['All is well', ' ', ' ', ' ',  ' ']

        if (modify is not None or vmod is not None) and numchecked!=1:
            modlink=0
            err[0]=' '
            err[2]='Must check exactly one box to use this option'
# ____________________________________________________________________________________________________________________E.Modify.Compliance

# ____________________________________________________________________________________________________________________B.Delete.Compliance
        if deletehit is not None and numchecked==1:
            if oder>0:
                #This section is to determine if we can delete the source file along with the data.  If other data is pointing to this
                #file then we need to keep it.
                modata=Compliance.query.get(oder)
                if modata.File1 is not None:
                    dot=modata.File1
                    docref=f'tmp/{scac}/data/vcompliance/' + dot

                othdoc=Compliance.query.filter((Compliance.File1==dot) & (Compliance.File1 != modata.id)).first()
                if othdoc is None:
                    try:
                        os.remove(addpath(docref))
                        os.remove(addtxt(docref))
                    except:
                        err[0]='File already removed'

                Compliance.query.filter(Compliance.id == oder).delete()
                db.session.commit()
                odata = Compliance.query.all()

        if deletehit is not None and numchecked != 1:
            err=[' ', ' ', 'Must have exactly one item checked to use this option', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Delete.Compliance

# ____________________________________________________________________________________________________________________B.Newjob.Compliance
        if newjob is not None:
            err=['Select Source Document from List']
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            modlink=10
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/NewJob.pdf'

        if newjob is None and update is None and modlink==10:
            filesel=request.values.get('FileSel')
            filetxt=filesel.replace('.pdf','.txt').replace('.jpg','.txt').replace('.jpeg','.txt')
            fdata = myoslist(f'tmp/{scac}/data/vunknown')
            fdata.sort()
            leftsize=8
            leftscreen=0
            docref=f'tmp/{scac}/data/vunknown/'+filesel
            doctxt=f'tmp/{scac}/data/vunknown/'+filetxt

            try:
                longs = open(addpath(doctxt)).read()
                longs = longs[0:999]
            except:
                doctxt=''
                longs=''

        if delfile is not None and modlink==10:
            modlink=0
            filesel=request.values.get('FileSel')
            if filesel != '1':
                dockill1=f'tmp/{scac}/data/vunknown/'+filesel
                try:
                    os.remove(addpath(dockill1))
                except:
                    err[1]='Could not delete ...'
                try:
                    os.remove(addtxt(dockill1))
                except:
                    err[2]='Could not delete txt'


        if update is not None and modlink==10:
            modlink=0
            #Create the new database entry for the source document
            filesel=request.values.get('FileSel')

            if filesel != '1':
                docold=f'tmp/{scac}/data/vunknown/'+filesel
                docref=f'tmp/{scac}/data/vcompliance/'+filesel
                try:
                    shutil.move(addpath(docold),addpath(docref))
                except:
                    err[4]='File has been moved already'
                try:
                    shutil.move(addtxt(docold),addtxt(docref))
                except:
                    err[4]='File has been moved already'

            else:
                docref=''
                doctxt=''

            subject=request.values.get('subject')
            category=request.values.get('category')
            item = request.values.get('item')
            longs=request.values.get('longs')
            datedue = request.values.get('date1')
            datefiled = request.values.get('date2')
            docsave= ntpath.basename(docref)

            if datedue == '':
                newdate1 = None
            else:
                newdate1 = datedue

            if datefiled == '':
                newdate2 = None
            else:
                newdate2 = datedue

            input = Compliance(Subject=subject, Category=category, Item=item, Textinfo=longs, File1=docsave, File2=None, File3=None, Date1=newdate1, Date2=newdate2)
            db.session.add(input)
            db.session.commit()
            db.session.close()

            odata = Compliance.query.all()

            modlink=0
            leftscreen=1
            oder=0
            leftsize=10
            err=['All is well', ' ', ' ', ' ',  ' ']
# ____________________________________________________________________________________________________________________E.Newjob.Compliance

        if modlink==20:
            odata=Compliance.query.filter((Compliance.Textinfo.contains(searchfind)) | (Compliance.Subject.contains(searchfind)) | (Compliance.Category.contains(searchfind))).all()

    #This is the else for 1st time through (not posting data from overseas.html)
    else:
        from viewfuncs import popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        oder=0
        cache=0
        modata=0
        modlink=0
        fdata=0
        filesel=''
        docref=''
        doctxt=''
        longs=''
        odata = Compliance.query.all()
        leftscreen=1
        leftsize=10
        err=['All is well', ' ', ' ', ' ',  ' ']
        actype = ''

    fdata = myoslist('data/vunknown')
    fdata.sort()
    doctxt=os.path.splitext(docref)[0] + '.txt'
    leftsize = 8
    acdata=[]
    for adat in db.session.query(Compliance.Subject).distinct():
        acdata.append(adat.Subject)
    return odata,oder,err,modata,modlink,leftscreen,docref,leftsize,fdata,filesel,today,now,doctxt,longs,acdata,actype
