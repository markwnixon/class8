from runmain import db
from models import Invoices, JO, Income, Bills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Orders, Drops, Services
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import subprocess
import img2pdf
from CCC_system_setup import addpath, scac, tpath

today=datetime.date.today()

def nodollar(infloat):
    outstr="%0.2f" % infloat
    return outstr

def dollar(infloat):
    outstr='$'+"%0.2f" % infloat
    return outstr

def avg(in1,in2):
    out=(in1+in2)/2
    return out

def stat_update(status,newval,i):
    a=list(status)
    a[i]=newval
    b=''.join(a)
    return b

def d2s(instr):
    try:
        instr=instr.replace('$','').replace(',','')
    except:
        instr=str(instr)
    try:
        infloat=float(instr)
        outstr="%0.2f" % infloat
    except:
        outstr=instr
    return outstr

def d1s(instr):
    try:
        instr=instr.replace('$','').replace(',','')
    except:
        instr=str(instr)
    try:
        infloat=float(instr)
        outstr="%0.1f" % infloat
    except:
        outstr=instr
    return outstr

def dropupdate(dropblock):
    droplist=dropblock.splitlines()
    avec=[' ']*5
    for j,drop in enumerate(droplist):
        if j<5:
            avec[j]=drop
    entity=avec[0]
    addr1=avec[1]
    edat=Drops.query.filter((Drops.Entity==entity) & (Drops.Addr1==addr1)).first()
    if edat is None:
        input = Drops(Entity=avec[0],Addr1=avec[1],Addr2=avec[2],Phone=avec[3],Email=avec[4])
        db.session.add(input)
        db.session.commit()
    return entity

def dropupdate2(bid):
    pdat = People.query.filter(People.id == bid).first()
    if pdat is not None:
        droplist = [pdat.Company,pdat.Addr1,pdat.Addr2,pdat.Email,pdat.Telephone]
        avec=[' ']*5
        for j,drop in enumerate(droplist):
            if j<5:
                avec[j]=drop
        entity=avec[0]
        addr1=avec[1]
        edat=Drops.query.filter((Drops.Entity==entity) & (Drops.Addr1==addr1)).first()
        if edat is None:
            input = Drops(Entity=avec[0],Addr1=avec[1],Addr2=avec[2],Phone=avec[3],Email=avec[4])
            db.session.add(input)
            db.session.commit()

        edatnew = Drops.query.filter((Drops.Entity==entity) & (Drops.Addr1==addr1)).first()
        return edatnew.id
    else:
        return 0



def getexpimp(con):
    idata = Interchange.query.filter(Interchange.CONTAINER == con).all()
    for idat in idata:
        ctype = idat.TYPE
        if ctype == 'Load Out':
            return 'Import'
        if ctype == 'Load In':
            return 'Export'
    return 'No Info'

def dropupdate3(txt):
    edat = Drops.query.filter(Drops.Entity == 'Baltimore Seagirt').first()
    return edat.id

def txtfile(infile):
    base=os.path.splitext(infile)[0]
    tf=base+'.txt'
    return tf

def doctransfer(d1,d2,filesel):
    if filesel != '1':
        docold=f'tmp/{scac}/processing/'+d1+'/'+filesel
        docref=f'tmp/{scac}/data/'+d2+'/'+filesel
        oldtxt=docold.split('.',1)[0]+'.txt'
        doctxt=docref.split('.',1)[0]+'.txt'
        try:
            shutil.move(addpath(docold),addpath(docref))
            shutil.move(addpath(oldtxt),addpath(doctxt))
        except OSError:
            print('File has been moved already')
    else:
        docref=''
        doctxt=''
    return docref,doctxt


def commaguard(instring):
    sandwich=re.compile(r',[A-Za-z]')
    t1=sandwich.findall(instring)
    for t in t1:
        l=t[1]
        instring=instring.replace(t,', '+l)
    return instring

def parseline(line,j):
    line=commaguard(line)
    splitline=line.upper().split()
    outline=[]
    newline=''
    for word in splitline:
        if len(newline)<j-7:
            newline=newline+word+' '
        else:
            outline.append(newline)
            newline=word+' '
    outline.append(newline)
    return outline

def parselinenoupper(line,j):
    line=commaguard(line)
    splitline=line.split()
    outline=[]
    newline=''
    for word in splitline:
        if len(newline)<j-7:
            newline=newline+word+' '
        else:
            outline.append(newline)
            newline=word+' '
    outline.append(newline)
    return outline

def nonone(input):
    if input is not None:
        output=int(input)
    else:
        output=0
    return output

def nons(input):
    if input is None:
        input=''
    return input

def nononef(input):
    if input=='' or input==' ' or input=='None':
        output=0.00
    else:
        input=input.replace('$','').replace(',','')
        output=float(input)
    return output

def GetCo(dtype,lpt):
    if dtype=='Jays':
        if lpt=='All':
            data=People.query.filter( (People.Ptype=='Jays') | (People.Ptype== 'TowCo') ).all()
        if lpt=='Jays':
            data=People.query.filter(People.Ptype=='Jays').all()
        if lpt=='TowCo':
            data=People.query.filter(People.Ptype=='TowCo').all()
        if lpt=='TowPu':
            data=People.query.filter(People.Ptype=='TowPu').all()
        if lpt=='TowDel':
            data=People.query.filter(People.Ptype=='TowDel').all()
    return data

