from runmain import db
from models import OverSeas, Orders, Moving, People, Invoices, Income, Interchange, Bills
from flask import session, request
import datetime
import calendar
from viewfuncs import nonone, nononef, dollar, nodollar
from CCC_system_setup import scac

start= datetime.date(2019, 1, 1)
end= datetime.date(2019, 1, 31)
itemlist=[]
truckjobcontainers=[]
oceanjobcontainers=[]
jaycontainers=[]

d2last=0
feljobs=['Knight','Global','Hunt']
odata=Orders.query.filter((Orders.Date>=start) & (Orders.Date<=end)).filter(Orders.Driver.contains("Khoder")).order_by(Orders.Date).all()
for data in odata:
    patron=People.query.get(data.Bid)
    #print('For Job Order: ',data.Jo,' on Date: ',data.Date,' with Company ',patron.Company, 'using Container: ',data.Container)
    lda=Invoices.query.filter(Invoices.Jo==data.Jo).first()
    if lda is None:
        print('No Invoice Created for Job')
    else:
        total=lda.Total
        #try:
            #print('Amount Invoiced for on this Job: $',lda.Total)
        #except:
            #print('Need to fix Total on this Invoice')
        ldata=Invoices.query.filter(Invoices.Jo==data.Jo)
        for ldat in ldata:
            #print(ldat.Jo, ldat.Service, ldat.Qty, ldat.Ea, ldat.Amount, ldat.Total)

            feljob=0
            for job in feljobs:
                if job in patron.Company:
                    feljob=1

            if 'Line' in ldat.Service:
                print(data.Order)
                contractamt=float(ldat.Amount)
                if feljob==0:
                    paytojay=.85*contractamt
                else:
                    paytojay=.8*contractamt
                #print('Contract pay for this job is: $',paytojay)




            if 'Chassis' in ldat.Service:
                chassis=float(ldat.Qty)
                if 'Knight' in patron.Company:
                    chassis=chassis+2.0
                chassisfee=chassis*30
                payfromjay=chassisfee
                #print('Number of Chassis Days: ',chassis)
                #print('Deduction for Chassis Fees is: $',payfromjay)
            else:
                payfromjay=0.00

        netpay=paytojay-payfromjay
        #print('Net Pay for this Job is: $',netpay)

        container=data.Container
        booking=data.Booking
        ticket1=Interchange.query.filter(Interchange.Container==container).first()
        try:
            ticket2=Interchange.query.filter((Interchange.Container==container) & (Interchange.id != ticket1.id)).first()
        except:
            ticket2 is None

        if ticket1 is not None and ticket2 is not None:
            truckjobcontainers.append(container)
            date1=ticket1.Date
            date2=ticket2.Date
            if date1>date2:
                d1=date2
                d2=date1
            else:
                d1=date1
                d2=date2

            if d2last==d1:
                add=0
            else:
                add=1
            d2last=d2
            delta=d2-d1
            chassisdays=delta.days+add
            fromjay=chassisdays*30
            netpay=paytojay-fromjay
            #print (d1,' to ',d2, data.Jo, chassisdays)
            #print(' ')
        elif ticket1 is not None or ticket2 is not None:
            truckjobcontainers.append(container)
            print('Have mismatch in tickets on job')

    explain='Trucking for '+patron.Company
    itemlist.append([d1.strftime('%m/%d/%Y'),d2.strftime('%m/%d/%Y'),booking,container,explain,nodollar(paytojay),str(chassisdays),nodollar(fromjay),nodollar(netpay)])

