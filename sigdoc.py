# Now lets print the report out
from flask import session, logging, request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.units import inch
from viewfuncs import nonone, nononef, nononestr, dollar, avg, comporname, fullname, address
import csv
import math
import datetime
from page_merger import pagemergerx
from CCC_system_setup import addpath, scac

def repackage(npages,file6,docref):
    import numpy as np
    import subprocess
    import fnmatch
    import os
    import json
    import shutil
    from collections import Counter
    import datetime
    from PyPDF2 import PdfFileReader

    newpages = []
    for f in range(1, npages+1):
        newpages.append(addpath(f'tmp/{scac}/data/vreport/'+str(f)+'.pdf'))
    pdfcommand = ['pdfunite']
    for page in newpages:
        pdfcommand.append(page)
    pdfcommand.append(file6)
    tes = subprocess.check_output(pdfcommand)
    os.rename(file6, addpath(docref))


def sigdoc(stampdata, docin, docref):

    import numpy as np
    import subprocess
    import fnmatch
    import os
    import json
    import shutil
    from collections import Counter
    import datetime
    from PyPDF2 import PdfFileReader


    today = datetime.datetime.today()
    year = str(today.year)
    day = str(today.day)
    month = str(today.month)
    # print(month,day,year)
    datestr = month+'/'+day+'/'+year
    file1 = addpath(docin)
    reader = PdfFileReader(open(file1, 'rb'))
    npages = reader.getNumPages()
    ck = subprocess.check_output(['pdfseparate', file1, addpath(f'tmp/{scac}/data/vreport/%d.pdf')])
    file6 = addpath(f'tmp/{scac}/data/vreport/report6.pdf')



    sigpage=int(stampdata[3])
    sigx=int(stampdata[5])
    sigy=int(stampdata[4])
    xpage=int(stampdata[0])
    xmarkx=int(stampdata[2])
    xmarky=int(stampdata[1])
    datepage=int(stampdata[6])
    datex=int(stampdata[8])
    datey=int(stampdata[7])

    if sigpage > 0:
        # Want to create a signature/date doc page
        file2 = addpath(f'tmp/{scac}/data/processing/t1.pdf')
        c = canvas.Canvas(file2, pagesize=letter)
        c.setLineWidth(1)
        sigpage=sigpage-1
        logo = addpath("tmp/sensitive/marksign2.jpg")
        c.drawImage(logo, sigx, sigy, width=150, preserveAspectRatio=True, mask='auto')
        c.showPage()
        c.save()
        cache = 1
        sigpagefile = addpath(f'tmp/{scac}/data/vreport/'+str(sigpage+1)+'.pdf')
        cache, docrefx = pagemergerx([file1, file2], sigpage, cache)
        file3 = addpath(f'tmp/{scac}/data/vreport/report1.pdf')
        os.remove(sigpagefile)
        os.rename(file3, sigpagefile)
        repackage(npages,file6,docin)

    if datepage > 0:
        # Want to create a signature/date doc page
        datepage=datepage-1
        file2 = addpath(f'tmp/{scac}/data/processing/t1.pdf')
        c = canvas.Canvas(file2, pagesize=letter)
        c.setLineWidth(1)
        c.setFont('Helvetica', 12, leading=None)
        c.drawString(datex, datey, datestr)
        c.showPage()
        c.save()
        cache = 1
        datepagefile = addpath(f'tmp/{scac}/data/vreport/'+str(datepage+1)+'.pdf')
        cache, docrefx = pagemergerx([file1, file2], datepage, cache)
        file3 = addpath(f'tmp/{scac}/data/vreport/report1.pdf')
        os.remove(datepagefile)
        os.rename(file3, datepagefile)
        repackage(npages,file6,docin)

    if xpage>0:
        xpage = xpage-1
        xpagefile = addpath(f'tmp/{scac}/data/vreport/'+str(xpage+1)+'.pdf')
        file2 = addpath(f'tmp/{scac}/data/processing/t2.pdf')
        c = canvas.Canvas(file2, pagesize=letter)
        c.setLineWidth(1)
        xbox = addpath("tmp/pics/x100.png")
        c.drawImage(xbox, xmarkx, xmarky, width=30, preserveAspectRatio=True, mask='auto')
        c.showPage()
        c.save()
        cache=5
        cache, docrefx = pagemergerx([file1, file2], xpage, cache)
        file5 = addpath(f'tmp/{scac}/data/vreport/report5.pdf')
        os.remove(xpagefile)
        os.rename(file5, xpagefile)
        repackage(npages,file6,docin)
    #Create final document after all the overwrites:
    os.rename(addpath(docin), addpath(docref))