def GetCo3(dtype):
    if dtype=='JaysAuto':
        pdata1=People.query.filter(People.Ptype=='TowCo').order_by(People.Company).all()
        pdata2=People.query.filter(People.Ptype=='TowPu').order_by(People.Company).all()
        pdata3=People.query.filter(People.Ptype=='TowDel').order_by(People.Company).all()
    return pdata1,pdata2,pdata3

def popjo(oder,monsel):
    m=Storage.query.get(oder)
    headjo=m.Jo
    if monsel is None or monsel==0:
        char3=headjo[2]
    else:
        char3=str(monsel)
        char3=char3.replace('10','X').replace('11','Y').replace('12','Z')
    thisjo='FS'+char3+'01'+headjo[5:8]
    return thisjo


def jovec(jo):
    jolist=['']*12
    char3=['1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'Y', 'Z']
    k=0
    for i in char3:
        jolist[k]='FS'+i+'01'+jo[5:8]
        k=k+1
    return jolist

def newjo(jtype,sdate):
    dt = datetime.datetime.strptime(sdate, '%Y-%m-%d')
    year= str(dt.year)
    day=str(dt.day)
    month=str(dt.month)
    lv=JO.query.get(1)
    nextid=lv.nextid
    eval=str(nextid%100).zfill(2)
    day2="{0:0=2d}".format(int(day))
    if month=='10':
        month='X'
    if month=='11':
        month='Y'
    if month=='12':
        month='Z'
    if jtype=='J':
        nextjo='JA'+month+day2+year[3]+eval
    else:
        nextjo='KT'+month+day2+year[3]+eval
    input2 = JO(jo=nextjo, nextid=0, date=sdate, status=1)
    db.session.add(input2)
    lv.nextid=nextid+1
    db.session.commit()
    return nextjo

def tabdataR(ntab,a1,a2,a3,a4,a5,reach):
    crawl=int(reach/2)
    u = [0]*ntab
    t = [0]*ntab
    s = [0]*ntab
    a = [0]*ntab
    add = [0]*ntab
    sub = [0]*ntab
    top = [0]*ntab
    bot = [0]*ntab
    bigset=[a1, a2, a3, a4, a5]
    for i in range(ntab):
        u[i]=len(bigset[i])
        ap=str(i+1)
        add[i] = request.values.get('up'+ap)
        sub[i] = request.values.get('dn'+ap)
        top[i] = request.values.get('topvalue'+ap)
        bot[i] = request.values.get('botvalue'+ap)
        if add[i] is not None:
            a[i] = int(top[i])+crawl
            t[i] = min(a[i],u[i])
            s[i] = max(t[i]-reach,0)
        elif sub[i] is not None:
            a[i] = int(bot[i])-crawl
            s[i] = max(a[i],0)
            t[i] = min(s[i]+reach,u[i])
        else:
            if top[i] is not None:
                t[i]=int(top[i])
            else:
                t[i]=u[i]
            if bot[i] is not None:
                s[i]=int(bot[i])
            else:
                s[i]=max(t[i]-reach,0)
        if u[i]<reach:
            t[i]=u[i]
        if i==0:
            subdata1=a1[s[i]:t[i]]
        if i==1:
            subdata2=a2[s[i]:t[i]]
        if i==2:
            subdata3=a3[s[i]:t[i]]
        if i==3:
            subdata4=a4[s[i]:t[i]]
        if i==4:
            subdata5=a5[s[i]:t[i]]
    if ntab==2:
        return subdata1,subdata2,s,t,u
    if ntab==3:
        return subdata1,subdata2,subdata3,s,t,u
    if ntab==4:
        return subdata1,subdata2,subdata3,subdata4,s,t,u
    if ntab==5:
        return subdata1,subdata2,subdata3,subdata4,subdata5,s,t,u

def tabdata(ntab,a1,a2,a3,a4,a5):
    reach=10
    crawl=int(reach/2)
    u = [0]*ntab
    t = [0]*ntab
    s = [0]*ntab
    a = [0]*ntab
    add = [0]*ntab
    sub = [0]*ntab
    top = [0]*ntab
    bot = [0]*ntab
    bigset=[a1, a2, a3, a4, a5]
    for i in range(ntab):
        u[i]=len(bigset[i])
        ap=str(i+1)
        add[i] = request.values.get('up'+ap)
        sub[i] = request.values.get('dn'+ap)
        top[i] = request.values.get('topvalue'+ap)
        bot[i] = request.values.get('botvalue'+ap)
        if add[i] is not None:
            a[i] = int(top[i])+crawl
            t[i] = min(a[i],u[i])
            s[i] = max(t[i]-reach,0)
        elif sub[i] is not None:
            a[i] = int(bot[i])-crawl
            s[i] = max(a[i],0)
            t[i] = min(s[i]+reach,u[i])
        else:
            if top[i] is not None:
                t[i]=int(top[i])
            else:
                t[i]=u[i]
            if bot[i] is not None:
                s[i]=int(bot[i])
            else:
                s[i]=max(t[i]-reach,0)
        if u[i]<reach:
            t[i]=u[i]
        if i==0:
            subdata1=a1[s[i]:t[i]]
        if i==1:
            subdata2=a2[s[i]:t[i]]
        if i==2:
            subdata3=a3[s[i]:t[i]]
        if i==3:
            subdata4=a4[s[i]:t[i]]
        if i==4:
            subdata5=a5[s[i]:t[i]]
    if ntab==2:
        return subdata1,subdata2,s,t,u
    if ntab==3:
        return subdata1,subdata2,subdata3,s,t,u
    if ntab==4:
        return subdata1,subdata2,subdata3,subdata4,s,t,u
    if ntab==5:
        return subdata1,subdata2,subdata3,subdata4,subdata5,s,t,u

def numcheckv(a1):
    numchecked=0
    avec=[]
    for a in a1:
        testone = request.values.get('oder'+str(a.id))
        if testone:
            numchecked=numchecked+1
            avec.append(int(testone))
    return avec

def numcheckvec(a1,a2):
    numchecked=0
    avec=[]
    for a in a1:
        testone = request.values.get(a2+str(a.id))
        if testone:
            numchecked=numchecked+1
            avec.append(int(testone))
    return avec

def numcheck(ntab, a1, a2, a3, a4, a5, textdat):
    out=[0]*ntab
    numchecked=0
    bigdata=[a1,a2,a3,a4,a5]
    for i in range(ntab):
        if bigdata[i] != 0:
            for data in bigdata[i]:
                testone = request.values.get(textdat[i]+str(data.id))
                if testone:
                    numchecked=numchecked+1
                    out[i]=int(testone)
    if ntab==1:
        return out[0],numchecked
    if ntab==2:
        return out[0],out[1],numchecked
    if ntab==3:
        return out[0],out[1],out[2],numchecked
    if ntab==4:
        return out[0],out[1],out[2],out[3],numchecked
    if ntab==5:
        return out[0],out[1],out[2],out[3],out[4],numchecked


def sdiff(a,b):
    try:
        af=nononef(a)
    except:
        af=0.0
    try:
        bf=nononef(b)
    except:
        bf=0.0
    sf=af-bf
    nsf="{:.2f}".format(sf)
    return nsf

def sadd(a,b):
    try:
        af=nononef(a)
    except:
        af=0.0
    try:
        bf=nononef(b)
    except:
        bf=0.0
    sf=af+bf
    nsf="{:.2f}".format(sf)
    return nsf

def init_tabdata(ntab,a1,a2,a3,a4,a5):
    u = [0]*ntab
    t = [0]*ntab
    s = [0]*ntab
    bigset=[a1, a2, a3, a4, a5]
    for i in range(ntab):
        u[i]=len(bigset[i])
        t[i]=u[i]
        s[i]=max(t[i]-10,0)
        if i==0:
            subdata1=a1[s[i]:t[i]]
        if i==1:
            subdata2=a2[s[i]:t[i]]
        if i==2:
            subdata3=a3[s[i]:t[i]]
        if i==3:
            subdata4=a4[s[i]:t[i]]
        if i==4:
            subdata5=a5[s[i]:t[i]]
    if ntab==2:
        return subdata1,subdata2,s,t,u
    if ntab==3:
        return subdata1,subdata2,subdata3,s,t,u
    if ntab==4:
        return subdata1,subdata2,subdata3,subdata4,s,t,u
    if ntab==5:
        return subdata1,subdata2,subdata3,subdata4,subdata5,s,t,u

def timedata(subdata1):
    k=0
    bm=['']*len(subdata1)
    cm=['']*len(subdata1)
    for data in subdata1:
        mdata=['']*12
        ndata=['']*12
        jo=data.Jo
        jol=jovec(jo)
        m=0
        for j in jol:
            idat=Invoices.query.filter(Invoices.SubJo==j).first()
            if idat is not None:
                if idat.Total is not None:
                    mdata[m]=str(idat.Total)
                    ndata[m]=idat.Status
            m=m+1
        bm[k]=mdata
        cm[k]=ndata
        k=k+1
    return bm, cm

def init_billing_zero():
    bill=0
    peep=0
    cache=0
    modata=0
    modlink=0
    fdata=0
    adata=0
    cdat=0
    pb=0
    passdata=0
    vdata=0
    caldays=0
    daylist=0
    weeksum=0
    nweeks=0
    return bill,peep,cache,modata,modlink,fdata,adata,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks

def init_storage_zero():
    monsel=0
    oder=0
    peep=0
    serv=0
    invo=0
    inco=0
    cache=0
    modata=0
    modlink=0
    fdata=0
    invooder=0
    return monsel,oder,peep,serv,invo,inco,cache,modata,modlink,fdata,invooder

def init_truck_zero():
    oder=0
    poof=0
    tick=0
    serv=0
    peep=0
    invo=0
    cache=0
    modata=0
    modlink=0
    stayslim=0
    invooder=0
    stamp=0
    fdata=0
    csize=0
    invodate=0
    inco=0
    cdat=0
    pb=0
    passdata=0
    vdata=0
    caldays=0
    daylist=0
    weeksum=0
    nweeks=0
    return oder, poof, tick, serv, peep, invo, cache, modata, modlink, stayslim, invooder, stamp, fdata, csize, invodate, inco, cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks

def init_ocean_zero():
    ship=0
    book=0
    auto=0
    peep=0
    comm=0
    invo=0
    cache=0
    modata=0
    modlink=0
    stayslim=0
    invooder=0
    stamp=0
    fdata=0
    csize=0
    invodate=0
    inco=0
    cdat=0
    pb=0
    passdata=0
    vdata=0
    caldays=0
    daylist=0
    weeksum=0
    nweeks=0
    return ship,book,auto,peep,comm,invo,cache,modata,modlink,stayslim,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks


def init_horizon_zero():
    cars=0
    auto=0
    peep=0
    invo=0
    cache=0
    modata=0
    modlink=0
    invooder=0
    stamp=0
    fdata=0
    csize=0
    invodate=0
    inco=0
    cdat=0
    pb=0
    passdata=0
    vdata=0
    caldays=0
    daylist=0
    weeksum=0
    nweeks=0
    return cars,auto,peep,invo,cache,modata,modlink,invooder,stamp,fdata,csize,invodate,inco,cdat,pb,passdata,vdata,caldays,daylist,weeksum,nweeks




def init_horizon_blank():
    filesel=''
    docref=''
    search11=''
    search12=''
    search21=''
    search22=''
    search31=''
    search32=''
    return filesel, docref, search11, search12, search21, search22, search31, search32

def init_billing_blank():
    filesel=''
    docref='',
    search11=''
    search12=''
    search13=''
    search14=''
    search21=''
    search22=''
    bType=''
    bClass=''
    return filesel,docref,search11,search12,search13,search14,search21,search22,bType,bClass

def init_storage_blank():
    invojo=''
    filesel=''
    docref='',
    search11=''
    search12=''
    search21=''
    search31=''
    return invojo, filesel,docref,search11,search12,search21,search31


def init_ocean_blank():
    filesel=''
    docref=''
    josearch1=''
    booksearch1=''
    josearch2=''
    booksearch2=''
    search31=''
    search32=''
    search41=''
    search42=''
    search51=''
    search52=''
    return filesel, docref, josearch1, booksearch1, josearch2, booksearch2, search31, search32, search41, search42, search51 , search52






def money12(basejo):
    involine=['']*13
    paidline=['']*13
    refline=['']*13
    balline=['']*13
    jol=jovec(basejo)

    for m,j in enumerate(jol):
        idat=Invoices.query.filter(Invoices.SubJo==j).first()
        pdat=Income.query.filter(Income.SubJo==j).first()
        invoamt=0.00
        incoamt=0.00
        if idat is not None:
            if idat.Total is not None:
                involine[m]=str(idat.Total)
                invoamt=float(idat.Total)
        if pdat is not None:
            if pdat.Amount is not None:
                paidline[m]=str(pdat.Amount)
                refline[m]=pdat.Ref
                incoamt=float(pdat.Amount)
        if idat is not None and pdat is not None:
            #balline[m]=sdiff(idat.Total,pdat.Amount)
            diffamt=invoamt-incoamt
            balline[m]=str(diffamt)
        elif idat is not None:
            balline[m]=str(idat.Total)
        elif pdat is not None:
            balline[m]=str(pdat.Amount)

    return involine,paidline,refline,balline

def calendar_calcs(thistype):
    today = datetime.datetime.today()
    ndays=18
    day=today.day
    d = today
    nlist=ndays*4
    caldays=list(range(ndays))
    caldt=list(range(ndays))
    daylist=list(range(nlist))
    for i in range(ndays):
        for j in range(4):
            k=4*i+j
            daylist[k]=0
    for i in range(6):
        days_ahead1 = i - 7 - d.weekday()
        if days_ahead1 <= 0:
            days_ahead1 += 7
        days_ahead2 = days_ahead1 + 7
        days_ahead0 = days_ahead1 - 7
        next_weekday0= d + datetime.timedelta(days_ahead0)
        next_weekday1= d + datetime.timedelta(days_ahead1)
        next_weekday2= d + datetime.timedelta(days_ahead2)
        calmon0=str(next_weekday0.month)
        calmon1=str(next_weekday1.month)
        calmon2=str(next_weekday2.month)
        caldays[i+12]= calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon2)] + ' ' + str(next_weekday2.day)
        if next_weekday1.day==day:
            caldays[i+6]=   'X' + calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon1)] + ' ' + str(next_weekday1.day)
        else:
            caldays[i+6]=   calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon1)] + ' ' + str(next_weekday1.day)
        caldays[i]=   calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon0)] + ' ' + str(next_weekday0.day)
    # Create DateTime obj while we are here:
        datestr2=str(next_weekday2.month) + '/' + str(next_weekday2.day) + '/' + str(next_weekday2.year)
        datestr1=str(next_weekday1.month) + '/' + str(next_weekday1.day) + '/' + str(next_weekday1.year)
        datestr0=str(next_weekday0.month) + '/' + str(next_weekday0.day) + '/' + str(next_weekday0.year)
        caldt[i] = datetime.datetime.strptime(datestr0, '%m/%d/%Y')
        caldt[i+6] = datetime.datetime.strptime(datestr1, '%m/%d/%Y')
        caldt[i+12] = datetime.datetime.strptime(datestr2, '%m/%d/%Y')
    if thistype=='Trucking':
        for i in range(ndays):
            dloc=caldt[i]
            odata = Orders.query.filter(Orders.Date == dloc)
            j=0
            for data in odata:
                k=4*i+j
                daylist[k]=[data.Order, data.Pickup, data.Booking, data.Driver, data.Time, data.Jo, data.Container, data.Status]
                j=j+1

    if thistype=='Billing':
        for i in range(ndays):
            dloc=caldt[i]
            odata = Bills.query.filter(Bills.bDate == dloc)
            j=0
            for data in odata:
                k=4*i+j
                daylist[k]=[data.Company, data.bAmount, data.Account, data.Status]
                j=j+1

    return caldays,daylist


