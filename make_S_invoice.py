def main(odata, ldata, pdata1, invojo, involine, paidline, refline, balline, invodate, cache, payment):
    # pdata1:Bid (Bill To)
    # pdata2:Lid (Load At)
    # pdata3:Did (Delv To)

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.pagesizes import landscape
    from reportlab.platypus import Image
    from reportlab.lib.units import inch
    import csv
    import math
    import datetime
    import shutil
    from viewfuncs import sdiff, sadd, dollar, nodollar, nononef
    from CCC_system_setup import myoslist, addpath, bankdata

    joborder = invojo
    file1 = addpath('tmp/data/vinvoice/INV'+joborder+'.pdf')
    file2 = addpath('tmp/data/vinvoice/INV'+joborder+'c'+str(cache)+'.pdf')
    type = joborder[1]

    #today = datetime.datetime.today().strftime('%m/%d/%Y')
   # if invodate is None or invodate==0:
    # invodate=today
    # else:
    try:
        invodate = invodate.strftime('%m/%d/%Y')
    except:
        err = 'ivodate already a string'

    billhistory = involine
    payhistory = paidline
    openbalance = balline
    custref = refline
    pyopenbal = odata.BalFwd
    pyopenbal = nononef(pyopenbal)
    pyopenbal = nodollar(pyopenbal)

    a = pyopenbal
    for j, i in enumerate(openbalance):
        if billhistory[j] != '' or payhistory[j] != '':
            openbalance[j] = sadd(a, i)
            a = openbalance[j]
            if j > 0:
                b = openbalance[j-1]
            else:
                b = pyopenbal

    # 'a' is the last open balance and should be added to the bill
    try:
        prevbal = float(b)
    except:
        prevbal = 0.00

    def avg(in1, in2):
        out = (in1+in2)/2
        return out

    def comporname(company, name):
        if company is None or company == '':
            nameout = name
        else:
            if len(company) < 4:
                nameout = name
            else:
                nameout = company
        return nameout

    def fullname(first, middle, last):
        if first is not None:
            nameout = first
        else:
            nameout = ''
        if middle is not None:
            nameout = nameout+' '+middle
        if last is not None:
            nameout = nameout+' '+last
        if len(nameout) > 55:
            nameout = first + ' ' + last
        return nameout

    def address(addr1, addr2, addr3):
        street = addr1
        if addr3 is None or addr3 == '':
            cityst = addr2
        else:
            if len(addr3) < 5:
                cityst = addr2
        if addr2 is None or addr2 == '':
            cityst = addr3
            if len(addr2) < 3:
                cityst = addr3
        if addr2 and addr3:
            if len(addr2) > 3 and len(addr3) > 3:
                street = addr1 + ' ' + addr2
                cityst = addr3
        return street, cityst

    def nononestr(input):
        if input is None or input == 'None':
            input = ''
        return input

    def nonone(input):
        if input is None:
            input = 0
        return input

    billto = list(range(5))
    if pdata1 is not None:
        billto[0] = comporname(pdata1.Company, fullname(pdata1.First, pdata1.Middle, pdata1.Last))
        billto[1] = nononestr(pdata1.Addr1)
        billto[2] = nononestr(pdata1.Addr2)
        billto[3] = nononestr(pdata1.Telephone)
        billto[4] = nononestr(pdata1.Email)
    else:
        for i in range(5):
            billto[i] = ' '

    us = list(range(4))
    us[0] = 'FIRST EAGLE LOGISTICS INC'
    us[1] = '505 HAMPTON PARK BLVD UNIT O'
    us[2] = 'CAPITOL HEIGHTS MD  20743'
    us[3] = '301-516-3000  info@firsteaglelogistics.com'

    line1 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    line2 = ['Quantity', 'Item Code', 'Description', 'Price Each', 'Amount']
    line3 = billhistory
    line41 = payhistory
    line42 = custref
    line5 = openbalance

    note = list(range(3))
    note[0] = '*All invoices that are 15 days past due will incurr a $35.00 late fee.'
    note[1] = '*After 60 days an additional late fee will be assessed in the amount of $100.00.'
    note[2] = '*If your account reaches 90 days past due it will be submitted for collection.'

    lab1 = 'Balance Due'
    lab2 = 'Add $39.00 for all international wires'

    nonote, bank = bankdata('FC')

