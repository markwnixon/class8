#Now lets print the report out
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
from report_background import invo_background
from pagemerger import pagemerger
from report_headers import jayheaders
from report_data import jaycalcs,ticketcalcs
from report_content import jaycontents,ticketcontents

def reportmake(type):

    cache =  request.values.get('cache')
    cache=nonone(cache)

    file1='tmp/data/vreport/pagestart.pdf'
    file2='tmp/data/vreport/background.pdf'
    file3='tmp/data/vreport/headers.pdf'
    file4='tmp/data/vreport/contents.pdf'
    today = datetime.datetime.today().strftime('%m/%d/%Y')
    invodate = datetime.date.today().strftime('%m/%d/%Y')

    c=canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)
    logo = "tmp/felpics/logo3.jpg"
    c.drawImage(logo, 185, 680, mask='auto')
    c.showPage()
    c.save()

    if type=='mtick':
        invo_background(file2)
        jayheaders(file3)
        itemlist=ticketcalcs()
        ticketcontents(file4,itemlist)

    if type=='jay':
        invo_background(file2)
        jayheaders(file3)
        itemlist,bitemlist,total,btotal,nettotal=jaycalcs()
        jaycontents(file4,itemlist,bitemlist,total,btotal,nettotal)

    cache,docref=pagemerger([file1,file2,file3,file4],cache)
    return cache,docref