def calendar7_weeks(thistype,lweeks):
    today = datetime.datetime.today()
    nweeks=lweeks[0]+lweeks[1]
    ndays=nweeks*7
    day=today.day
    d = today
    nlist=ndays*4
    caldays=list(range(ndays))
    caldt=list(range(ndays))
    daylist=list(range(nlist))
    days_ahead=[0]*nweeks
    calmon=[0]*nweeks
    next_weekday=[0]*nweeks
    datestr=[0]*nweeks

    for i in range(ndays):
        for j in range(4):
            k=4*i+j
            daylist[k]=0

    for i in range(7):
        days_ahead1 = i - 7 - d.weekday()
        if days_ahead1 <= 0:
            days_ahead1 += 7
        day0=days_ahead1-7*lweeks[0]
        for m in range(nweeks):
            days_ahead[m]=day0+7*m
            next_weekday[m] = d + datetime.timedelta(days_ahead[m])
            calmon[m]=str(next_weekday[m].month)
            caldays[i+7*m]=   calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[m])] + ' ' + str(next_weekday[m].day)
            datestr[m]=str(next_weekday[m].month) + '/' + str(next_weekday[m].day) + '/' + str(next_weekday[m].year)
            caldt[i+7*m] = datetime.datetime.strptime(datestr[m], '%m/%d/%Y')

        if next_weekday[lweeks[0]].day==day:
            caldays[i+7*lweeks[0]]=   'X' + calendar.day_abbr[i] + ' ' + calendar.month_abbr[int(calmon[lweeks[0]])] + ' ' + str(next_weekday[lweeks[0]].day)

    if thistype=='Trucking':
        weeksum=0
        for i in range(ndays):
            dloc=caldt[i]
            odata = Orders.query.filter(Orders.Date == dloc).all()
            for j,data in enumerate(odata):
                k=4*i+j
                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=Drops.query.filter(Drops.Entity==data.Company).first()
                loc2=Drops.query.filter(Drops.Entity==data.Company2).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12=''
                    addr22=''
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                daylist[k]=[data.Order, data.Pickup, data.Booking, data.Driver, data.Time, data.Jo, data.Container, data.Status, shipper, data.id, data.Company, addr11, addr21, data.Company2, addr12, addr22, phone, trk, plate, cb]

    if thistype=='Moving':
        weeksum=0
        for i in range(ndays):
            dloc=caldt[i]
            odata = Moving.query.filter(Moving.Date == dloc).all()
            for j,data in enumerate(odata):
                k=4*i+j
                shipper=data.Shipper
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]
                loc1=Drops.query.filter(Drops.Entity==data.Drop1).first()
                loc2=Drops.query.filter(Drops.Entity==data.Drop2).first()
                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()

                if loc1 is not None:
                    addr11=loc1.Addr1
                    addr21=loc1.Addr2
                else:
                    addr11=''
                    addr21=''
                if loc2 is not None:
                    addr12=loc2.Addr1
                    addr22=loc2.Addr2
                else:
                    addr12='NF'
                    addr22='NF'
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                daylist[k]=[data.id, data.Jo, shipper, data.Drop1, addr11, addr21, data.Time, data.Drop2, addr12, addr22, data.Time2, data.Container, data.Driver, data.Status, phone, trk, plate, cb]




    if thistype=='Overseas':
        weeksum=0
        for i in range(ndays):
            dloc=caldt[i]
            odata = OverSeas.query.filter(OverSeas.PuDate==dloc).all()
            for j,data in enumerate(odata):
                k=4*i+j
                shipper=data.BillTo
                if len(shipper)>8:
                    shipper=re.match(r'\W*(\w[^,. !?"]*)', shipper).groups()[0]

                pod=data.Pod
                pol=data.Pol
                if len(pod)>8:
                    pod=re.match(r'\W*(\w[^,. !?"]*)', pod).groups()[0]
                if len(pol)>8:
                    pol=re.match(r'\W*(\w[^,. !?"]*)', pol).groups()[0]

                container=data.Container
                book=data.Booking
                bdat=Bookings.query.filter(Bookings.Booking==data.Booking).first()
                if bdat is not None:
                    doccut=bdat.PortCut.strftime('%m/%d/%Y')
                else:
                    doccut=''
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                drv=Drivers.query.filter(Drivers.Name==data.Driver).first()
                if drv is not None:
                    phone=drv.Phone
                    trk=drv.Truck
                    plate=drv.Tag
                else:
                    phone=''
                    trk=''
                    plate=''

                daylist[k]=[data.id, shipper, book, container, pol, pod, data.Jo, data.Status, data.Driver, phone, trk, plate, doccut, cb]


    if thistype=='Horizon':
        weeksum=0
        for i in range(ndays):
            dloc=caldt[i]
            adata = db.session.query(Autos.Jo).distinct().filter(Autos.Date2==dloc)
            for j,data in enumerate(adata):
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==data.Jo).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                adat=Autos.query.filter(Autos.Jo==data.Jo).first()
                com=adat.TowCompany
                if com is None or com=='' or len(com)<2:
                    com='FIX'

                if adat is not None:
                    autolist=[]
                    allcars=Autos.query.filter(Autos.Jo==adat.Jo).all()
                    for car in allcars:
                        autolist.append([car.Year,car.Make,car.Model,car.VIN])


                try:
                    amt=adat.TowCost
                    amt=nononef(amt)
                    ncars=len(autolist)
                    amteach=amt/ncars
                    amteach=dollar(amteach)
                except:
                    amteach='0.00'
                    ncars=0

                k=4*i+j
                daylist[k]=[adat.id, com, adat.TowCost, adat.Status, autolist, cb, adat.Jo, amteach, ncars]

    if thistype=='Billing':
        adata= Accounts.query.all()
        sum=[0]*len(adata)
        weekly=[]
        weeksum=[0]*nweeks
        weekstop=6
        thisweek=0

        for i in range(ndays):
            dloc=caldt[i]
            odata = Bills.query.filter(Bills.bDate == dloc)
            j=0
            for data in odata:
                k=4*i+j

                billno='Bill'+str(data.id)
                cb=[]
                comlist=ChalkBoard.query.filter(ChalkBoard.Jo==billno).all()
                for c in comlist:
                    addline=c.register_date.strftime('%m/%d/%Y')+' by '+c.creator+' at '+c.register_date.strftime('%H:%M')+': '+c.comments
                    addline=parselinenoupper(addline,85)
                    for a in addline:
                        cb.append(a)

                daylist[k]=[data.id, data.Company, data.bAmount, data.pAccount, data.Status, data.bCat + ' ' + data.bType, data.bAccount, cb]
                for mm,adat in enumerate(adata):
                    if adat.Name == data.pAccount:
                        sum[mm]=sum[mm]+nononef(data.bAmount)
                j=j+1

            if i==weekstop:
                for mm,adat in enumerate(adata):
                    if sum[mm]>0:
                        weekly.append([adat.Name, sum[mm]])
                        sum[mm]=0
                weeksum[thisweek]=weekly
                weekly=[]
                thisweek=thisweek+1
                weekstop=weekstop+7

    return caldays,daylist,weeksum