# ___________________________________________________________

    ltm = 36
    rtm = 575
    ctrall = 310
    left_ctr = 170
    right_ctr = 480
    dl = 17.6
    tdl = dl*2
    hls = 530
    m1 = hls-dl
    m2 = hls-2*dl
    m3 = hls-3*dl
    m4 = hls-4*dl
    m5 = hls-5*dl
    m61 = hls-6*dl
    m62 = hls-7*dl
    m63 = hls-8*dl

    m7 = hls-20*dl
    m8 = hls-23*dl
    m9 = hls-27*dl
    fulllinesat = [m1, m2, m3, m4, m5, m61, m62, m63, m7, m8, m9]

    p = [0]*13
    p[0] = ltm+87
    for i in range(1, 13):
        p[i] = p[i-1]+37.7

    n1 = ltm+58
    n2 = ltm+128
    n3 = rtm-140
    n4 = rtm-70
    sds2 = [n1, n2, n3, n4]
    q1 = ltm+180
    q2 = rtm-180
    sds3 = [q1, q2]
    bump = 2.5
    tb = bump*2

    c = canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)

    logo = addpath("tmp/felpics/logo3.jpg")
    c.drawImage(logo, 185, 680, mask='auto')

    # Date and JO boxes
    dateline = m1+8.2*dl
    c.rect(rtm-150, m1+7*dl, 150, 2*dl, stroke=1, fill=0)
    c.line(rtm-150, dateline, rtm, dateline)
    c.line(rtm-75, m1+7*dl, rtm-75, m1+9*dl)

    if type == 'S':
        # Address boxes
        ctm = 218
        c.rect(ltm, m1+dl, 175, 5*dl, stroke=1, fill=0)
        #c.rect(ctm, m1+dl,175,5*dl, stroke=1, fill=0)
        #c.rect(rtm-175, m1+dl,175,5*dl, stroke=1, fill=0)
        level1 = m1+5*dl
        c.line(ltm, level1, ltm+175, level1)
        # c.line(ctm,level1,ctm+175,level1)
        # c.line(rtm-175,level1,rtm,level1)

    for i in fulllinesat:
        c.line(ltm, i, rtm, i)
    for k in p[0:12]:
        c.line(k, m1, k, m61)
    for l in sds2:
        c.line(l, m62, l, m7)
    for m in sds3:
        c.line(m, m8, m, m9)
    c.line(ltm, m1, ltm, m9)
    c.line(rtm, m1, rtm, m9)
    h1 = avg(m8, m9)-3
    c.line(q2, h1, rtm, h1)

    c.setFont('Helvetica-Bold', 24, leading=None)
    c.drawCentredString(rtm-75, dateline+1.5*dl, 'Invoice')
    if payment != 0:
        c.setFont('Helvetica-Bold', 18, leading=None)
        c.drawCentredString(rtm-75, dateline-50, 'Payment Received')

    c.setFont('Helvetica', 12, leading=None)

    c.drawCentredString(rtm-112.5, dateline+bump, 'Date')
    c.drawCentredString(rtm-37.7, dateline+bump, 'Invoice #')

    c.drawString(ltm+bump*3, m1+5*dl+bump*2, 'Bill To')
    # c.drawString(ctm+bump*3,m1+5*dl+bump*2,'Load At')
    # c.drawString(rtm-170+bump*2,m1+5*dl+bump*2,'Delv To')

    dh = 12
    ct = 305

    if payment != 0:
        try:
            thispay = float(payment[0])
        except:
            thispay = 0.00
        top = m1+4*dl-5
        try:
            c.drawString(ct, top, 'Your payment of '+payment[0]+', Ref No. '+payment[1])
            c.drawString(ct, top-dh, 'was applied on '+payment[2])
        except:
            c.drawString(ct, top, 'There is no payment data as of yet')
    else:
        thispay = 0.00

    c.drawString(ct, m1+dl, 'Balance Fwd from 2018: $'+pyopenbal)

    j = 0
    ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n3, n4), avg(n4, rtm)]
    for i in line2:
        c.drawCentredString(ctr[j], m63+tb, i)
        j = j+1

    top = m8-1.5*dh
    for i in bank:
        c.drawCentredString(ct, top, i)
        top = top-dh

    top = m1+9*dl-5
    for i in us:
        c.drawString(ltm+bump, top, i)
        top = top-dh

    bottomline = m8-23
    c.setFont('Helvetica-Bold', 12, leading=None)
    c.drawString(q2+tb, bottomline, 'Balance Due:')

    c.setFont('Helvetica', 10, leading=None)
    c.drawCentredString(avg(q2, rtm), m9+12, 'Add $39.00 for all international wires')

    c.setFont('Times-Roman', 9, leading=None)
    j = 0
    dh = 9.95
    top = m7-dh
    for i in note:
        c.drawString(ltm+tb, top, note[j])
        j = j+1
        top = top-dh


