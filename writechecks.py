from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
import csv
import math
import datetime
import shutil
from viewfuncs import dollar
from CCC_system_setup import addpath, scac, companydata

def getzip(addr):
    items = addr.split()
    zip = items[-1]
    if len(zip)==5 or len(zip)==10:
        return zip
    else:
        return 0


def writechecks(bdat, pdat, file1, sbdata, links, style):

    today = datetime.datetime.today().strftime('%m/%d/%Y')
    nbills = 1
    file1 = addpath(file1)

    if links == 0:
        amt = bdat.pAmount
        amt = amt.replace(',', '')
        amount = float(amt)
    else:
        amt = bdat.pMulti
        amt = amt.replace(',', '')
        amount = float(amt)

    #billno = 'Bk:'+bdat.bCat
    billno = bdat.Jo

    # Create the Check Date:
    billdate = bdat.pDate
    print(billdate)
    try:
        datestr = billdate.strftime('%m/%d/%Y')
    except:
        datestr = datetime.datetime.today().strftime('%m/%d/%Y')

    if bdat.Memo is None:
        memo = ' '
    else:
        memo = bdat.Memo

    if bdat.Description is None:
        desc = ' '
    else:
        desc = bdat.Description

    payref = bdat.Ref
    # Check to see if we have the required data to make an invoice:
    company = pdat.Company
    addr1 = pdat.Addr1
    addr2 = pdat.Addr2
    email = pdat.Email
    phone = pdat.Telephone

    payee = company

    amount_num = "{:.2f}".format(amount)
    # amount_num=145.23
    bank = bdat.pAccount

    type = bdat.bType

    if links != 0:
        memo = ''
        nbills = 0
        for sb in sbdata:
            nbills = nbills+1
            if len(memo) > 45:
                memo = memo+'\n'
            memo = memo+sb.Memo+', '

        lm = len(memo)
        memo = memo[0:lm-2]
        memo = 'Payment for multiple references:\n'+memo

    one = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    tenp = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tenp2 = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def avg(in1, in2):
        out = (in1+in2)/2
        return out

    def once(num):
        one = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        word = ''
        word = one[int(num)]
        word = word.strip()
        return word

    def ten(num):
        tenp = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tenp2 = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        word = ''
        if num[0] == '1':
            word = tenp[int(num[1])]
        else:
            text = once(num[1])
            word = tenp2[int(num[0])]
            word = word + "-" + text
        word = word.strip()
        return word

    def hundred(num):
        one = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        word = ''
        text = ten(num[1:])
        word = one[int(num[0])]
        if num[0] != '0':
            word = word + "-Hundred "
        word = word + text
        word = word.strip()
        return word

    def thousand(num):
        word = ''
        pref = ''
        text = ''
        length = len(num)
        if length == 6:
            text = hundred(num[3:])
            pref = hundred(num[:3])
        if length == 5:
            text = hundred(num[2:])
            pref = ten(num[:2])
        if length == 4:
            text = hundred(num[1:])
            word = one[int(num[0])]
        if num[0] != '0' or num[1] != '0' or num[2] != '0':
            word = word + "-Thousand "
        word = word + text
        if length == 6 or length == 5:
            word = pref + word
        word = word.strip()
        return word

    def million(num):
        word = ''
        pref = ''
        text = ''
        length = len(num)
        if length == 9:
            text = thousand(num[3:])
            pref = hundred(num[:3])
        if length == 8:
            text = thousand(num[2:])
            pref = ten(num[:2])
        if length == 7:
            text = thousand(num[1:])
            word = one[int(num[0])]
        if num[0] != '0' or num[1] != '0' or num[2] != '0':
            word = word + " Million "
        word = word + text
        if length == 9 or length == 8:
            word = pref + word
        word = word.strip()
        return word


    val1 = float(amount_num)
    val2 = math.floor(val1)
    print(val2)
    val3 = val1-val2
    val3 = round(val3*100)
    print(val3)
    a = str(val2)
    leng = len(a)
    if leng == 1:
        if a == '0':
            num = 'Zero'
        else:
            num = once(a)
    if leng == 2:
        num = ten(a)
    if leng == 3:
        num = hundred(a)
    if leng > 3 and leng < 7:
        num = thousand(a)
    if leng > 6 and leng < 10:
        num = million(a)

    lnum = len(num)
    # print(num[lnum-1])
    if num[lnum-1] == '-':
        num = num[0:lnum-1]

    tval3 = "{0:0=2d}".format(val3)
    amount_text = num + ' and ' + tval3 + '/100 '
    # print(amount_text)

    # We need to add '*******' to back of this enough to fill up the rest of the block
    atlen = len(amount_text)
    # Guess that we need 120 chars total
    atremain = 90-atlen
    b = '*'
    for i in range(atremain):
        b = b+'*'

    # print(atlen,atremain,b)
    amount_text = amount_text+b
    # print(amount_text)

    c = canvas.Canvas(file1,  pagesize=letter)
    c.setFont('Helvetica', 12, leading=None)

    c.drawString(515, 720, datestr)
    c.drawString(70, 685, payee)
    # ____________________________________________________________________________
    c.drawString(500, 686, amount_num)

    c.drawString(30, 660, amount_text)

    image = addpath(f'tmp/{scac}/pics/ck_sigfile.png')
    c.drawImage(image, 374, 587, width=200, height=40)

    c.setFont('Helvetica', 12, leading=None)
    ltm = 15
    rtm = 590
    ctrall = 310
    left_ctr = 170
    right_ctr = 480
    dl = 17.6
    tdl = dl*2
    hls = 530

    m1 = 510
    m2 = m1-dl
    m3 = m2-dl

    m4 = m3-10
    m5 = m4-dl
    m6 = m5-dl

    m7 = 265
    m8 = m7-dl
    m9 = m8-dl

    m10 = m9-10
    m11 = m10-dl
    m12 = m11-dl

    n1 = ltm+90
    n2 = n1+150
    n3 = n2+80
    n4 = n3+80
    n5 = rtm-90

    bump = 3

    btype = bdat.bType
    bcat = bdat.bCat
    bsubcat = bdat.bSubcat



    item11 = ['Date', 'PayRef', 'Type', 'Category', 'Subcategory', 'Amount Paid']
    item12 = [datestr, payref, btype, bcat, bsubcat, amount_num]
    item21 = ['BillNo', 'Check Made Out To', 'From Acct']
    item22 = [billno, payee, bank]
    item3 = 'Memo on Check:'
    item41 = ['Address of Company:']

    if style == 1:
        fulllinesat = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12]
        for i in fulllinesat:
            c.line(ltm, i, rtm, i)
        vlines1at = [ltm, n1, n2-40, n3-40, n4-40, n5, rtm]
        for i in vlines1at:
            c.line(i, m1, i, m3)
            c.line(i, m7, i, m9)
        p1 = n1
        p2 = n5 - 60
        vlines2at = [ltm, n1, p2, rtm]
        for i in vlines2at:
            c.line(i, m4, i, m6)
            c.line(i, m10, i, m12)
    else:
        fulllinesat = [m7, m8, m9, m10, m11, m12]
        for i in fulllinesat:
            c.line(ltm, i, rtm, i)
        vlines1at = [ltm, n1, n2-40, n3-40, n4-40, n5, rtm]
        for i in vlines1at:
            c.line(i, m7, i, m9)
        p1 = n1
        p2 = n5 - 60
        vlines2at = [ltm, n1, p2, rtm]
        for i in vlines2at:
            c.line(i, m10, i, m12)

    dx = 80
    xoff = 18
    stretch = [0, -5, 15, 10, 10, 0]

    if style == 1:
        for i in range(6):
            x = avg(vlines1at[i], vlines1at[i+1])
            c.drawCentredString(x, m2+bump, item11[i])
            c.drawCentredString(x, m3+bump, str(item12[i]))
            c.drawCentredString(x, m8+bump, item11[i])
            c.drawCentredString(x, m9+bump, str(item12[i]))

        for i in range(3):
            x = avg(vlines2at[i], vlines2at[i + 1])
            c.drawCentredString(x, m5 + bump, item21[i])
            c.drawCentredString(x, m6 + bump, str(item22[i]))
            c.drawCentredString(x, m11 + bump, item21[i])
            c.drawCentredString(x, m12 + bump, str(item22[i]))
    else:

        for i in range(6):
            x = avg(vlines1at[i], vlines1at[i + 1])
            c.drawCentredString(x, m8 + bump, item11[i])
            c.drawCentredString(x, m9 + bump, str(item12[i]))

        for i in range(3):
            x = avg(vlines2at[i], vlines2at[i + 1])
            c.drawCentredString(x, m11 + bump, item21[i])
            c.drawCentredString(x, m12 + bump, str(item22[i]))





    mlev11 = m6-dl
    mlev12 = mlev11-dl
    mlev13 = mlev12-dl*1.5
    mlev14 = mlev13-dl
    mlev15 = mlev14-dl

    mlev21 = m12-dl
    mlev22 = mlev21-dl
    mlev23 = mlev22-dl*1.5
    mlev24 = mlev23-dl
    mlev25 = mlev24-dl

    c.setFont('Helvetica', 10, leading=None)

    if links != 0:
        memo2 = memo.splitlines()
        nlines = len(memo2)
        memoline = 592+13*(nlines-1)
        memoline2 = mlev12
        memoline3 = mlev22

        for line in memo2:
            c.setFont('Helvetica', 12, leading=None)
            c.drawString(52, memoline, line)
            memoline = memoline-13

            c.setFont('Helvetica', 10, leading=None)
            c.drawString(ltm+20, memoline2, line)
            memoline2 = memoline2-10
            c.drawString(ltm+20, memoline3, line)
            memoline3 = memoline3-10

    else:
        c.drawString(52, 592, memo)

    c.setFont('Helvetica', 12, leading=None)
    if style == 1: c.drawString(ltm+20, mlev11, item3)
    c.drawString(ltm+20, mlev21, item3)

    c.setFont('Helvetica', 10, leading=None)
    if links == 0:
        c.drawString(ltm+20, mlev12, memo)
        if style == 1: c.drawString(ltm+20, mlev22, memo)
        memoline2 = mlev12
        memoline3 = mlev22

    try:
        pufrom = 'Pickup: '+bdat.Link
    except:
        pufrom = 'Pickup: Unknown'
    c.setFont('Helvetica', 12, leading=None)
    if style == 1: c.drawString(ltm+20, memoline2-dl, 'Payee Address:')
    c.drawString(ltm+20, memoline3-dl, 'Payee Address:')
    c.setFont('Helvetica', 10, leading=None)
    if addr1 is None:
        addr1 = ''
    if addr2 is None:
        addr2 = ''
    if pufrom is None:
        pufrom = ''
    if style == 1:
        c.drawString(ltm+20, memoline2-dl*2, company)
        c.drawString(ltm+20, memoline2-dl*2-11, addr1)
        c.drawString(ltm+20, memoline2-dl*2-22, addr2)
        c.drawString(ltm+20, memoline2-dl*2-44, pufrom)
    else:
        cdata = companydata()
        c.setFont('Helvetica', 12, leading=None)
        offup = 5
        c.drawString(50, m2+offup, cdata[2])
        c.drawString(50, m2+offup-14, cdata[5])
        c.drawString(50, m2+offup-28, cdata[6])
        memoline2 = memoline2 - 15
        c.drawString(ltm+70, memoline2, company)
        c.drawString(ltm+70, memoline2-14, addr1)
        c.drawString(ltm+70, memoline2-28, addr2)
        zip = getzip(addr2)
        print('myzipcode is',zip)
        if zip != 0:
            barcode_usps = usps.POSTNET(zip)
            barcode_usps.drawOn(c,ltm+70,memoline2-42)
        c.setFont('Helvetica', 10, leading=None)


    c.drawString(ltm+20, memoline3-dl*2, company)
    c.drawString(ltm+20, memoline3-dl*2-11, addr1)
    c.drawString(ltm+20, memoline3-dl*2-22, addr2)
    c.drawString(ltm+20, memoline3-dl*2-44, pufrom)

    acct = bdat.bAccount
    comp = bdat.Co
    if acct is None:
        acct = ' '
    if comp is None:
        comp = ' '


    if nbills == 1:
        if btype == 'Expense':
            if style == 1: c.drawString(ltm+230, mlev11, 'Expensed Account Name: '+ acct + ' (' + comp + ')')
            c.drawString(ltm+230, mlev21, 'Expensed Account Name: '+ acct + ' (' + comp + ')')
            mlev21 = mlev21-2*dl
            mlev11 = mlev11-2*dl

        if style == 1: c.drawString(ltm+230, mlev11, 'Full Description:')
        c.drawString(ltm+230, mlev21, 'Full Description:')
        for i, line in enumerate(desc.splitlines()):
            mlev21 = mlev21-dl
            mlev11 = mlev11-dl
            if style == 1: c.drawString(ltm+230, mlev11, line)
            c.drawString(ltm+230, mlev21, line)

    if nbills > 1:
        dl = .9*dl
    if nbills > 5:
        dl = .9*dl
    mlevtop = mlev14+80-dl-dl
    mlevbot = mlev24+80-dl-dl
    if links != 0:
        s1 = ltm+270
        s2 = ltm+310
        s3 = ltm+380
        s4 = ltm+480
        if btype == 'Expense':
            if style == 1: c.drawString(ltm+230, mlev11, 'Expensed Account Name: '+ acct + ' (' + comp + ')')
            c.drawString(ltm+230, mlev21, 'Expensed Account Name: '+ acct + ' (' + comp + ')')
            mlevtop = mlev21-2*dl
            mlevbot = mlev11-2*dl
        c.setFont('Helvetica-Bold', 12, leading=None)
        if style == 1: c.drawString(s1, mlevtop+dl, 'Multi-bill payment:')
        c.drawString(s1, mlevbot+dl, 'Multi-bill payment:')
        c.drawString(s1, mlevtop, 'ID')
        c.drawString(s2, mlevtop, 'Bill No / JO')
        c.drawString(s3, mlevtop, 'Reference/BkNo.')
        c.drawString(s4, mlevtop, 'Amount')
        c.drawString(s1, mlevbot, 'Bill ID')
        c.drawString(s2, mlevbot, 'Bill No')
        c.drawString(s3, mlevbot, 'Reference/BkNo.')
        c.drawString(s4, mlevbot, 'Amount')
        c.setFont('Helvetica', 12, leading=None)

        for data in sbdata:
            mlevtop = mlevtop-dl
            mlevbot = mlevbot-dl
            id = str(data.id)
            billno = data.Jo
            ref = data.Memo
            # if memo long
            ref = ref.replace('For booking ', '')
            amt = dollar(float(data.pAmount))
            c.drawString(s1, mlevtop, id)
            try:
                c.drawString(s2, mlevtop, billno)
                c.drawString(s2, mlevbot, billno)
            except:
                err = '1'
            c.drawString(s3, mlevtop, ref)
            c.drawString(s4, mlevtop, amt)
            c.drawString(s1, mlevbot, id)

            c.drawString(s3, mlevbot, ref)
            c.drawString(s4, mlevbot, amt)

    c.showPage()
    c.save()
    return