#______________________________________________________________________________________________________________________________________________________________________________________________




def viewbuttons():
    match    =  request.values.get('Match')
    modify   =  request.values.get('Modify')
    vmod     =  request.values.get('Vmod')
    minvo    =  request.values.get('MakeI')
    mpack    =  request.values.get('MakeP')
    viewo     =  request.values.get('ViewO')
    viewi     =  request.values.get('ViewI')
    viewp     =  request.values.get('ViewP')
    print    =  request.values.get('Print')
    addE     = request.values.get('addentity')
    addS     = request.values.get('addservice')
    slim     = request.values.get('slim')
    stayslim = request.values.get('stayslim')
    unslim = request.values.get('unslim')
    limitptype = request.values.get('limitptype')
    returnhit = request.values.get('Return')
    deletehit = request.values.get('Delete')
    # hidden values
    update   =  request.values.get('Update')
    invoupdate = request.values.get('invoUpdate')
    emailnow = request.values.get('emailnow')
    emailinvo = request.values.get('emailInvo')
    newjob=request.values.get('NewJ')
    thisjob=request.values.get('ThisJob')
    recpay   = request.values.get('RecPay')
    hispay   = request.values.get('HisPay')
    recupdate = request.values.get('recUpdate')
    calendar=request.values.get('Calendar')
    calupdate=request.values.get('calupdate')
    return match,modify,vmod,minvo,mpack,viewo,viewi,viewp,print,addE,addS,slim,stayslim,unslim,limitptype,returnhit,deletehit,update,invoupdate,emailnow,emailinvo,newjob,thisjob,recpay,hispay,recupdate,calendar,calupdate


