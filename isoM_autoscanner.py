from runmain import db
from models import Autos
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import subprocess
from CCC_system_setup import myoslist,addpath,addtxt,tpath, scac

def isoMautoscanner():

    if request.method == 'POST':
# ____________________________________________________________________________________________________________________B.FormVariables.General

        from viewfuncs import parseline, popjo, jovec, newjo, timedata, nonone, nononef
        from viewfuncs import numcheck, numcheckv, viewbuttons, get_ints, numcheckvec

        #Zero and blank items for default
        username = session['username'].capitalize()

        today = datetime.date.today()
        now = datetime.datetime.now().strftime('%I:%M %p')
        vinlist=''
        try:
            os.remove('/home/oslm/oslrun/tmp/data/processing/vins.txt')
        except IOError:
            print('File already removed')

        vins = request.values.get('vinlist')
        if vins is not None:
            vinlist=vins.split()
            txt_file=addpath(f'tmp/{scac}/data/processing/vins.txt')
            with open(txt_file,'a+') as f:
                for vin in vinlist:
                    vin=vin.strip()
                    f.write(vin+'\n')
        f.close()
        thisip = os.environ['PUBLICIP']
        vinlist = vinlist + ['Sent to', thisip]
        tout = subprocess.check_output(['scp', '/home/oslm/oslrun/tmp/data/processing/vins.txt', 'mark@'+thisip+':/home/mark/flask/crontasks/incoming/vins.txt'])

        #os.system('scp tmp/data/processing/vins.txt mark@98.231.243.208:/home/mark/flask/crontasks/incoming/vins.txt')
        #p = subprocess.Popen(["scp", "tmp/data/processing/vins.txt", "mark@98.231.243.208:/home/mark/flask/crontasks/incoming/vins.txt"])
        #sts = os.waitpid(p.pid, 0)

# ____________________________________________________________________________________________________________________E.Delete.General

    else:
        from viewfuncs import init_tabdata, popjo, jovec, timedata, nonone, nononef
        today = datetime.date.today()
        #today = datetime.datetime.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime('%I:%M %p')
        err=['All is well', ' ', ' ', ' ',  ' ']
        vinlist=''


    return vinlist