odata=OverSeas.query.filter((OverSeas.PuDate>=start) & (OverSeas.PuDate<=end)).filter(OverSeas.Driver.contains("Khoder")).order_by(OverSeas.PuDate).all()
for data in odata:
    booking=data.Booking
    container=data.Container

    ticket1=Interchange.query.filter(Interchange.Container==container).first()
    if ticket1 is not None:
        driver1=ticket1.Driver
        yard1=ticket1.Chassis
    else:
        driver1='NotJay'
        yard1='NotJay'
    try:
        ticket2=Interchange.query.filter((Interchange.Container==container) & (Interchange.id != ticket1.id)).first()
        driver2=ticket2.Driver
        yard2=ticket2.Chassis
    except:
        ticket2 is None
        driver2='NotJay'
        yard2='NotJay'


    if driver1=='Hassan Khoder' and driver2=='Hassan Khoder':
        oceanjobcontainers.append(container)
        date1=ticket1.Date
        date2=ticket2.Date
        if date1>date2:
            d1=date2
            d2=date1
        else:
            d1=date1
            d2=date2

        if d2last==d1:
            add=0
        else:
            add=1
        d2last=d2
        delta=d2-d1
        chassisdays=delta.days+add
        #print (d1,' to ',d2, data.Jo, chassisdays)
        #print(' ')
        explain='Ocean Container Both Ways'
        fromjay=0
        netpay=500-fromjay
    elif driver1=='Hassan Khoder' or driver2=='Hassan Khoder':
        oceanjobcontainers.append(container)
        print('One-way job',container)
        if '7655' in container:
            print(data.id,container)
        if yard1=='Yard' or yard2=='Yard':
            explain='Ocean Container To/From Yard'
            fromjay=0
            netpay=50
        else:
            explain='Ocean Container One Way'
            fromjay=0
            netpay=250

    if driver1=='Hassan Khoder' or driver2=='Hassan Khoder':
        print(booking,container,explain)
        itemlist.append([d1.strftime('%m/%d/%Y'),d2.strftime('%m/%d/%Y'),booking,container,explain,nodollar(netpay),str(chassisdays),nodollar(fromjay),nodollar(netpay)])

pay=0
fromjay=0
netpay=0
paytojay=0


print('The truck job containers are:',truckjobcontainers)
print('The ocean job containers are:',oceanjobcontainers)
jobcontainers=truckjobcontainers+oceanjobcontainers

jaycontainers=[]
idata = db.session.query(Interchange.Container).distinct().filter((Interchange.Date>=start) & (Interchange.Date<=end))
for data in idata:
    idat=Interchange.query.filter(Interchange.Container==data.Container).first()
    container=idat.Container
    driver=idat.Driver
    if driver=="Hassan Khoder" and container not in jobcontainers:
        booking=idat.Release
        date1=idat.Date
        match=Interchange.query.filter((Interchange.Container==container) & (Interchange.id != idat.id)).first()

        if match is not None:
            driver2=match.Driver
            if driver2=="Hassan Khoder":
                # Matched Containers and Khoder is Driver for both
                date2=match.Date
                explain='Jay matched Containers In/Out'
                if date1>date2:
                    d1=date2
                    d2=date1
                else:
                    d1=date1
                    d2=date2
                delta=d2-d1
                chassisdays=delta.days
                #print (d1,' to ',d2, chassisdays)
                pay=0.00
                fromjay=chassisdays*30
                netpay=0-fromjay
                itemlist.append([d1.strftime('%m/%d/%Y'),d2.strftime('%m/%d/%Y'),booking,container,explain,nodollar(pay),str(chassisdays),nodollar(fromjay),nodollar(netpay)])
                jaycontainers.append(container)

allcompletes=jaycontainers+jobcontainers

idata = Interchange.query.filter((Interchange.Date>=start) & (Interchange.Date<=end)).all()
for data in idata:
    container=data.Container
    if container not in allcompletes and data.Driver=='Hassan Khoder':
        status=data.Status
        date1=data.Date
        booking=data.Release
        odat=Orders.query.filter(Orders.Container==container).first()
        if 'IO' in status or odat is not None:
            explain='Local Port Pull/Drop'
            pay=50.00
            itemlist.append([date1.strftime('%m/%d/%Y'),'nomatch',booking,container,explain,nodollar(pay),'0','0.00',nodollar(pay)])
        else:
            explain='Unmatched Ticket not FEL'
            pay=0.00
            itemlist.append([date1.strftime('%m/%d/%Y'),'nomatch',booking,container,explain,nodollar(pay),'0','0.00',nodollar(pay)])


