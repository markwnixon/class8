def makeTmanifest(odata, pdata1, pdata2, pdata3, tdata, cache):
    #pdata1:Bid (Bill To)
    #pdata2:Lid (Load At)
    #pdata3:Did (Delv To)

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.pagesizes import landscape
    from reportlab.platypus import Image
    from reportlab.lib.units import inch
    import csv
    import math
    import datetime
    import shutil
    from CCC_system_setup import scac

    joborder=odata.Jo
    file1=f'tmp/{scac}/data/vmanifest/Manifest'+joborder+'.pdf'
    file2=f'tmp/{scac}/data/vmanifest/Manifest'+joborder+'c'+str(cache)+'.pdf'
    today = datetime.datetime.today().strftime('%m/%d/%Y')
    sigdate = request.values.get('sigdate')
    type=joborder[1]
    if invodate is None or invodate==0:
        invodate=today
    else:
        invodate = invodate.strftime('%m/%d/%Y')



    def dollar(infloat):
        outstr='$'+"%0.2f" % infloat
        return outstr


    def avg(in1,in2):
        out=(in1+in2)/2
        return out

    def comporname(company,name):
        if company is None or company=='':
            nameout=name
        else:
            if len(company)<4:
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
            input=''
        return input

    def nonone(input):
        if input is None:
            input=0
        return input

    billto=list(range(5))
    if pdata1 is not None:
        billto[0]=comporname(pdata1.Company, fullname(pdata1.First, pdata1.Middle, pdata1.Last))
        billto[1]=nononestr(pdata1.Addr1)
        billto[2]=nononestr(pdata1.Addr2)
        billto[3]=nononestr(pdata1.Telephone)
        billto[4]=nononestr(pdata1.Email)
    else:
        for i in range(5):
            billto[i]=' '

    loadat=list(range(5))
    if pdata2 is not None:
        loadat[0]=comporname(pdata2.Company, fullname(pdata2.First, pdata2.Middle, pdata2.Last))
        loadat[1]=nononestr(pdata2.Addr1)
        loadat[2]=nononestr(pdata2.Addr2)
        loadat[3]=nononestr(pdata2.Telephone)
        loadat[4]=nononestr(pdata2.Email)
    else:
        for i in range(5):
            loadat[i]=' '

    shipto=list(range(5))
    if pdata3 is not None:
        shipto[0]=comporname(pdata3.Company, fullname(pdata3.First, pdata3.Middle, pdata3.Last))
        shipto[1]=nononestr(pdata3.Addr1)
        shipto[2]=nononestr(pdata3.Addr2)
        shipto[3]=nononestr(pdata3.Telephone)
        shipto[4]=nononestr(pdata3.Email)
    else:
        for i in range(5):
            shipto[i]=' '

    us=list(range(4))
    us[0]='FIRST EAGLE LOGISTICS INC'
    us[1]='505 HAMPTON PARK BLVD UNIT O'
    us[2]='CAPITOL HEIGHTS MD  20743'
    us[3]='301-516-3000  info@firsteaglelogistics.com'


    line1=['Booking #', 'Terms', 'Load Appt', 'Load Finish', 'Chassis No.', 'Container No.']
    line2=['Quantity', 'Item Code', 'Description', 'Price Each', 'Amount']
    chassis=' '
    time1=nononestr(odata.Time)
    time2=nononestr(odata.Time2)
    if 'Knight' in billto[0]:
        due='Due within 21 days'
    else:
        due='Due Upon Receipt'
    line3=[odata.Booking, due, time1, time2, chassis, odata.Container]

    note=list(range(8))
    note[0]='*All containers are subject to inspection by US Customs. Any charges incurred due to delays/inspection by customs are exporters responsibility.'
    note[1]='*First Eagle Logistics will not be liable for any cost/or delays occuring due to intervention of US Customs.'
    note[2]='*Dates for arrivals and departures are local.'
    note[3]='*Dates, times, and estimates are given without any gurantee and are subject to change without prior notice.'
    note[4]='*First Eagle Logistics is not responsible for any changes implemented by the shipping lines.'
    note[5]='*All invoices that are 15 days past due will incurr a $35.00 late fee.'
    note[6]='*After 60 days an additoinal late fee will be assessed in the amount of $100.00.'
    note[7]='*If your account reaches 90 days past due it will be submitted for collection.'

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
    fulllinesat=[m1, m2, m3, m4, m5, m6, m7]
    p1=ltm+87
    p2=ltm+180
    p3=ctrall-25
    p4=rtm-220
    p5=rtm-120
    sds1   =[p1,p2,p3,p4,p5]
    n1=ltm+58
    n2=ltm+128
    n3=rtm-140
    n4=rtm-70
    sds2    =[n1,n2,n3,n4]
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


    #Address boxes
    ctm=218
    c.rect(ltm, m1+dl,175,5*dl, stroke=1, fill=0)
    c.rect(ctm, m1+dl,175,5*dl, stroke=1, fill=0)
    c.rect(rtm-175, m1+dl,175,5*dl, stroke=1, fill=0)
    level1=m1+5*dl
    c.line(ltm,level1,ltm+175,level1)
    c.line(ctm,level1,ctm+175,level1)
    c.line(rtm-175,level1,rtm,level1)

    for i in fulllinesat:
        c.line(ltm,i,rtm,i)
    for k in sds1:
        c.line(k,m1,k,m3)
    for l in sds2:
        c.line(l,m3,l,m5)
    for m in sds3:
        c.line(m,m6,m,m7)
    c.line(ltm,m1,ltm,m7)
    c.line(rtm,m1,rtm,m7)
    h1=avg(m6,m7)-3
    c.line(q2,h1,rtm,h1)

    c.setFont('Helvetica-Bold',24,leading=None)
    c.drawCentredString(rtm-75,dateline+1.5*dl,'Invoice')

    c.setFont('Helvetica',12,leading=None)

    c.drawCentredString(rtm-112.5,dateline+bump,'Date')
    c.drawCentredString(rtm-37.7,dateline+bump,'Invoice #')


    c.drawString(ltm+bump*3,m1+5*dl+bump*2,'Bill To')
    c.drawString(ctm+bump*3,m1+5*dl+bump*2,'Load At')
    c.drawString(rtm-170+bump*2,m1+5*dl+bump*2,'Delv To')

    j=0
    for i in line1:
        ctr=[avg(ltm,p1),avg(p1,p2),avg(p2,p3),avg(p3,p4),avg(p4,p5),avg(p5,rtm)]
        c.drawCentredString(ctr[j],m2+tb,i)
        j=j+1

    j=0
    for i in line2:
        ctr=[avg(ltm,n1),avg(n1,n2),avg(n2,n3),avg(n3,n4),avg(n4,rtm)]
        c.drawCentredString(ctr[j],m4+tb,i)
        j=j+1

    dh=12
    ct=305

    top=m1+9*dl-5
    for i in us:
        c.drawString(ltm+bump,top,i)
        top=top-dh

    bottomline=m6-23
    c.setFont('Helvetica-Bold',12,leading=None)
    c.drawString(q2+tb,bottomline,'Balance Due:')

    c.setFont('Times-Roman',9,leading=None)
    j=0
    dh=9.95
    top=m5-dh
    for i in note:
        c.drawString(ltm+tb,top,note[j])
        j=j+1
        top=top-dh



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

    top=level1-dh
    lft=ctm+bump*3
    for i in loadat:
        c.drawString(lft,top,i)
        top=top-dh

    top=level1-dh
    lft=rtm-175+bump*3
    for i in shipto:
        c.drawString(lft,top,i)
        top=top-dh

    x=avg(rtm-75,rtm)
    y=dateline-dh-bump
    c.drawCentredString(x,y,joborder)
    x=avg(rtm-75,rtm-150)
    c.drawCentredString(x,y,sigdate)

    c.setFont('Helvetica',9,leading=None)

    j=0
    for i in line3:
        ctr=[avg(ltm,p1),avg(p1,p2),avg(p2,p3),avg(p3,p4),avg(p4,p5),avg(p5,rtm)]
        c.drawCentredString(ctr[j],m3+tb,i)
        j=j+1

    total=0
    top=m4-dh

    c.drawRightString(rtm-tb*2,bottomline,dollar(total))

    c.showPage()
    c.save()
    #
    #Now make a cache copy
    shutil.copy(file1,file2)
    return file2