def get_ints():
    oder=request.values.get('oder')
    poof=request.values.get('poof')
    tick=request.values.get('tick')
    serv=request.values.get('serv')
    peep=request.values.get('peep')

    invo=request.values.get('invo')
    invooder=request.values.get('invooder')
    cache=request.values.get('cache')
    modlink =  request.values.get('passmodlink')

    oder=nonone(oder)
    poof=nonone(poof)
    tick=nonone(tick)
    serv=nonone(serv)
    peep=nonone(peep)

    invo=nonone(invo)
    invooder=nonone(invooder)
    cache=nonone(cache)
    modlink=nonone(modlink)

    return oder,poof,tick,serv,peep,invo,invooder,cache,modlink



def comporname(company,name):
    if company is None or company=='':
        nameout=name
    else:
        if len(company)<3:
            nameout=name
        else:
            nameout=company
    return nameout

def fullname(first,middle,last):
    if first is not None:
        nameout=first
    else:
        nameout=''
    if middle is not None:
        nameout=nameout+' '+middle
    if last is not None:
        nameout=nameout+' '+last
    if len(nameout)>55:
        nameout=first + ' ' + last
    return nameout

def address(addr1,addr2,addr3):
    street=addr1
    if addr3 is None or addr3=='':
        cityst=addr2
    else:
        if len(addr3)<5:
            cityst=addr2
    if addr2 is None or addr2=='':
        cityst=addr3
        if len(addr2)<3:
            cityst=addr3
    if addr2 and addr3:
        if len(addr2)>3 and len(addr3)>3:
            street=addr1 + ' ' + addr2
            cityst=addr3
    return street,cityst