#print(itemlist)
print(jobcontainers)
print(jaycontainers)
l1=len(itemlist)
total=0.00
for i in range(l1):
    newlist=itemlist[i]
    amount=float(newlist[8])
    total=total+amount

print(total)

bitemlist=[]
#Find expenses paid for Jay
bdata=FELBills.query.filter((FELBills.bDate>=start) & (FELBills.bDate<=end)).filter(FELBills.bClass=='JaysAuto').order_by(FELBills.bDate).all()
for data in bdata:
    print(data.bDate,data.Description,data.bAmount)
    bitemlist.append([data.bDate.strftime('%Y-%m-%d'),data.Description,data.bAmount])

btotal=0.00
l2=len(bitemlist)
for i in range(l2):
    newlist=bitemlist[i]
    amount=newlist[2]
    btotal=btotal+float(amount)

print(dollar(btotal))

nettotal=total-btotal
print(dollar(nettotal))

#Now lets print the report out
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.units import inch
from viewfuncs import nonone, nononef, nononestr, dollar, avg, comporname, fullname, address
import csv
import math


# All dates must begin in datetime format and will be converted to strings as required


file1=f'tmp/{scac}/data/jay.pdf'
today = datetime.datetime.today().strftime('%m/%d/%Y')
invodate = datetime.date.today().strftime('%m/%d/%Y')

billto=list(range(5))
billto[0]='First Eagle Logistics'
billto[1]='505 Hampton Park Blvd Unit O'
billto[2]='Capitol Heights, MD  20743'
billto[3]='301-516-3000'
billto[4]='info@firsteaglelogistics.com'

line2=['Start', 'Finish', 'Booking','Container','Summary','Gross','Days','Fees','NetP']


#___________________________________________________________


ltm=36
rtm=575
ctrall=310
left_ctr=170
right_ctr=480
dl=17.6
tdl=dl*2
hls=530
m1=hls-dl
m2=hls-2*dl
m3=hls-3*dl
m4=hls-4*dl
m5=hls-18*dl
m6=hls-23*dl
m7=hls-27*dl
n1=580
n2=n1-dl
n3=hls-27*dl

fulllinesat=[n1,n2,n3]
p1=ltm+50
p2=p1+50
p3=p2+80
p4=p3+70

p5=rtm-132

p7=rtm-100
p8=rtm-70
p9=rtm-40
sds1  =[p1,p2,p3,p4,p5,p7,p8,p9]

q1=ltm+180
q2=rtm-180
sds3=[q1,q2]
bump=2.5
tb=bump*2

c=canvas.Canvas(file1, pagesize=letter)
c.setLineWidth(1)

logo = "logo3.jpg"
c.drawImage(logo, 185, 680, mask='auto')

#Date and JO boxes
dateline=m1+8.2*dl
c.rect(rtm-150,m1+7*dl,150,2*dl,stroke=1,fill=0)
c.line(rtm-150,dateline,rtm,dateline)
c.line(rtm-75,m1+7*dl,rtm-75,m1+9*dl)

ctm=218
mtmp/data=dateline-3.5*dl
c.rect(ltm, dateline-4*dl,175,5*dl, stroke=1, fill=0)
level1=mtmp/data+3.5*dl
c.line(ltm,level1,ltm+175,level1)
c.drawString(ltm+bump*3,level1+bump*2,'Bill To')

for i in fulllinesat:
    c.line(ltm,i,rtm,i)
for k in sds1:
    c.line(k,n1,k,n2)
c.line(ltm,n1,ltm,n3)
c.line(rtm,n1,rtm,n3)


c.setFont('Helvetica-Bold',24,leading=None)
c.drawCentredString(rtm-75,dateline+1.5*dl,'Invoice')

c.setFont('Helvetica',12,leading=None)

