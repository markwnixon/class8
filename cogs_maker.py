import numpy as np
import subprocess
import fnmatch
import os
import shutil
from collections import Counter
import datetime
import re
from scrapers import vinscraper
from models import OverSeas, Orders, Bills, Autos, Invoices

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import numpy as np
import subprocess
import os
import shutil
import datetime
import re
import mysql.connector

from remote_db_connect import db
from models import Autos

start= datetime.date(2019, 1, 1)
end= datetime.date(2019, 1, 29)
tdata=Orders.query.filter((Orders.Date>=start) & (Orders.Date<=end)).order_by(Orders.Date).all()
odata=OverSeas.query.filter((OverSeas.RetDate>=start) & (OverSeas.RetDate<=end)).order_by(OverSeas.RetDate).all()

for odat in odata:
    jo=odat.Jo
    try:
        income1=float(odat.Charge)
    except:
        income1=0.00
    try:
        expens1=float(odat.Estimate)
    except:
        expens1=0.00

    towinc=Invoices.query.filter( (Invoices.Jo==jo) & (Invoices.Service=='Towing') ).all()
    income2=0.00
    expens2=0.00
    for tow in towinc:
        income2=income2+float(tow.Ea)
        descipt=tow.Description
        vin=descipt.split('VIN:',1)[1]
        adat=Autos.query.filter(Autos.VIN==vin).first()
        if adat is not None:
            towcost=adat.TowCostEa
            try:
                expens2=expens2+float(towcost)
            except:
                print('bad tow cost:',towcost)
            print(adat.VIN,towcost,tow.Ea)

    income3=0.00
    expens3=0.00
    fedex=Invoices.query.filter( (Invoices.Jo==jo) & (Invoices.Service=='Towing') ).all()

    profit=income1 + income2 - expens1 - expens2

    print(odat.Jo,odat.PuDate,odat.RetDate,income1,expens1,income2,expens2)
    print('Gross Profit=',profit)