# _______________________________________________________________________
    # Insert data here
# _______________________________________________________________________

    c.setFont('Helvetica', 12, leading=None)

    dh = 13
    top = level1-dh
    lft = ltm+bump*3
    for i in billto:
        c.drawString(lft, top, i)
        top = top-dh

    x = avg(rtm-75, rtm)
    y = dateline-dh-bump
    c.drawCentredString(x, y, joborder)
    x = avg(rtm-75, rtm-150)
    try:
        c.drawCentredString(x, y, invodate)
    except:
        err = 'Date not set yet'

    c.setFont('Helvetica', 9, leading=None)
    c.drawCentredString(avg(ltm, p[0]), m2+tb, '2019 by Month:')
    c.drawCentredString(avg(ltm, p[0]), m3+tb, 'Bill History')
    c.drawCentredString(avg(ltm, p[0]), m4+tb, 'Pay History')
    c.drawCentredString(avg(ltm, p[0]), m5+tb, 'Cust Ref No.')
    c.drawCentredString(avg(ltm, p[0]), m61+tb, 'Open Balances')
    for j, i in enumerate(line1):
        ctr = avg(p[j], p[j+1])
        c.drawCentredString(ctr, m2+tb, i)
        c.drawCentredString(ctr, m3+tb, line3[j])
        c.drawCentredString(ctr, m4+tb, line41[j])
        c.drawCentredString(ctr, m5+tb, line42[j])
        c.drawCentredString(ctr, m61+tb, line5[j])

    total = 0
    top = m63-dh
    for data in ldata:
        qty = int(nonone(data.Qty))
        each = float(nonone(data.Ea))
        subtotal = qty*each
        total = total+subtotal
        line4 = [str(qty), data.Service]
        line5 = nononestr(data.Description)
        line6 = [each, subtotal]

        ctr = [avg(ltm, n1), avg(n1, n2)]
        for j, i in enumerate(line4):
            c.drawCentredString(ctr[j], top, i)

        ctr = [n4-tb*2, rtm-tb*2]
        for j, i in enumerate(line6):
            c.drawRightString(ctr[j], top, dollar(i))

        line5a = line5.splitlines()
        for line in line5a:
            c.drawString(n2+tb, top, line)
            top = top-dh

        top = top-dh

    if prevbal > 0:
        c.drawString(n2+tb, top, 'Open balance from previous month')
        c.drawRightString(rtm-tb*2, top, dollar(prevbal))

    total = total+prevbal-thispay

    c.drawRightString(rtm-tb*2, bottomline, dollar(total))

    c.showPage()
    c.save()
    #
    # Now make a cache copy
    shutil.copy(file1, file2)


if __name__ == "__main__":
    main(odata, ldata, pdata1, idate, invojo, involine, paidline, refline, balline, cache, payment)