c.drawCentredString(rtm-112.5,dateline+bump,'Date')
c.drawCentredString(rtm-37.7,dateline+bump,'Invoice #')

#Main Items Header
c.setFont('Helvetica-Bold',10,leading=None)
ctr=[avg(ltm,p1),avg(p1,p2),avg(p2,p3),avg(p3,p4),avg(p4,p5),avg(p5,p7),avg(p7,p8),avg(p8,p9),avg(p9,rtm)]
for j,i in enumerate(line2):
    c.drawCentredString(ctr[j],n2+tb,i)

#Main Items Listing
c.setFont('Helvetica',9,leading=None)
dh=dl*.6
l1=len(itemlist)
total=0.00
top = n2-dh
for k in range(l1):
    newlist=itemlist[k]
    for j,i in enumerate(newlist):
        if j==8:
            c.drawRightString(rtm-bump,top,i)
        elif j==7:
            c.drawRightString(p9,top,i)
        elif j==5:
            c.drawRightString(p7,top,i)
        elif j==4:
            c.drawString(p4,top,i)
        else:
            try:
                c.drawCentredString(ctr[j],top,i)
            except:
                c.drawCentredString(ctr[j],top,'53 Dry Van')
    top=top-dh
    amount=newlist[8]
    total=total+float(amount)
# Main items total
bot=top-dh
c.line(ltm,top,rtm,top)
c.line(ltm,bot,rtm,bot)
c.drawRightString(p8,bot+bump,'Work Subtotal')
c.drawRightString(rtm-bump,bot+bump,dollar(total))



top=bot-dh
bot=top-dh*1.2
c.line(ltm,top,rtm,top)
c.line(ltm,bot,rtm,bot)
line3=['Date','Bill Payments for Jays Auto Account', 'Amount']
c.setFont('Helvetica-Bold',10,leading=None)
ctr=[avg(ltm,p3),avg(p3,p7),avg(p7,rtm)]
# Items listing
c.drawCentredString(avg(p1,p2),bot+bump,'Date')
c.drawString(p3,bot+bump,'Bill Payments for Jays Auto Account')
c.drawRightString(rtm-bump,bot+bump,'Amount')

#print item performed list
c.setFont('Helvetica',9,leading=None)
top=bot-dh
billtot=0.0
l2=len(bitemlist)
for k in range(l2):
    a=bitemlist[k]
    c.drawCentredString(avg(p1,p2),top,a[0])
    c.drawString(p3,top,a[1])
    c.drawRightString(rtm-bump,top,a[2])
    top=top-dh
    amount=a[2]
    billtot=billtot+float(amount)
    total=total-float(amount)

# Bill items total
bot=top-dh*1.2
c.line(ltm,top,rtm,top)
c.line(ltm,bot,rtm,bot)
c.drawRightString(p8,bot+bump,'Bill Subtotal')
c.drawRightString(rtm-bump,bot+bump,dollar(billtot))

dh=12
ct=305

c.line(ltm,n3+dh*1.2,rtm,n3+dh*1.2)
bottomline=n3+bump
c.setFont('Helvetica-Bold',10,leading=None)
c.drawRightString(p8,bottomline,'Balance Due:')
c.drawRightString(rtm-bump,bottomline,dollar(total))

#_______________________________________________________________________
    #Insert data here
#_______________________________________________________________________

c.setFont('Helvetica',12,leading=None)

dh=13
top=level1-dh
lft=ltm+bump*3
for i in billto:
    c.drawString(lft,top,i)
    top=top-dh

x=avg(rtm-75,rtm)
y=dateline-dh-bump
c.drawCentredString(x,y,'JayBill')
x=avg(rtm-75,rtm-150)
c.drawCentredString(x,y,invodate)

drangestring='Date Range: '+start.strftime('%m/%d/%Y')+' to '+end.strftime('%m/%d/%Y')
c.drawRightString(rtm-bump,y-30,drangestring)



c.showPage()
c.save()
