import numpy as np
import os
import shutil

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
import csv
import math
import datetime
from viewfuncs import avg

def dockm(odata, bdata, adata, pdata1, pdata2, pdata3, pdata4, pdata5, newfile, fs, hscode, iti):

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
        nameout=first + ' ' + middle + ' ' + last
        if len(nameout)>55:
            nameout=first + ' ' + last
        return nameout

    def address(addr1,addr2,addr3):
        street=addr1
        cityst=addr2
        if addr3 is None or addr3=='':
            cityst=addr2
        else:
            if len(addr3)<5:
                cityst=addr2
        if addr2 is None or addr2=='':
            cityst=addr3
            if len(addr2)<3:
                cityst=addr3
            else:
                cityst=addr2+' '+addr3
        return street,cityst

    def nonone(incoming):
        if incoming is not None:
            outgoing=incoming
        else:
            outgoing=' '
        return outgoing

    today = datetime.datetime.today().strftime('%m/%d/%Y')
    joborder=nonone(odata.Jo)

    exporter=list(range(5))
    if pdata1 is not None:
        exporter[0]=comporname(pdata1.Company, fullname(pdata1.First, pdata1.Middle, pdata1.Last))
        exporter[1], exporter[2]= address(pdata1.Addr1,pdata1.Addr2,pdata1.Addr3)
        exporter[3]='Phone: '+pdata1.Telephone
        exporter[4]='Email: '+pdata1.Email
    else:
        for i in range(5):
            exporter[i]=' '

    consig=list(range(5))
    if pdata2 is not None:
        consig[0]=comporname(pdata2.Company, fullname(pdata2.First, pdata2.Middle, pdata2.Last))
        consig[1], consig[2]= address(pdata2.Addr1,pdata2.Addr2,pdata2.Addr3)
        consig[3]='Phone: '+pdata2.Telephone
        consig[4]='Email: '+pdata2.Email
    else:
        for i in range(5):
            consig[i]=' '

    notify=list(range(3))
    if pdata3 is not None:
        notify[0]=comporname(pdata3.Company, fullname(pdata3.First, pdata3.Middle, pdata3.Last))
        notify[1]='Phone: '+pdata3.Telephone
        notify[2]='Email: '+pdata3.Email
    else:
        for i in range(3):
            notify[i]=' '

    prec=list(range(3))
    if pdata4 is not None:
        prec[0]=pdata4.Company
        prec[1]=pdata4.Addr1 + ' ' + pdata4.Addr2
        prec[2]='Phone: '+pdata4.Telephone + '  Email: '+ pdata4.Email
    else:
        for i in range(3):
            prec[i]=' '

    itidis=''
    if iti is not None:
        if iti != 'None':
            itidis=iti

    occarrier=list(range(1))
    occarrier[0]=nonone(bdata.Line)

    pod=list(range(1))
    pod[0]=nonone(odata.Pod)+' '+itidis
# End of left side
# Start right side
    booking=list(range(1))
    booking[0]=nonone(odata.Booking)

    if bdata is not None:
        shipref=nonone(bdata.ExportRef)
    else:
        shipref=''
    overshipref=odata.ExpRef
    if overshipref is not None:
        if overshipref != '':
            shipref=overshipref

    exportref=list(range(1))
    exportref[0]=nonone(shipref)

    displaynote=''
    addnote=odata.AddNote
    if addnote is not None and addnote != 'None':
        if addnote != '':
            displaynote=addnote

    ff=list(range(4))
    if pdata5 is not None:
        try:
            ff[0]=comporname(pdata5.Company, fullname(pdata5.First, pdata5.Middle, pdata5.Last)) + '                  FMC# '
        except:
            ff[0]=pdata5.Company + '                  FMC# '+pdata5.Idnumber
        ff[1], ff[2]= address(pdata5.Addr1,pdata5.Addr2,pdata5.Addr3)
        ff[3]=' '
