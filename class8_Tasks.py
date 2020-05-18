from runmain import db
from models import DriverAssign, Gledger, Vehicles, Invoices, JO, Income, Orders, Accounts, LastMessage, People, Interchange, Drivers, ChalkBoard, Services, Drops, StreetTurns
from flask import render_template, flash, redirect, url_for, session, logging, request
from CCC_system_setup import myoslist, addpath, tpath, companydata, scac
from InterchangeFuncs import Order_Container_Update, Match_Trucking_Now, Match_Ticket
from email_appl import etemplate_truck

import datetime
import os
import subprocess
from func_cal import calmodalupdate
import json


define New_task(iter):
    #First time through new job sequence
    if iter == 0:
        cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
        modlink = 4
        leftsize = 8
        leftscreen = 0
        docref = None
        holdvec = [''] * 25
        holdvec[16] = today_str
        holdvec[17] = today_str
        holdvec[18] = '500.00'

if newjob is None and modlink == 4:
    holdvec = [''] * 25
    cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
    leftscreen = 0
    shipper = request.values.get('shipper')
    pufrom = request.values.get('thislcomp')
    deltoc = request.values.get('thisdcomp')
    holdvec[0], holdvec[1], holdvec[2] = shipper, pufrom, deltoc
    plist = []
    delist = []
    oshipper = Orders.query.filter(Orders.Shipper == shipper).all()
    for tship in oshipper:
        try:
            pu = tship.Company.strip()
        except:
            pu = tship.Company
        try:
            du = tship.Company2.strip()
        except:
            du = tship.Company2
        if pu not in plist:
            plist.append(pu)
        if du not in delist:
            delist.append(du)
    holdvec[4] = plist
    holdvec[5] = delist
    holdvec[6] = request.values.get('getpuloc')
    holdvec[7] = request.values.get('getduloc')
    if holdvec[6] is not None:
        oship = Orders.query.filter((Orders.Shipper == shipper) & (Orders.Company == holdvec[6])).first()
        if oship is not None:
            holdvec[8] = oship.Dropblock1
    if holdvec[8] is not None:
        oship = Orders.query.filter((Orders.Shipper == shipper) & (Orders.Company2 == holdvec[7])).first()
        if oship is not None:
            holdvec[9] = oship.Dropblock2
    vals = ['order', 'bol', 'booking', 'container', 'ctype', 'future',
            'date', 'date2', 'amount', 'commodity', 'packing', 'pickup', 'seal', 'desc']
    a = list(range(len(vals)))
    for i, v in enumerate(vals):
        a[i] = request.values.get(v)
        if a[i]:
            a[i] = a[i].strip()
            itap = i + 10
            holdvec[itap] = a[i]
    amt = request.values.get('amount')
    holdvec[18] = d2sa(amt)

if thisjob is not None:
    modlink = 0
    # Create the new database entry for the source document
    oid, nextjo = make_new_order()
    modata = Orders.query.filter(Orders.Jo == nextjo).first()
    cdata = People.query.filter(People.Ptype == 'Trucking').order_by(People.Company).all()
    oder = modata.id
    Order_Container_Update(oder)
    leftscreen = 1