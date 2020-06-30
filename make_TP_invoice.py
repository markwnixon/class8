def main(file1, keydata, grandtotal, pdata1, date1, date2):
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
    from viewfuncs import parseline
    from CCC_system_setup import addpath, bankdata

    file1 = addpath(file1)
    print(file1)

    date1 = date1.strftime('%m/%d/%Y')
    date2 = date2.strftime('%m/%d/%Y')
# ___________________________________________________________

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
            output = ' '
        else:
            output = input
        return output

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


    line2 = ['Invoice', 'Booking', 'Container', 'Description', 'Amount']

    qnote, note, bank, us, lab, logoi = bankdata('FC')

    ltm = 36
    rtm = 575
    ctrall = 310
    left_ctr = 170
    right_ctr = 480
    dl = 17.6
    tdl = dl*2

    hls = 530
   # m1=hls-dl
   # m2=hls-2*dl
    m3 = hls-dl
    m4 = hls-2*dl
    m5 = hls-18*dl
    m6 = hls-23*dl
    m7 = hls-27*dl

    fulllinesat = [m3, m4, m5, m6, m7]
    p1 = ltm+87
    p2 = ltm+180
    p3 = ctrall
    p4 = rtm-180
    p5 = rtm-100
   # sds1   =[p1,p2,p3,p4,p5]
    n1 = ltm+60
    n2 = ltm+150
    n3 = ltm+240
    n4 = rtm-70
    sds2 = [n1, n2, n3, n4]
    q1 = ltm+180
    q2 = rtm-180
    sds3 = [q1, q2]
    bump = 2.5
    tb = bump*2
    bottomline = m6-23

    print('file1 is',file1)
    c = canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)

    #logo = addpath("static/pics/onestop.png")
    c.drawImage(logoi, 185, 680, mask='auto')

    # Date and JO boxes
    dateline = m3+8.2*dl
    c.rect(rtm-150, m3+7*dl, 150, 2*dl, stroke=1, fill=0)
    c.line(rtm-150, dateline, rtm, dateline)
    # c.line(rtm-75,m3+7*dl,rtm-75,m3+8*dl)
    c.drawCentredString(rtm-75, dateline-13-bump, 'to')

    ctm = 218
    c.rect(ltm, m3+dl, 175, 5*dl, stroke=1, fill=0)
    #c.rect(ctm, m3+dl,175,5*dl, stroke=1, fill=0)
    #c.rect(rtm-175, m3+dl,175,5*dl, stroke=1, fill=0)
    level1 = m3+5*dl
    c.line(ltm, level1, ltm+175, level1)
    # c.line(ctm,level1,ctm+175,level1)
    # c.line(rtm-175,level1,rtm,level1)

    # All full horizontal lines
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

    h1 = m6-3
    c.line(q2, h1, rtm, h1)

    c.setFont('Helvetica-Bold', 24, leading=None)
    c.drawCentredString(rtm-75, dateline+3*dl, 'Invoice')
    c.drawCentredString(rtm-75, dateline+1.5*dl, 'Summary')

    c.setFont('Helvetica', 12, leading=None)

    c.drawCentredString(rtm-112.5, dateline+bump, 'Date')
    c.drawCentredString(rtm-37.7, dateline+bump, 'Range')

    c.drawString(ltm+bump*3, m3+5*dl+bump*2, 'Bill To')
    #c.drawString(ctm+bump*3,m1+5*dl+bump*2,'Load At')
    #c.drawString(rtm-170+bump*2,m1+5*dl+bump*2,'Delv To')
    dh = 13
    top = level1-dh
    lft = ltm+bump*3
    c.setFont('Helvetica', 10, leading=None)
    for i in billto:
        c.drawString(lft, top, i)
        top = top-dh
    c.setFont('Helvetica', 12, leading=None)

    x = avg(rtm-75, rtm)+3
    y = dateline-dh-bump
    c.drawCentredString(x, y, date2)
    x = avg(rtm-75, rtm-150)-3
    c.drawCentredString(x, y, date1)

    c.drawRightString(rtm-tb*2, bottomline, dollar(grandtotal))

    ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n3, n4), avg(n4, rtm)]
    for j, i in enumerate(line2):
        c.drawCentredString(ctr[j], m4+tb, i)

    c.setFont('Helvetica', 10, leading=None)
    ctr = [avg(ltm, n1), avg(n1, n2), avg(n2, n3), avg(n4, rtm), avg(n3, n4)]
    top = m4-dl
    for k, data in enumerate(keydata):
        dataline = keydata[k]
        print(dataline)
        for j, i in enumerate(dataline):
            if j == 4:
                dlen = len(i)
                if dlen > 35:
                    pline = parseline(i, 32)
                    for myline in pline:
                        if 'STORE' in myline: myline = 'WAREHOUSE STORAGE'
                        if 'None' in myline: myline = ''
                        if 'TBD' in myline: myline = ''
                        c.drawString(n3+5, top, myline)
                        top = top-.6*dl
                else:
                    c.drawString(n3+5, top, i)
                    top = top - .6 * dl
            else:
                if 'None' in str(i): i = ''
                if 'TBD' in str(i): i = ''
                c.drawCentredString(ctr[j], top, str(i))
        top = top-.6*dl

    c.setFont('Helvetica', 12, leading=None)
    dh = 12
    ct = 305
    top = m6-1.5*dh
    for i in bank:
        c.drawCentredString(ct, top, i)
        top = top-dh

    top = m3+9*dl-5
    for i in us:
        c.drawString(ltm+bump, top, i)
        top = top-dh

    c.setFont('Helvetica-Bold', 12, leading=None)
    c.drawString(q2+tb, bottomline, 'Balance Due:')

    c.setFont('Helvetica', 10, leading=None)
    c.drawCentredString(avg(q2, rtm), m7+12, 'Add $39.00 for all international wires')

    c.setFont('Times-Roman', 9, leading=None)

    dh = 9.95
    top = m5-dh
    for j, i in enumerate(note):
        c.drawString(ltm+tb, top, note[j])
        top = top-dh

    c.showPage()
    c.save()
    #
    # Now make a cache copy
    # shutil.copy(file1,file2)


if __name__ == "__main__":
    main()