#'Phone: '+pdata5.Telephone + '     Email: '+pdata5.Email
    else:
        for i in range(4):
            ff[i]=' '

    origin=list(range(1))
    origin[0]=nonone(odata.Origin)

    route=list(range(7))
    route[0]='Vessel: '+nonone(bdata.Vessel)
    route[1]='Ship Line: '+nonone(bdata.Line)
    route[2]="Port Cutoff: "+bdata.PortCut.strftime("%m-%d-%Y")
    route[3]="Doc Cutoff: "+bdata.DocCut.strftime("%m-%d-%Y")
    route[4]="Sail Date: "+bdata.SailDate.strftime("%m-%d-%Y")
    route[5]="Estimated Arrival: "+bdata.EstArr.strftime("%m-%d-%Y")
    route[6]="Arrives At: "+nonone(bdata.Dest)+itidis

    pol=list(range(1))
    pol[0]=nonone(odata.Pol)

    type=list(range(1))
    type[0]=nonone(odata.MoveType)

    containertype='1* ' + nonone(odata.ContainerType)
    #end right side
    #Begin side to side
    #[container, packages, cars, wts, colors, titles]
    if odata is not None:
        thiscontainer=nonone(odata.Container)
    else:
        container=''

    seal=nonone(odata.Seal)
    itn=nonone(odata.AES)


    container=list(range(4))
    container[0]='Cont: '+thiscontainer
    container[1]='Seal: '+seal
    container[2]=' '
    container[3]='ITN: '+ itn

    z=len(adata)
    if z>0:
        package=str(z)+' autos'
    else:
        package=' '

    if adata is not None:
        cars=[]
        vins=[]
        colors=[]
        titles=[]
        states=[]
        wts=[]
        packages=[]

        for j,data in enumerate(adata):
            if j==0:
                packages.append(package)
            else:
                packages.append(' ')
            cars.append(data.Year+' '+data.Make+' '+data.Model)
            vins.append('VIN: '+nonone(data.VIN))
            wtlb=data.EmpWeight
            try:
                wts.append(str(int(float(wtlb)/2.2))+' Kg')
            except:
                wts.append(wtlb)
            colors.append(nonone(data.Color))
            titles.append('Title No. ' + nonone(data.Title))
            states.append('State of '+ nonone(data.State))

        if odata.Description:
            text=nonone(odata.Description).splitlines()
            for i,line in enumerate(text):
                try:
                    lp1=line.split(':',2)[0]
                    lp2=line.split(':',2)[1]
                    lp3=line.split(':',2)[2]
                except:
                    try:
                        lp1=''
                        lp2=line.split(':',1)[0]
                        lp3=line.split(':',1)[1]
                    except:
                        lp1=''
                        lp2=line
                        lp3=''

                cars.append(nonone(lp2))
                try:
                    wts.append(str(int(float(lp3)/2.2))+' Kg')
                except:
                    wts.append('')
                packages.append(lp1)






    hscode='HS Code: '+hscode
    release=nonone(odata.RelType)
    if release=='telex':
        reldisplay='TELEX Release REQUESTED'
    else:
        reldisplay='SEAWAY BILL REQUESTED'
