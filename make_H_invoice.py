def main(odata, ldata, pdata1, cache, invodate, payment):
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
    from CCC_system_setup import bankdata, scac

    joborder = odata.Jo
    file1 = f'tmp/{scac}/data/vinvoice/INV'+joborder+'.pdf'
    file2 = f'tmp/{scac}/data/vinvoice/INV'+joborder+'c'+str(cache)+'.pdf'
    today = datetime.datetime.today().strftime('%m/%d/%Y')
    type = joborder[1]
    if invodate is None or invodate == 0:
        invodate = today
    else:
        invodate = invodate.strftime('%m/%d/%Y')

    def dollar(infloat):
        outstr = '$'+"%0.2f" % infloat
        return outstr

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

    if payment != 0:
        try:
            paydate = payment[2].strftime('%m/%d/%Y')
        except:
            paydate = payment[2]

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
    us[0] = 'HORIZON MOTORS INC'
    us[1] = '505 HAMPTON PARK BLVD UNIT N'
    us[2] = 'CAPITOL HEIGHTS MD  20743'
    us[3] = '301-909-1819  info@horizonmotors1.com'

    line1 = ['Quantity', 'Item Code', 'Description', 'Price Each', 'Amount']

    note = list(range(2))
    note[0] = '*Horizon Motors Auto License# X800013003087'
    note[1] = '*Hoizon Motors Car Sales Terms and Conditions'

    lab1 = 'Balance Due'
    lab2 = 'Add $39.00 for all international wires'

    nonote, bank = bankdata('HC')

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
    m5 = hls-18*dl
    m6 = hls-23*dl
    m7 = hls-27*dl
    fulllinesat = [m3, m4, m5, m6, m7]
    p1 = ltm+87
    p2 = ltm+180
    p3 = ctrall-25
    p4 = rtm-220
    p5 = rtm-120
    sds1 = [p1, p2, p3, p4, p5]
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

    c = canvas.Canvas(file2, pagesize=letter)
    c.setLineWidth(1)

    logo = "tmp/felpics/hm.jpg"
    c.drawImage(logo, 220, 580, mask='auto', width=180, preserveAspectRatio=True)

    # Date and JO boxes
    dateline = m1+8.2*dl
    c.rect(rtm-150, m1+7*dl, 150, 2*dl, stroke=1, fill=0)
    c.line(rtm-150, dateline, rtm, dateline)
    c.line(rtm-75, m1+7*dl, rtm-75, m1+9*dl)

    # Address boxes
    ctm = 218
    c.rect(ltm, m1+dl, 250, 5*dl, stroke=1, fill=0)
    #c.rect(ctm, m1+dl,175,5*dl, stroke=1, fill=0)
    #c.rect(rtm-175, m1+dl,175,5*dl, stroke=1, fill=0)
    level1 = m1+5*dl
    c.line(ltm, level1, ltm+250, level1)
    # c.line(ctm,level1,ctm+175,level1)
    # c.line(rtm-175,level1,rtm,level1)

    for i in fulllinesat:
        c.line(ltm, i, rtm, i)
    # for k in sds1:
        # c.line(k,m1,k,m3)
    for l in sds2:
        c.line(l, m3, l, m5)
    for m in sds3:
        c.line(m, m6, m, m7)
    c.line(ltm, m3, ltm, m7)
    c.line(rtm, m3, rtm, m7)
    h1 = avg(m6, m7)-3
    c.line(q2, h1, rtm, h1)

    c.setFont('Helvetica-Bold', 24, leading=None)
    c.drawCentredString(rtm-75, dateline+1.5*dl, 'Invoice')

    c.setFont('Helvetica', 12, leading=None)

    c.drawCentredString(rtm-112.5, dateline+bump, 'Date')
    c.drawCentredString(rtm-37.7, dateline+bump, 'Invoice #')

    c.drawString(ltm+bump*3, m1+5*dl+bump*2, 'Bill To')

#    ctr=[avg(ltm,p1),avg(p1,p2),avg(p2,p3),avg(p3,p4),avg(p4,p5),avg(p5,rtm)]
#    for j,i in enumerate(line1):
#        c.drawCentredString(ctr[j],m2+tb,i)

    ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n3, n4), avg(n4, rtm)]
    for j, i in enumerate(line1):
        c.drawCentredString(ctr[j], m4+tb, i)

    dh = 12
    ct = 305
    top = m6-1.5*dh
    for i in bank:
        c.drawCentredString(ct, top, i)
        top = top-dh

    top = m1+9*dl-5
    for i in us:
        c.drawString(ltm+bump, top, i)
        top = top-dh

    bottomline = m6-23
    c.setFont('Helvetica-Bold', 12, leading=None)
    c.drawString(q2+tb, bottomline, 'Balance Due:')

    c.setFont('Helvetica', 10, leading=None)
    c.drawCentredString(avg(q2, rtm), m7+12, 'Add $39.00 for all international wires')

    c.setFont('Times-Roman', 9, leading=None)
    j = 0
    dh = 9.95
    top = m5-dh
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
    c.drawCentredString(x, y, invodate)

    c.setFont('Helvetica', 9, leading=None)

    total = 0
    top = m4-dh
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

        c.drawString(n2+tb, top, line5)

        ctr = [n4-tb*2, rtm-tb*2]
        for j, i in enumerate(line6):
            c.drawRightString(ctr[j], top, dollar(i))

        top = top-dh

    if payment != 0:
        c.setFont('Helvetica-Bold', 18, leading=None)
        c.drawCentredString(ct, top-2*dh, 'Payment Received')

    if payment != 0:
        c.setFont('Helvetica-Bold', 12, leading=None)
        try:
            thispay = float(payment[0])
        except:
            thispay = 0.00
        top = top-4*dh
        try:
            c.drawString(n2+bump, top, 'Your payment of ' +
                         dollar(float(payment[0]))+', Ref No. '+payment[1])
        except:
            c.drawString(ct, top, 'There is no payment data as of yet')
        try:
            c.drawString(n2+bump, top-dh, 'was applied on ' + paydate)
        except:
            c.drawString(ct, top-dh, 'There is a problem with the date')

        else:
            thispay = 0.00

        total = total-thispay

    c.setFont('Helvetica-Bold', 12, leading=None)
    c.drawRightString(rtm-tb*2, bottomline, dollar(total))

    c.showPage()
    c.save()
    #
    # Now make a cache copy
    shutil.copy(file2, file1)


if __name__ == "__main__":
    main()