def nononestr(input):
    if input is None or input=='None':
        output=' '
    else:
        output=input
    return output

def containersout(datecut):
    idata=Interchange.query.filter((Interchange.Status=='Unmatched') & (Interchange.Date > datecut)).all()
    cout=[]
    for data in idata:
        cout.append(data.CONTAINER)

    return cout

def chassismatch(odat):
    con=odat.Container
    book=odat.Booking
    if 1==1:
        ticket1=Interchange.query.filter((Interchange.RELEASE==book) | (Interchange.CONTAINER==con)).first()
        if ticket1 is not None:
            ticket2=Interchange.query.filter(((Interchange.RELEASE==book) | (Interchange.CONTAINER==con)) & (Interchange.id != ticket1.id)).first()

        if ticket1 is not None and ticket2 is not None:
            date1=ticket1.Date
            date2=ticket2.Date
            if date1>date2:
                d1=date2
                d2=date1
            else:
                d1=date1
                d2=date2
            delta=d2-d1
            chassisdays=delta.days+1
            ticket1.Company=odat.Shipper
            ticket2.Company=odat.Shipper
            ticket1.Jo=odat.Jo
            ticket2.Jo=odat.Jo
            #Now check to see if a no-charge chassis was used...
            chas1 = ticket1.CHASSIS
            chas2 = ticket2.CHASSIS
            if chas1 == 'GBL' or chas2 == 'GBL':
                chassisdays = 0
                odat.BOL = 'GBL Chassis'
                odat.Chassis = 'GBL'
            odat.Container=ticket1.CONTAINER
            odat.Date=d1
            odat.Date2=d2
            db.session.commit()
        else:

            chassisdays=1
            d1=today
            d2=today

    return chassisdays,d1,d2




