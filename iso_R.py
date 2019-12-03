from runmain import db
from models import General, users, OverSeas, Orders
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import subprocess
from report_maker import reportmaker

def isoR():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec

        #Zero and blank items for default
        username = session['username'].capitalize()
        cache= request.values.get('cache')
        err=['','']
        docref=''
        doctxt=''
        fyear=2019
        oceantype=request.values.get('dt1')
        trucktype=request.values.get('dt2')
        detailtype=request.values.get('dt3')
        c1=request.values.get('dc1')
        c2=request.values.get('dc2')
        c3=request.values.get('dc3')
        c4=request.values.get('dc4')
        c5=request.values.get('dc5')
        c6=request.values.get('dc6')
        clist=[oceantype,trucktype,detailtype,c1,c2,c3,c4,c5,c6]

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')

        leftsize=8
        leftscreen=0

        interreport =  request.values.get('mtick')
        jayreport   =  request.values.get('jaystuff')
        increport   =  request.values.get('income')
        custreport  =  request.values.get('customer')
        thiscomp    =  request.values.get('thiscompany')
        PLreport    =  request.values.get('PL')

        sdate=request.values.get('start')
        fdate=request.values.get('finish')

        monvec=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for j, mon in enumerate(monvec):
            a=request.values.get(mon)
            if a is not None:
                b=request.values.get('focusyear')
                if b is not None:
                    fyear=2018
                jmonth=j+1
                enddays=[31,28,31,30,31,30,31,31,30,31,30,31]
                endday=enddays[j]
                start= datetime.date(fyear, jmonth, 1)
                end= datetime.date(fyear, jmonth, endday)
                sdate=start.strftime('%Y-%m-%d')
                fdate=end.strftime('%Y-%m-%d')

        if interreport is not None:
            cache,docref=reportmaker('mtick','')

        if jayreport is not None:
            cache,docref=reportmaker('jay','')

        if increport is not None:
            cache,docref=reportmaker('income','')

        if custreport is not None and thiscomp != '1':
            cache,docref=reportmaker('customer',thiscomp)

        if PLreport is not None:
            cache,docref=reportmaker('pl','')


        if cache is not None:
            #Save the current cache so we do not start from bad place in future
            udat=users.query.filter(users.name=='cache').first()
            udat.username=str(cache)
            db.session.commit()

            err=['All is well', ' ']


    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef, init_truck_zero
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        docref=''
        doctxt=''
        thiscomp=''
        leftscreen=0
        leftsize=8
        udat=users.query.filter(users.name=='Cache').first()
        cache=udat.username
        cache=nonone(cache)
        err=['All is well', ' ', ' ', ' ',  ' ']
        sdate=today
        fdate=today
        fyear=2019
        clist=['on','off']

    customerlist=[]
    if clist[0]=='on':
        odata=OverSeas.query.all()
        for odat in odata:
            cust=odat.BillTo
            if cust not in customerlist:
                customerlist.append(cust)
    if clist[1]=='on':
        odata=Orders.query.all()
        for odat in odata:
            cust=odat.Shipper
            if cust not in customerlist:
                customerlist.append(cust)

    customerlist.sort()


    return cache,err,leftscreen,docref,leftsize,today,now,doctxt,sdate,fdate,fyear,customerlist,thiscomp,clist