#___________________________________________________________


    ltm=15
    rtm=600
    ctr=310
    left_ctr=165
    right_ctr=462
    dl=13
    tdl=dl*2
    linesat=[730, 730-dl, 660, 590, 500, 500-dl, 475, 475-dl, 450, 450-dl, 450-dl*2, 195, 75, 75-dl]
    lhl    =[660-dl,590-dl,545,545-dl]
    #sds    =[ltm,50,215,400,450,495,rtm]
    sds2   =[ltm,ctr,rtm]
    rhl    =[730-dl*2, 730-dl*3, 730-dl*4, 590+2*dl, 590+dl, 590-dl, 75+dl+5]

    c=canvas.Canvas(newfile, pagesize=letter)
    c.setLineWidth(.3)
    c.setFont('Helvetica-Bold',52,leading=None)
    c.drawCentredString(310,732,'DOCK RECEIPT')



    c.setFont('Helvetica-Bold',fs,leading=None)
    lxm=ltm+5
    rxm=ctr+5
    bump=2
    lbltat=[730-dl, 660-dl, 590-dl, 545-dl, 500-dl, 475-dl, 450-2*dl]
    lblt=['Exporter', 'Consignee', 'Notify Party', 'PRE Carriage By:', 'Ocean Carrier', 'P.O.D.', '']
    j=0
    for i in lbltat:
        c.drawString(lxm,i+bump,str(lblt[j]))
        j=j+1
    lbrtat=[730-dl, 730-dl*3, 660, 590+dl, 590-dl, 500-dl, 475-dl]
    lbrt=['Booking#','Exporter Reference', 'Freight Forwarder', 'Point of Origin', 'Routing/Export Instructions','P.O.L./Terminal', 'Type of Move']
    j=0
    for i in lbrtat:
        c.drawString(rxm,i+bump,str(lbrt[j]))
        j=j+1
    c.drawRightString(rtm,730-2*dl+bump, str(joborder))
    c.drawString(518,450+dl+bump,'Containerized')
    #labltorat=[135,215,400,450,495]
    labltor=['Marks/Numbers', 'Pkgs', 'Description of Commodity', 'Weight', 'Color', 'Other']

    sds    =[ltm,120,360,420,465,170]
    ctpt=[avg(sds[0],sds[1]),avg(sds[1],sds[5]),avg(sds[5],sds[2]),avg(sds[2],sds[3]),avg(sds[3],sds[4]),avg(sds[4],rtm)]
    for j,i in enumerate(labltor):
        c.drawCentredString(ctpt[j],450-2*dl+bump,str(labltor[j]))
    c.drawRightString(rtm,732-dl,today)


    nfs=fs-1
    c.setFont('Helvetica',nfs,leading=None)
    blocks=[exporter, consig, notify, prec, occarrier, pod]
    dh=10
    for i in range(6):
        sb=lbltat[i]-dl+bump+1
        block=blocks[i]
        for b in block:
            c.drawString(lxm,sb,str(b))
            sb=sb-dh

    blocks=[booking, exportref, ff, origin, route, pol, type]
    for i in range(7):
        sb=lbrtat[i]-dl+bump+1
        block=blocks[i]
        for b in block:
            c.drawString(rxm,sb,str(b))
            sb=sb-dh
    c.drawString(518,450+bump,str(containertype))

    xfs=fs-2
    c.setFont('Times-Roman',xfs,leading=None)

    # Do cars last to make it easy to get lowest record
    topblocks=[container, packages, wts, colors, titles, cars]

    j=0
    for i in sds:
        ls=i+bump
        top=450-3*dl
        block=topblocks[j]
        j=j+1
        k=0
        for b in block:
            k=k+1
            c.drawString(ls,top,str(b))
            if k>z and (j==6 or j==3 or j==2):
                top=top-dh
            else:
                top=top-3*dh
    lowest=top-dh

    botblocks=[vins,states]
    sdstwo     =[170,465]
    k=0
    for i in sdstwo:
        ls=i+bump
        top=450-3*dl-dh
        block=botblocks[k]
        k=k+1
        for b in block:
            c.drawString(ls,top,str(b))
            top=top-3*dh

    #Write out the special marks hscode, ...etc
    lsr=465+bump
    ls=170+bump
    rs=ls+141

    c.setFillColorRGB(255,255,0)
    c.rect(lsr-bump,lowest-bump,100,dh, stroke=0, fill=1)
    c.rect(ls-bump,lowest-bump,130,dh, stroke=0, fill=1)
    c.setFillColorRGB(0,0,0)
    c.drawString(ls,lowest,reldisplay)
    c.drawString(ls,lowest-50,displaynote)
    c.drawString(lsr,lowest,hscode)
    c.drawString(ls,lowest-20,itidis)
    ls=170+bump
    rs=ls+141
    top=205
    c.drawString(ls,top,'ON BOARD FREIGHT PREPAID')
    if '9403' in hscode:
        err=0
    else:
        c.drawString(ls,top+30,'**GAS TANKS HAVE BEEN EMPTIED**')
        c.drawString(ls,top+15,'**BATTERY CABLES DISCONNECTED**')
    top=top-bump
    c.line(ls,top,rs,top)

    c.setFont('Times-Roman',10,leading=None)
    items=['Received are the above goods and packages, which are subject to',
          "all the terms of the undersigned's documentation, and shall",
          'constituate a contract under which the goods are received.',
          'Copies of this documentation in the form of a dock receipt',
          'or bill of lading are available from the carrier upon request,',
          "or may be inspected at any of its offices.",
          ' ',
          'By                                                       Date:',
          ' ',
          ' ',
          '        Receiving Clerk for the Master']
    sb=195-dl-bump
    for item in items:
        c.drawString(rxm,sb,str(item))
        sb=sb-dh
    sb=195-dl-bump
    c.drawCentredString(left_ctr,sb,'Delivered by FIRST EAGLE LOGISTICS, INC.')
    items=['Truck:', 'Arrived:', 'Checked By:', 'Dropped (Port):']
    sb=sb-2*dh
    for item in items:
        c.drawString(lxm,sb,item)
        sb=sb-2*dh

    #c.setFont('Times-Roman',24,leading=None)
    #Decided not to place any numbers here for now.
    #c.drawCentredString(ctr,80,container[3])



    c.line(ctr,730,ctr,450)
    for i in linesat:
        c.line(ltm,i,rtm,i)
    for j in lhl:
        c.line(ltm,j,ctr,j)
    for k in sds:
        c.line(k,450-dl,k,195)
    c.line(rtm,450-dl,rtm,195)
    for l in sds2:
        c.line(l,195,l,75-dl)
    for m in rhl:
        c.line(ctr,m,rtm,m)
    c.line(515,450,515,450+dl*2)
    c.showPage()
    c.save()
    return