def global_inv(odata,odervec):
    #First create all the invoices for these specific jobs
    for oder in odervec:
        myo=Orders.query.get(oder)
        qty,d1,d2=chassismatch(myo)
        Invoices.query.filter(Invoices.Jo==myo.Jo).delete()
        myo.Status=stat_update(myo.Status,'1',1)
        db.session.commit()


    for oder in odervec:
        myo=Orders.query.get(oder)
        qty,d1,d2=chassismatch(myo)
        shipper=myo.Shipper
        jo=myo.Jo
        bid=myo.Bid
        lid=myo.Lid
        did=myo.Did
        cache=myo.Storage+1

        mys=Services.query.filter(Services.Service=='Chassis Fees').first()
        descript= 'Days of Chassis'
        price=float(mys.Price)
        chassis_amount=price*qty
        haul_amount=float(myo.Amount)
        total=haul_amount+chassis_amount
        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service=mys.Service, Description=descript, Ea=mys.Price, Qty=qty, Amount=chassis_amount, Total=total, Date=today, Original=None, Status='New')
        db.session.add(input)
        db.session.commit()
        descript= 'Order ' + myo.Order+ ' Line Haul '+ myo.Company + ' to ' + myo.Company2
        input=Invoices(Jo=myo.Jo, SubJo=None, Pid=bid, Service='Line Haul', Description=descript, Ea=myo.Amount, Qty=1, Amount=haul_amount, Total=total, Date=today, Original=None, Status='New')
        db.session.add(input)
        db.session.commit()
        #Now write out the invoice
        ldata=Invoices.query.filter(Invoices.Jo==myo.Jo).order_by(Invoices.Ea.desc()).all()
        pdata1=People.query.filter(People.id==myo.Bid).first()
        pdata2=Drops.query.filter(Drops.id==myo.Lid).first()
        pdata3=Drops.query.filter(Drops.id==myo.Did).first()
        import make_T_invoice
        make_T_invoice.main(myo,ldata,pdata1,pdata2,pdata3,cache,today,0)
        if cache>1:
            docref=f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'c'+str(cache)+'.pdf'
        else:
            docref=f'tmp/{scac}/data/vinvoice/INV'+myo.Jo+'.pdf'
        myo.Path=docref
        myo.Storage=cache
        db.session.commit()
# Now all the invoices are created.  Next pack them up and create a single master invoice.
    keydata=[0]*len(odervec)
    grandtotal=0
    for j, i in enumerate(odervec):
        odat=Orders.query.get(i)
        if j==0:
            pdata1=People.query.filter(People.id==odat.Bid).first()
            date1=odat.Date
            order=odat.Order
            date2=odat.Date2
        dtest1=odat.Date
        dtest2=odat.Date2
        if dtest1<date1:
            date1=dtest1
        if dtest2>date2:
            date2=dtest2
        idat=Invoices.query.filter(Invoices.Jo==odat.Jo).order_by(Invoices.Ea.desc()).first()
        keydata[j]=[odat.Jo, odat.Booking, odat.Container, idat.Total, ' For Global to Baltimore Seagirt']
        grandtotal=grandtotal+float(idat.Total)
        # put together the file paperwork

    file1=f'tmp/{scac}/data/vinvoice/P_' + 'test.pdf'
    cache2 = int(odat.Detention)
    cache2=cache2+1
    docref=f'tmp/{scac}/data/vinvoice/P_c'+str(cache2)+'_' + order + '.pdf'

    for j, i in enumerate(odervec):
        odat=Orders.query.get(i)
        odat.Location=docref
        db.session.commit()


    import make_TP_invoice
    make_TP_invoice.main(file1,keydata,grandtotal,pdata1,date1,date2)

    invooder=oder
    leftscreen=0
    leftsize=8
    modlink=0

    filegather=['pdfunite', addpath(file1)]
    for i in odervec:
        odat=Orders.query.get(i)
        filegather.append(addpath(odat.Path))

    filegather.append(addpath(docref))
    tes=subprocess.check_output(filegather)

    odat.Detention=cache2
    db.session.commit()

    return docref

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def docuploader(dbase):
    err = []

    if dbase == 'oder':
        oder = request.values.get('passoder')
        oder = nonone(oder)
        print(oder)
        odat = Orders.query.get(oder)
        base = odat.Jo

        file = request.files['sourceupload']
        if file.filename == '':
            err.append('No source file selected for uploading')

        if file and allowed_file(file.filename):
            name, ext = os.path.splitext(file.filename)
            filename1 = f'Source_{base}{ext}'
            filename2 = f'Source_{base}.pdf'
            output1 = addpath(tpath(dbase,filename1))
            output2 = addpath(tpath(dbase,filename2))
            file.save(output1)
            if filename1 != filename2:
                try:
                    with open(output2,"wb") as f:
                        f.write(img2pdf.convert(output1))
                    os.remove(output1)
                except:
                    err.append(f'Problem converting {filename1} to pdf')
                    filename2 = filename1
            err.append(f'Source uploaded as {filename2}')
            odat.Original = filename2
            db.session.commit()
        else:
            err.append('Allowed file types are txt, pdf, png, jpg, jpeg, gif')

    if dbase == 'poof':
        oder = request.values.get('passoder')
        oder = nonone(oder)
        print(oder)
        odat = Orders.query.get(oder)
        base = odat.Jo

        file = request.files['proofupload']
        if file.filename == '':
            err.append('No file selected for uploading')

        if file and allowed_file(file.filename):
            name, ext = os.path.splitext(file.filename)
            filename1 = f'Proof_{base}{ext}'
            filename2 = f'Proof_{base}.pdf'
            output1 = addpath(tpath('poof',filename1))
            output2 = addpath(tpath('poof',filename2))
            file.save(output1)
            if filename1 != filename2:
                try:
                    with open(output2,"wb") as f:
                        f.write(img2pdf.convert(output1))
                    os.remove(output1)
                except:
                    err.append(f'Problem converting {filename1}to pdf')
                    filename2 = filename1
            err.append(f'Proof uploaded as {filename2}')
            odat.Proof = filename2
            db.session.commit()
        else:
            err.append('Allowed file types are txt, pdf, png, jpg, jpeg, gif')

    return err

def dataget_T(thismuch, dlist):
    # 0=order,#2=interchange,#3=people/services
    today = datetime.date.today()
    stopdate = today-datetime.timedelta(days=60)
    odata = 0
    idata = 0
    if thismuch == '1':
        stopdate = today-datetime.timedelta(days=60)
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Date > stopdate).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '2':
        stopdate = today-datetime.timedelta(days=120)
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Date > stopdate).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '3':
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Istat<2).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    elif thismuch == '4':
        if dlist[0] == 'on':
            odata = Orders.query.filter(Orders.Istat<4).all()
        if dlist[2] == 'on':
            idata = Interchange.query.filter(
                (Interchange.Date > stopdate) | (Interchange.Status == 'AAAAAA')).all()
    else:
        if dlist[0] == 'on':
            odata = Orders.query.all()
        if dlist[2] == 'on':
            idata = Interchange.query.all()
    return odata, idata
