from runmain import app, db
from models import Vehicles, Invoices, JO, Income, Bills, Accounts, OverSeas, Orders, Gledger
from models import Autos, People, Interchange, Drivers, ChalkBoard, Services, Drops, Divisions, LastMessage
from flask import session, logging, request
import datetime
import calendar
import re
import os
import shutil
import json
from CCC_system_setup import myoslist, addpath, addtxt, scac, companydata

compdata = companydata()
billexpcode = compdata[10]+'B'
billxfrcode = compdata[10]+'X'


def isoB(indat):

    if request.method == 'POST':

        from viewfuncs import tabdata, tabdataR, popjo, jovec, timedata, nonone, nononef, nons, numcheck, newjo, init_billing_zero, init_billing_blank
        from viewfuncs import sdiff, calendar7_weeks, txtfile, numcheckvec, d2s, erud, dataget_B, hv_capture, docuploader, get_def_bank, next_check
        from gledger_write import gledger_write

        username = session['username'].capitalize()
        bill_path = 'processing/bills'
        bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_billing_zero()
        filesel, docref, search11, search12, search13, search14, search21, search22, bType, bClass = init_billing_blank()
        expdata, addjobselect, jobdata, modal, viewck = 0, 0, 0, 0, 0

        hv = [0]*20
        divdat = Divisions.query.all()

        monlvec = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
        monsvec = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                   'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        err = []
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        docref = ' '
        doctxt = ' '
        if indat == 'stay' or indat == 0:
            indat = '0'

        match = request.values.get('Match')
        modify = request.values.get('Modify')
        modify2 = request.values.get('Modify2')
        vmod = request.values.get('Vmod')
        viewo = request.values.get('ViewO')
        addE = request.values.get('addentity')
        addE2 = request.values.get('addentity2')
        paybill = request.values.get('PayB')
        paybill2 = request.values.get('PayB2')
        paynmake = request.values.get('paynmake')
        unpay = request.values.get('UnPay')
        printck = request.values.get('Prt')
        openbal = request.values.get('Open')
        returnhit = request.values.get('Return')
        deletehit = request.values.get('Delete')
        # hidden values
        update = request.values.get('Update')
        modlink = request.values.get('modlink')
        newbill = request.values.get('NewB')
        thisbill = request.values.get('ThisBill')
        newxfer = request.values.get('Xfer')
        thisxfer = request.values.get('ThisXfer')
        calendar = request.values.get('Calendar')
        calupdate = request.values.get('calupdate')
        incoming = request.values.get('incoming')
        incoming_O = request.values.get('incoming_O')
        datatable1 = request.values.get('datatable1')
        datatable2 = request.values.get('datatable2')
        dlist = [datatable1, datatable2]


        copy = request.values.get('copy')
        copy12 = request.values.get('copy12')
        qpay = request.values.get('qpay')

        bill = request.values.get('bill')
        cache = request.values.get('cache')
        peep = request.values.get('peep')
        uploadS = request.values.get('UploadS')

        modlink = nonone(modlink)
        bill = nonone(bill)
        peep = nonone(peep)

        thismuch = request.values.get('thismuch')
        if thismuch is not None:
            hv[1] = thismuch
        else:
            hv[1] = request.values.get('passthismuch')

        thisbox0 = request.values.get('codiv')
        if thisbox0 is not None:
            hv[0] = thisbox0
        else:
            hv[0] = request.values.get('passco')


        thisbox1 = request.values.get('addbox')
        if thisbox1 == '1':
            newbill = 1
        if thisbox1 == '2':
            addE = 1
        if thisbox1 == '3':
            copy = 1
        if thisbox1 == '4':
            copy12 = 1
        if thisbox1 == '5':
            uploadS = 1
        if thisbox1 == '6':
            newxfer = 1


        thisbox2 = request.values.get('editbox')
        if thisbox2 == '1':
            vmod = 1
        if thisbox2 == '2':
            match = 1
        if thisbox2 == '3':
            acceptthese = 1
        if thisbox2 == '4':
            loadc = 1

        thisbox3 = request.values.get('invobox')
        if thisbox3 == '1':
            qpay = 1
        if thisbox3 == '2':
            paybill = 1
        if thisbox3 == '3':
            paybill2 = 1
        if thisbox3 == '4':
            printck = 1

        thisbox4 = request.values.get('viewbox')
        if thisbox4 == '1':
            viewo = 1
        if thisbox4 == '2':
            viewck = 1

        thisbox5 = request.values.get('xbox')
        if thisbox5 == '1':
            deletehit = 1
        if thisbox5 == '2':
            unpay = 1

        thisbox6 = request.values.get('dispbox')
        if thisbox6 == '1':
            mm2 = 1
            #Signature date:
            holdvec[16] = today_str
        if thisbox6 == '2':
            lbox = 6
            lbox, holdvec, err = container_list(lbox, holdvec)
        if thisbox6 == '3':
            lbox = 1
       # if modlink==9 or modlink==8:
       #     peephold=peep

        if modlink == 4 or modlink == 8:
            leftscreen = 0
        else:
            leftscreen = 1

        if returnhit is not None:
            modlink = 0
            leftscreen = 1
            indat = '0'
            # Delete all vendors created but not completed
            pgone = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
            for pg in pgone:
                company = pg.Company
                if company == '' or company == ' ' or company == None or company == 'None':
                    People.query.filter(People.id == pg.id).delete()
                    db.session.commit()
            # Put all bills in Paying Status back to unpaid
            pybills = Bills.query.filter(Bills.Status == 'Paying').all()
            for py in pybills:
                py.Status = 'Unpaid'
                db.session.commit()
# ____________________________________________________________________________________________________________________B.QuickBillPayTowing
        if incoming is not None:
            # Came to this point from outside so nothing is translated
            bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_billing_zero()
            filesel, docref, search11, search12, search13, search14, search21, search22, bType, bClass = init_billing_blank()

            towid = request.values.get('towid')
            towid = nonone(towid)
            adat = Autos.query.get(towid)
            pufrom = adat.Pufrom
            bdesc = 'Towing performed by \r\n'+adat.TowCompany
            print('Towing Items',adat.TowCompany,adat.Pufrom)
            adata = Autos.query.filter(Autos.Orderid == adat.Orderid).all()
            for dat in adata:
                bdesc = bdesc+'\r\n'+nons(dat.Year)+' '+nons(dat.Make) + \
                    ' '+nons(dat.Model)+' VIN: '+nons(dat.VIN)
                dat.Status = 'Paid'
                db.session.commit()

            cdat = People.query.filter((People.Company == adat.TowCompany) & (
                (People.Ptype == 'TowCo') | (People.Ptype == 'Vendor'))).first()
            if cdat is None:
                input = People(Company=adat.TowCompany, First=None, Middle=None, Last=None, Addr1=None, Addr2=None, Addr3=None,
                               Idtype=None, Idnumber=None, Telephone=None,
                               Email=None, Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None,
                               Ptype='TowCo', Temp1=None, Temp2=None, Accountid=None)
                db.session.add(input)
                db.session.commit()
                cdat = People.query.filter((People.Company == adat.TowCompany) & (
                        (People.Ptype == 'TowCo') | (People.Ptype == 'Vendor'))).first()

            if cdat is not None:
                cid = cdat.Accountid
                aid = cdat.id
                acdat = Accounts.query.filter(Accounts.id == cid).first()
                if acdat is not None:
                    descript = acdat.Description
                    baccount = acdat.Name
                    btype = acdat.Type
                    bcat = acdat.Category
                    bsubcat = acdat.Subcategory
                else:
                    bcat = 'NAY'
                    bsubcat = 'NAY'
                    descript = ''
                    baccount = ''
            else:
                bcat = 'NAY'
                bsubcat = 'NAY'
                descript = ''
                baccount = ''

            # Create the new database entry for the source document
            sdate = adat.Date2
            ckmemo = 'Towing for Dealership Car Purchase'
            bamt = d2s(adat.TowCost)
            bref = ''
            btype= 'Expense'
            bcat = 'Direct'
            bsubcat = 'Overseas'
            account = compdata[9]
            baccount = 'Towing Costs'
            nextjo = newjo(billexpcode, today)

            input = Bills(Jo=nextjo, Pid=aid, Company=cdat.Company, Memo=ckmemo, Description=bdesc, bAmount=bamt, Status='Paid', Cache=0, Original='',
                             Ref=bref, bDate=sdate, pDate=today, pAmount=bamt, pMulti=None, pAccount=account, bAccount=baccount, bType=btype,
                             bCat=bcat, bSubcat=bsubcat, Link=pufrom, User=username, Co=compdata[10], Temp1=None, Temp2=str(towid), Recurring=0, dDate=today,
                             pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0)

            db.session.add(input)
            db.session.commit()

            modata = Bills.query.filter(Bills.Jo == nextjo).first()
            csize = People.query.filter(People.Ptype == 'TowCo').order_by(People.Company).all()
            bill = modata.id
            leftscreen = 1
            bdata = Bills.query.order_by(Bills.bDate).all()
            cdata = People.query.filter((People.Ptype == 'Vendor') | (
                People.Ptype == 'TowCo')).order_by(People.Company).all()
            modlink = 12
# ____________________________________________________________________________________________________________________E.QuickBillPayTowing

        print('yes here with modlink=', modlink)

        if modlink == 4 and (newbill is None and thisbill is None and update is None):
            upnow = request.values.get('uploadnow')
            if upnow is not None:
                err, oid = docuploader('bill')
                if modlink == 4:
                    bill = oid
                    bdat = Bills.query.get(bill)
                    bdat.User = username
                    original = bdat.Original
                    if original is not None:
                        docref = f'tmp/{scac}/data/vbills/' + original
                        print(bill,docref)
                    modlink = 7
                else:
                    modlink = 0

        if modlink == 70:
            print('Got to bill uploader')
            err, oid = docuploader('bill')
            modlink = 0
# ____________________________________________________________________________________________________________________B.UpdateDatabasesSection
        if (update is not None and modlink == 1) or modlink == 9 or modlink == 8 or modlink == 7 or modlink == 6:
            print('Yes Here')
            if bill > 0:
                modata = Bills.query.get(bill)
                ifxfer = modata.bType
                if ifxfer == 'XFER':
                    vals = ['fromacct', 'toacct', 'pamt', 'bref',
                            'pdate', 'ckmemo', 'bdesc', 'ddate']
                    a = list(range(len(vals)))
                    i = 0
                    for v in vals:
                        a[i] = request.values.get(v)
                        i = i+1

                    if a[4] is None:
                        a[4] = today
                    bdol = d2s(a[2])
                    modata.Memo = a[5]
                    modata.Description = a[6]
                    modata.bAmount = bdol
                    modata.bDate = a[4]
                    modata.dDate = a[7]
                    modata.pAmount = bdol
                    modata.pDate = a[4]
                    modata.pAccount = a[0]
                    modata.Ref = a[3]
                    modata.User = username
                    modata.Company = a[1]
                    err.append('Modification to Xfer ' + modata.Jo + ' completed.')

                else:

                    leftsize = 8
                    leftscreen = 0
                    if update is None:

                        pbill = request.values.get('pbill')
                        pb = nonone(pbill)
                        bval = request.values.get('ctype')
                        print('Updat is None so running this sequence')
                        if bval is not None:
                            modata.Co = bval
                            db.session.commit()
                            expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(bval))).all()
                        pacct = request.values.get('account')
                        print(pacct)
                        pcheck = next_check(pacct,modata.id)
                        modata.pAccount = pacct
                        modata.Ref = pcheck
                        db.session.commit()
                        docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                        if os.path.isfile(addpath(docref)):
                            leftscreen = 0
                            err.append(f'Paying Bill {modata.Jo}')
                        else:
                            leftscreen = 1
                            err.append(f'Paying Bill {modata.Jo}')
                            err.append('Bill has no source document')
                        modata = Bills.query.get(bill)

                    else:

                        vals = ['bdesc', 'bamt', 'bdate', 'pamt', 'pdate', 'account',
                                'bref', 'ckmemo', 'ctype', 'thiscomp', 'ddate', 'billacct']
                        a = list(range(len(vals)))
                        i = 0
                        for v in vals:
                            a[i] = request.values.get(v)
                            i = i+1

                        if a[4] is None:
                            a[4] = today
                        bdol = d2s(a[1])
                        pdol = d2s(a[3])
                        modata.Company = a[9]
                        cdat = People.query.filter((People.Company == a[9]) & ((People.Ptype == 'Vendor') | (
                            People.Ptype == 'TowCo') | (People.Ptype == 'Overseas'))).first()
                        if cdat is not None:
                            modata.Pid = cdat.id
                        else:
                            cdat = People.query.filter(People.Company == modata.Company).first()
                            if cdat is not None:
                                modata.Pid = cdat.id
                            else:
                                modata.Pid = 0
                        modata.Memo = a[7]
                        modata.Description = a[0]
                        modata.bAmount = bdol
                        modata.bDate = a[2]
                        modata.dDate = a[10]
                        modata.pAmount = pdol
                        modata.pDate = a[4]
                        modata.pAccount = a[5]
                        modata.Ref = a[6]
                        if modata.Status == 'Paying':
                            if float(bdol) == float(pdol):
                                modata.Status = 'Paid'
                            else:
                                modata.Status = 'PartPaid'

                        modata.User = username
                        modata.Co = a[8]
                        cache = modata.Cache
                        base = modata.Jo
                        filename2 = f'Source_{base}_c{str(cache)}.pdf'
                        docref = f'tmp/{scac}/data/vbills/{filename2}'
                        modata.Original = filename2
                        acctname = a[11]
                        acctco = a[8]
                        modata.bAccount = acctname
                        acdat1 = Accounts.query.filter((Accounts.Name == acctname) & (Accounts.Co == acctco)).first()
                        if acdat1 is not None:
                            modata.bType = acdat1.Type
                            modata.bCat = acdat1.Category
                            modata.bSubcat = acdat1.Subcategory
                            modata.Recurring = acdat1.id
                        db.session.commit()
                        # Check that JO still consistent with modification
                        co=modata.Co
                        jo=modata.Jo
                        #Check to see if uploaded file and created JO before inputting data...need to update the JO
                        if jo[0] == 'X':
                            jo = co+jo[1:]
                            modata.Jo = jo
                            db.session.commit()
                        ccode=jo[0]
                        if co is None:
                            co = ccode
                        if jo is None:
                            ccode = co[0]
                        if co != ccode:
                            # Have to change all the Gledger items with old jo to new jo
                            Gledger.query.filter(Gledger.Tcode==jo).delete()
                            jo=jo.replace(ccode,co)
                            modata.Jo=jo
                            db.session.commit()
                        print('line302:',modata.Jo,modata.bAccount,modata.pAccount)
                        gledger_write('newbill',modata.Jo,modata.bAccount,modata.pAccount)

                if modal == 1:
                    calendar = 1
                    modlink = 0

            if peep > 0:
                modata = People.query.get(peep)
                modata.Ptype = 'Vendor'
                vals = ['company', 'addr1', 'addr2', 'tid',
                        'tel', 'email', 'date1', 'ctype', 'billacct']
                a = list(range(len(vals)))
                i = 0
                for v in vals:
                    a[i] = request.values.get(v)
                    i = i+1
                modata.Company = a[0]
                modata.Addr1 = a[1]
                modata.Addr2 = a[2]
                modata.Idnumber = a[3]
                modata.Telephone = a[4]
                modata.Email = a[5]
                modata.Date1 = a[6]
                modata.Idtype = a[7]
                diva = Divisions.query.filter(Divisions.Co == a[7]).first()
                if diva is not None:
                    modata.First = diva.Color
                aname = a[8]
                if aname is not None:
                    aname = aname.strip()
                else:
                    aname = ''
                modata.Associate1 = aname
                aadat = Accounts.query.filter((Accounts.Name == aname) & (Accounts.Co == a[7])).first()
                if aadat is not None:
                    modata.Accountid = aadat.id
                    modata.Associate2 = aadat.Type
                    modata.Temp1 = aadat.Category
                    modata.Temp2 = aadat.Subcategory
                    modata.Idtype = aadat.Co
                db.session.commit()
                err.append('Continue New Entry for Entity ID ' + str(modata.id))

                if update is not None:
                    err.append('Modification to Entity ID ' + str(modata.id) + ' completed.')
                    print('modlink value',modlink)
                    # if modlink=8 then we are updating vendor while entering a new bill, time to transition back to the bill
                    if modlink == 8:
                        modlink = 44
                        cdat = People.query.get(peep)
                        print('cdat1',cdat.Company,modlink)
                        if cdat is not None:
                                # Set account defaults for this vendor
                            ccode = cdat.Idtype
                            expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co == ccode)).all()
                            print('Color Here',ccode)
                            diva = Divisions.query.filter(Divisions.Co == ccode).first()
                            if diva is not None:
                                modata.First = diva.Color
                                db.session.commit()
                        peep = 0

                    else:
                        modlink = 0
                else:
                    leftsize = 8
                    bval = request.values.get('ctype')
                    if bval is not None:
                        modata.Idtype = bval
                        db.session.commit()
                        expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(bval))).all()


                # And now update the crossover to Storage in case the Company info changed:
                cross = Bills.query.filter(Bills.Pid == peep)
                for cros in cross:
                    cros.Company = a[0]
                db.session.commit()

            # create return status
            if update is not None and modlink != 6 and modlink != 44:
                modlink = 0
                leftscreen = 1
                indat = '0'

            print('leftscreen on exit',leftscreen)

# ____________________________________________________________________________________________________________________B.UpdateDatabasesSection

        bdata, cdata = dataget_B(hv[1],hv[0])
# ____________________________________________________________________________________________________________________B.SearchFilters

        if modlink < 5:
            bill, peep, numchecked = numcheck(2, bdata, cdata, 0, 0, 0, ['bill', 'peep'])
        else:
            numchecked = 0

        if uploadS is not None:
            print('Using uploadS')
            if bill > 0  and numchecked == 1:
                bdat = Bills.query.get(bill)
                jo = bdat.Jo
                cache = bdat.Cache
                filename2 = f'Source_{jo}_c{str(cache)}.pdf'
                err.append(f'File uploaded as {filename2}')
                #Provide a file name for the upload and store message:
                edat = LastMessage.query.filter(LastMessage.User == username).first()
                if edat is not None:
                    edat.Err = json.dumps(err)
                    db.session.commit()
                else:
                    input = LastMessage(User=username, Err=json.dumps(err))
                    db.session.add(input)
                    db.session.commit()

                modlink = 70
                leftscreen = 1
                mm3 = 0
            else:
                err.append('No Bill Selected for Source Upload')
                err.append('Select One Box')
# ____________________________________________________________________________________________________________________E.SearchFilters


# ____________________________________________________________________________________________________________________B.Viewers
        if viewo == 1 and numchecked == 1:
            if bill > 0:
                modata = Bills.query.get(bill)
                viewtype = 'source'
                hv[2] = viewtype
                if modata.Original is not None:
                    if len(modata.Original) > 5:
                        docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                        leftscreen = 0
                        leftsize = 8
                        modlink = 0
                        err.append('Viewing document '+docref)

        if viewo == 1 and numchecked != 1:
            err.append('Must check exactly one box to view source file')

        if viewck == 1 and numchecked == 1:
            if bill > 0:
                modata = Bills.query.get(bill)
                viewtype = 'check'
                hv[2] = viewtype
                if modata.Code1 is not None:
                    if len(modata.Code1) > 5:
                        docref = f'tmp/{scac}/data/vchecks/{modata.Code1}'
                        leftscreen = 0
                        leftsize = 8
                        modlink = 0
                        err.append('Viewing check '+docref)

        if viewck == 1 and numchecked != 1:
            err.append('Must check exactly one box to view checks')

# ____________________________________________________________________________________________________________________E.Viewers
# ____________________________________________________________________________________________________________________B.Modify Entries
        if (modify is not None or vmod is not None) and numchecked == 1:
            leftsize = 8

            if bill > 0:
                modata = Bills.query.get(bill)
                filesel = request.values.get('FileSel')
                fdata = myoslist(bill_path)
                fdata.sort()
                vendor = modata.Company
                co = modata.Co
                vdat = People.query.filter((People.Ptype == 'Vendor') & (People.Company == vendor)).first()
                # co = vdat.Idtype
                if vdat is not None:
                    defexp = modata.bAccount
                    if defexp is not None:
                        if len(defexp) < 5:
                            defexp = vdat.Associate1
                    else:
                        defexp = vdat.Associate1
                else:
                    defexp = None
                modata.bAccount = defexp
                duedate = modata.dDate
                if duedate is None:
                    modata.dDate = modata.bDate
                paccount = modata.pAccount
                print(paccount)
                if paccount is None:
                    lastbill = Bills.query.filter((Bills.Company == modata.Company) & (Bills.id != modata.id)).first()
                    if lastbill is not None:
                        modata.pAccount = lastbill.pAccount
                db.session.commit()
                modata = Bills.query.get(bill)

                expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co==co)).all()
                leftsize = 8
                leftscreen = 0
                docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                modlink = 7
                if vmod is not None:
                    err.append('There is no document available for this selection')
                    if modata.Original is not None:
                        if len(modata.Original) > 5:
                            leftscreen = 0
                            docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                            doctxt = txtfile(docref)
                            err.append('All is well')

            if peep > 0:
                modata = People.query.get(peep)
                modlink = 9
                co = modata.Idtype
                if co is None:
                    co = 'F'
                    modata.Idtype = co
                    db.session.commit()
                    modata = People.query.get(peep)

                expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(co))).all()
                # peephold=peep
                if vmod is not None:
                    err.append('There is no document available for this selection')

        # Modification coming from calendar
        if modify2 is not None:
            bill = nonone(modify2)
            modata = Bills.query.get(bill)
            modlink = 7
            leftsize = 8

# ____________________________________________________________________________________________________________________E.Modify Entries
# ____________________________________________________________________________________________________________________B.Add Entries

        if addE is not None:
            leftsize = 8
            modlink = 9
            # Remove any new starts that were not completed
            People.query.filter(People.Ptype=='NewVendor').delete()
            # We will create a blank line and simply modify that by updating:
            input = People(Company='', First=None, Middle=None, Last=None, Addr1='', Addr2='', Addr3='', Idtype=None, Idnumber='', Telephone='',
                           Email='', Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='NewVendor', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter(People.Ptype == 'NewVendor').first()
            peep = modata.id
            err.append('Enter Data for New Entity')
            expdata = Accounts.query.filter(Accounts.Type == 'Expense').all()

        if addE2 is not None:
            leftsize = 8
            modlink = 8
            # We will create a blank line and simply modify that by updating:
            hlist = hv_capture(['thiscomp','ctype','billacct','bamt','bdate','ddate','bdesc'])
            hv = hv[0:2]+hlist
            print(hv)
            # We will create a blank line and simply modify that by updating:
            input = People(Company='', First=None, Middle=None, Last=None, Addr1='', Addr2='', Addr3='', Idtype=None, Idnumber='', Telephone='',
                           Email='', Associate1=None, Associate2=None, Date1=today, Date2=None, Original=None, Ptype='NewVendor', Temp1=None, Temp2=None, Accountid=None)
            db.session.add(input)
            db.session.commit()
            modata = People.query.filter(People.Ptype == 'NewVendor').first()
            peep = modata.id
            err.append('Enter Data for New Entity')
            expdata = Accounts.query.filter(Accounts.Type == 'Expense').all()

# ____________________________________________________________________________________________________________________E.Add Entries

# ____________________________________________________________________________________________________________________B.Delete an Entry
        if deletehit is not None and numchecked >= 1:
            if bill > 0:
                bdat = Bills.query.get(bill)
                try:
                    orderid = nonone(bdat.Temp2)
                    adat = Autos.query.get(orderid)
                    if adat is not None:
                        adata = Autos.query.filter(Autos.Orderid == adat.Orderid).all()
                        for dat in adata:
                            dat.Status = 'Novo'
                except:
                    err.append('Delete problem')
                jo = bdat.Jo
                Gledger.query.filter(Gledger.Tcode==jo).delete()
                Bills.query.filter(Bills.id == bill).delete()
                db.session.commit()
            if peep > 0:
                peepvec = numcheckvec(cdata, 'peep')
                for peep in peepvec:
                    People.query.filter(People.id == peep).delete()
                    db.session.commit()

            bdata = Bills.query.order_by(Bills.bDate).all()
            cdata = People.query.filter((People.Ptype == 'Vendor') | (
                People.Ptype == 'TowCo')).order_by(People.Company).all()

        if deletehit is not None and numchecked == 0:
            err.append('Must have at least one item checked to use this option')
# ____________________________________________________________________________________________________________________E.Delete an Entry
# ____________________________________________________________________________________________________________________B.NewXfer.Billing
        if newxfer == 1:
            modlink = 3
            err.append('Select Source Document from List')
            leftscreen = 0
            expdata = Accounts.query.filter((Accounts.Type == 'Bank') | (Accounts.Type == 'Equity')).order_by(Accounts.Name).all()
            vdata = [today, today, '', '']

        if newxfer is None and modlink == 3:

            leftscreen = 0
            bdate = request.values.get('bdate')
            ddate = request.values.get('bdate')
            xamt = request.values.get('xamt')
            new_desc = request.values.get('desc')
            xferfrom = request.values.get('fromacct')
            xferto = request.values.get('toacct')
            if xamt is None:
                xamt = '0.00'
            vdata = [bdate, ddate, xamt, new_desc, xferfrom, xferto]
            print(vdata)
            expdata = Accounts.query.filter((Accounts.Type == 'Bank') | (Accounts.Type == 'Equity')).order_by(
                Accounts.Name).all()

        if thisxfer is not None:
            modlink = 0

            sdate = request.values.get('bdate')
            if sdate is None or sdate == '':
                sdate = today

            fromacct = request.values.get('fromacct')
            toacct = request.values.get('toacct')
            xamt = request.values.get('xamt')
            xamt = d2s(xamt)
            xdesc = request.values.get('xdesc')
            btype = 'XFER'
            bclass = 'Non-Expense'
            nextjo = newjo(billxfrcode, today)

            input = Bills(Jo=nextjo, Pid=0, Company=toacct, Memo=None, Description=xdesc, bAmount=xamt, Status='Paid', Cache=0, Original=None,
                             Ref=None, bDate=sdate, pDate=sdate, pAmount=xamt, pMulti=None, pAccount=fromacct, bAccount=toacct, bType=btype,
                             bCat=bclass, bSubcat='', Link=None, User=username, Co=None, Temp1=None, Temp2=None, Recurring=0, dDate=today,
                             pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0)

            db.session.add(input)
            db.session.commit()

            modata = Bills.query.filter(Bills.Jo == nextjo).first()
            gledger_write('xfer',nextjo,fromacct,toacct)
            bill = modata.id
            leftscreen = 1
            err.append('All is well')
            bdata = Bills.query.order_by(Bills.bDate).all()
        # ____________________________________________________________________________________________________________________E.NewXfer.Billing
        if copy == 1:
            if bill > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                bdat = Bills.query.get(bill)
                thisdate = bdat.bDate
                nextdate = thisdate + datetime.timedelta(days=30)
                nextjo = newjo(billexpcode, today)
                input = Bills(Jo=nextjo, Pid=bdat.Pid, Company=bdat.Company, Memo=bdat.Memo, Description=bdat.Description, bAmount=bdat.bAmount, Status=bdat.Status, Cache=0, Original=bdat.Original,
                                 Ref=bdat.Ref, bDate=nextdate, pDate=None, pAmount='0.00', pMulti=None, pAccount=bdat.pAccount, bAccount=bdat.bAccount, bType=bdat.bType,
                                 bCat=bdat.bCat, bSubcat=bdat.bSubcat, Link=None, User=username, Co=bdat.Co, Temp1=None, Temp2='Copy', Recurring=0, dDate=today, pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0)
                db.session.add(input)
                db.session.commit()

                gledger_write('newbill', nextjo, bdat.bAccount, bdat.pAccount)

            elif peep > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                pdat = People.query.get(peep)
                input = People(Company=pdat.Company, First=pdat.First, Middle='Copy', Last=None, Addr1=pdat.Addr1, Addr2=pdat.Addr2, Addr3=pdat.Addr3,
                               Idtype=pdat.Idtype, Idnumber=pdat.Idnumber, Telephone=pdat.Telephone,
                               Email=pdat.Email, Associate1=pdat.Associate1, Associate2=pdat.Associate2, Date1=today, Date2=None, Original=None,
                               Ptype='Vendor', Temp1=pdat.Temp1, Temp2=pdat.Temp2, Accountid=pdat.Accountid)
                db.session.add(input)
                db.session.commit()

            else:
                err.append('Must select one item to use this function')

        if copy12 is not None:
            if bill > 0 and numchecked == 1:
                # sdate=today.strftime('%Y-%m-%d')
                bdat = Bills.query.get(bill)
                thisdate = bdat.bDate
                year = thisdate.year
                month = thisdate.month
                day = thisdate.day
                while month < 12:
                    month = month+1
                    nextdate = datetime.datetime(year, month, day)
                    nextjo = newjo(billexptype, today)
                    input = Bills(Jo=nextjo, Pid=bdat.Pid, Company=bdat.Company, Memo=bdat.Memo, Description=bdat.Description, bAmount=bdat.bAmount, Status=bdat.Status, Cache=0, Original=bdat.Original,
                                     Ref=bdat.Ref, bDate=nextdate, pDate=None, pAmount='0.00', pMulti=None, pAccount=bdat.pAccount, bAccount=bdat.bAccount, bType=bdat.bType,
                                     bCat=bdat.bCat, bSubcat=bdat.bSubcat, Link=None, User=username, Co=bdat.Co, Temp1=None, Temp2='Copy', Recurring=0, dDate=today, pAmount2='0.00', pDate2=None, Code1 = None, Code2=None, CkCache=0, QBi=0)
                    db.session.add(input)
                    db.session.commit()

                    gledger_write('newbill',nextjo,bdat.bAccount,bdat.pAccount)

        if qpay is not None:
            if bill > 0 and numchecked == 1:
                bdat = Bills.query.get(bill)
                bdat.pDate = bdat.bDate
                bdat.pAmount = bdat.bAmount
                bdat.Temp2 = ''
                bdat.Status = 'Paid'
                pacct = bdat.pAccount
                if pacct is None:
                    pacct = get_def_bank(bdat)
                elif pacct == '0' or pacct == '1' or pacct == 0 or pacct == 1:
                    pacct = get_def_bank(bdat)
                bdat.pAccount = pacct
                db.session.commit()

# ____________________________________________________________________________________________________________________B.NewJob
        if newbill is not None:
            err.append('Select Source Document from List')
            modlink = 4
            leftscreen = 0
            expdata = Accounts.query.filter((Accounts.Type == 'Expense') | (Accounts.Type == 'CC')).order_by(Accounts.Name).all()
            vdata = [today, today, '', '']



        if newbill is None and (modlink == 4 or modlink == 44):
            leftsize = 8
            leftscreen = 0
            bdate = request.values.get('bdate')
            ddate = request.values.get('bdate')

            if modlink == 4:
                thiscompany = request.values.get('thiscomp')
                cdat = People.query.filter((People.Company == thiscompany) & (
                    (People.Ptype == 'Vendor') | (People.Ptype == 'TowCo'))).first()
                print(cdat.Idtype)
                ddat = Divisions.query.filter(Divisions.Co==cdat.Idtype).first()
                if ddat is not None:
                    err.append(f'Loading data for {thiscompany} Defaults')
                    err.append(f'Bill for {cdat.Idtype}: {ddat.Name}')

            else:
                modlink = 4 #reset the vondor feed back to bill feed

            if cdat is not None:
                print(cdat.Company, peep, cdat.Idtype, cdat.Associate1)
                # Set account defaults for this vendor
                ccode = cdat.Idtype
                cchg = request.values.get('ctype')
                ddat = Divisions.query.filter(Divisions.Co ==cchg).first()
                if ddat is not None:
                    cdat.Idtype = ddat.Co
                    ccode = ddat.Co
                expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co == ccode)).all()

            # Get information from previous bill paid by the vendor

                ldata = Bills.query.filter(Bills.Company == cdat.Company).all()
                if ldata:
                    ldat = ldata[-1]
                    last_desc = ldat.Description
                    last_memo = ldat.Memo
                    new_desc = ''
                    new_memo = ''
                    for i, x in enumerate(monlvec):
                        if i == 11:
                            k = 0
                        else:
                            k = i+1
                        if x in last_desc:
                            new_desc = last_desc.replace(x, monlvec[k])
                        if x in last_memo:
                            new_memo = last_memo.replace(x, monlvec[k])
                    last_amt = d2s(ldat.bAmount)
                    # last_date=datetime.datetime.strptime(ldat.bDate,"%Y-%m-%d")+datetime.timedelta(days=30)

                    last_date = ldat.bDate
                    if last_date is not None:
                        last_date = last_date.strftime("%Y-%m-%d")
                        err.append(f'The last bill to this vendor was written on {last_date} for ${last_amt}')
                    else:
                        last_date = 'None'
                        err.append(f'No Bills Recorded for this Vendor')
                    vdata = [bdate, ddate, last_amt, new_desc]
                else:
                    # if not then get the category info from the vendor data
                    vdata = [bdate, ddate, '0.00', '']
            else:
                expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co == ccode)).all()

        if thisbill is not None:
            modlink = 0
            # Create the new database entry for the source document
            sdate = request.values.get('bdate')
            print('bdate:', sdate)
            if sdate is None or sdate == '':
                sdate = today

            thiscomp = request.values.get('thiscomp')
            cdat = People.query.filter((People.Company == thiscompany) & (
                (People.Ptype == 'Vendor') | (People.Ptype == 'TowCo'))).first()
            if cdat is not None:
                acomp = cdat.Company
                cid = cdat.Accountid
                aid = cdat.id
                acdat = Accounts.query.filter(Accounts.id == cid).first()
                if acdat is not None:
                    baccount = acdat.Name
                    category = acdat.Category
                    subcat = acdat.Subcategory
                    descript = acdat.Description
                    btype = acdat.Type
                else:
                    category = 'NAY'
                    subcat = 'NAY'
                    descript = ''
                    btype = ''
                    baccount = ''
            else:
                acomp = None
                aid = None
                category = 'NAY'
                subcat = 'NAY'
                descript = ''
                btype = ''
                baccount = ''
                docref = f'tmp/{scac}/data/vbills/' + newfile

            bdesc = request.values.get('bdesc')
            bamt = request.values.get('bamt')
            bamt = d2s(bamt)
            bcomp = request.values.get('bcomp')
            cco = request.values.get('ctype')
            print(f'Getting nextjo with {cco} and {today}')
            nextjo = newjo(cco+'B', today)
            account = request.values.get('crataccount')
            baccount = request.values.get('billacct')
            bfile = os.path.basename(docref)

            input = Bills(Jo=nextjo, Pid=aid, Company=acomp, Memo='', Description=bdesc, bAmount=bamt, Status='Unpaid', Cache=0, Original=bfile,
                             Ref='', bDate=sdate, pDate=today, pAmount='0.00', pMulti=None, pAccount=account, bAccount=baccount, bType=btype,
                             bCat=category, bSubcat=subcat, Link=None, User=username, Co=cco, Temp1=None, Temp2=None, Recurring=0, dDate=today,
                             pAmount2='0.00', pDate2=None, Code1 = None, Code2=None, CkCache=0, QBi=0)

            db.session.add(input)
            db.session.commit()
            gledger_write('newbill',nextjo,baccount,account)


            # reget because we need the bill unique id number in the document
            modata = Bills.query.filter(Bills.Jo == nextjo).first()
            csize = People.query.filter((People.Ptype == 'Vendor') | (
                People.Ptype == 'TowCo')).order_by(People.Company).all()
            bill = modata.id
            leftscreen = 1
            leftsize = 10
            err.append('All is well')
            bdata = Bills.query.order_by(Bills.bDate).all()
# ____________________________________________________________________________________________________________________E.New Bill
        if unpay == 1:
            if numchecked == 1 and bill > 0:
                myb = Bills.query.get(bill)
                myb.Status = 'Unpaid'
                myb.pAmount = '0.00'
                db.session.commit()
                Gledger.query.filter((Gledger.Tcode == myb.Jo) & (Gledger.Type == 'AP')).delete()
                err.append(f'Unpay Bill {myb.Jo} and remove from register')
            else:
                err.append('Must select one Bill to Unpay')

        if paybill is not None or paybill2 is not None:
            exit = 0

            if numchecked == 1 and bill > 0:
                myb = Bills.query.get(bill)
                status = myb.Status
                if status != 'Paid':
                    myb.pDate = today
                    myb.pAmount = myb.bAmount
                    pacct = myb.pAccount
                    if pacct is None:
                        pacct = get_def_bank(myb)
                    elif len(pacct) < 4:
                        pacct = get_def_bank(myb)
                    myb.pAccount = pacct
                    # Get the next check in line for this account:
                    cknum = next_check(pacct,myb.id)
                    myb.Ref = cknum

                    myb.Status = 'Paying'
                    db.session.commit()
                    co = myb.Co
                    expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(co))).all()
                else:
                    err.append('Bill for single bill pay has been paid already')
                    exit = 1

            if numchecked > 1 and bill > 0:
                # See how many bills are to be paid together
                nbill = 0
                bill_ids = []
                total = 0
                for data in bdata:
                    testone = request.values.get('bill'+str(data.id))
                    if testone:
                        myb = Bills.query.get(data.id)
                        try:
                            nbill = nbill+1
                            bamt = myb.bAmount
                            bamt = d2s(bamt)
                            amt = float(bamt)
                            total = total+amt
                            bill_ids.append(data.id)
                        except:
                            err.append('Some checked bills of multi-pay already paid')
                            exit = 1
                if exit == 0 and nbill > 1:
                    # Create link code
                    linkcode = 'Link'
                    # Create a master reference from first bill
                    masterbill = bill_ids[0]
                    myb = Bills.query.get(masterbill)
                    masterref = myb.Ref
                    masteracct = myb.pAccount
                    masterdesc = ''
                    masterpid = myb.Pid
                    masterpayee = myb.Company
                    co = myb.Co
                    expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(co))).all()
                    if masteracct is None or len(masteracct) < 4:
                        masteracct = 'Industrial Bank'
                    for bill in bill_ids:
                        myb = Bills.query.get(bill)
                        linkcode = linkcode+'+'+str(bill)
                        try:
                            descline = 'Bill ID:' + str(myb.id) + ' Billcode: ' + \
                                myb.Jo + ' Amount: ' + str(myb.bAmount) + '\n'
                        except:
                            descline = 'Bill ID:' + str(myb.id)
                        masterdesc = masterdesc+descline
                    for bill in bill_ids:
                        myb = Bills.query.get(bill)
                        myb.Status = 'Paid-M'
                        myb.Link = linkcode
                        myb.pDate = today
                        myb.pAmount = myb.bAmount
                        myb.pMulti = "{:.2f}".format(total)
                        myb.Ref = masterref
                        myb.pAccount = masteracct
                        myb.Description = masterdesc
                        myb.Pid = masterpid
                        myb.Company = masterpayee
                        db.session.commit()
                        jo = myb.Jo
                        gledger_write('paybill',jo,myb.bAccount,myb.pAccount)

            if numchecked == 0 or bill == 0:
                err.append('Must check at least one bill for this selection')
                err.append(f'Numchecked = {numchecked}')
                exit = 1

            if exit == 0:
                modlink = 7
                leftsize = 8
                modata = Bills.query.get(bill)
                docref = f'tmp/{scac}/data/vbills/{modata.Original}'
                if os.path.isfile(addpath(docref)):
                    leftscreen = 0
                    err.append(f'Paying Bill {modata.Jo}')
                else:
                    leftscreen = 1
                    err.append(f'Paying Bill {modata.Jo}')
                    err.append('Bill has no source document')
                pb = 1
            else:
                err.append('Could not complete billpay')
                leftside = 8
                modlink = 0
                leftscreen = 1

            bdata = Bills.query.order_by(Bills.bDate).all()

        if printck is not None or modlink == 6 or modlink == 12 or paynmake is not None or indat != '0':
            fdata = myoslist(bill_path)
            fdata.sort()
            if paynmake is not None:
                bill = nonone(paynmake)
                bdat = Bills.query.get(bill)
                bdat.Status = 'Paid'
                bdat.pAmount = bdat.bAmount
                ckref = request.values.get('ckref'+str(bill))
                bdat.Ref = ckref
                db.session.commit()
                numchecked = 1

            if indat != '0':
                bdat = Bills.query.filter(Bills.Jo == indat).first()
                bill = bdat.id
                modlink = 6

            if (numchecked == 1 and bill > 0) or modlink == 6 or modlink == 12:
                exit = 0
                bdat = Bills.query.get(bill)
                ifxfer = bdat.bType
                if ifxfer == 'XFER':
                    acct_to = bdat.Company
                    acdat = Accounts.query.filter(Accounts.Name == acct_to).first()
                    pdat = People.query.filter((People.Ptype == 'Vendor') &
                                               (People.Company == acdat.Payee)).first()
                else:
                    pdat = People.query.get(bdat.Pid)

                if bdat.Status == 'Unpaid':
                    bdat.Status = 'Paid'
                    db.session.commit()
                if bdat.Status == 'Paid-M':
                    linkcode = bdat.Link
                    sbdata = Bills.query.filter(Bills.Link == linkcode)
                    link = linkcode.replace('Link+', '')
                    items = link.split('+')
                    links = []
                    [links.append(int(item)) for item in items]
                else:
                    links = 0
                    sbdata = 0

                if exit == 0:
                    ckcache = bdat.CkCache
                    if ckcache is None or ckcache == 0:
                        ckcache = 1
                    last_ckfile = f'Check_{bdat.Jo}_{bdat.Ref}_c{str(ckcache-1)}.pdf'
                    ckfile = f'Check_{bdat.Jo}_{bdat.Ref}_c{str(ckcache)}.pdf'
                    docref = f'tmp/{scac}/data/vchecks/{ckfile}'
                    bdat.Code1 = ckfile
                    ckcache = ckcache+1
                    bdat.CkCache = ckcache
                    pamount = bdat.pAmount
                    if pamount == '0.00':
                        bdat.pAmount = bdat.bAmount
                    db.session.commit()

                    from writechecks import writechecks

                    writechecks(bdat, pdat, docref, sbdata, links)
                    modlink = 6
                    leftsize = 8
                    leftscreen = 0
                    co = bdat.Co
                    expdata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Co.contains(co))).all()
                    db.session.commit()

                    pacct=bdat.pAccount
                    if pacct is not None and pacct != '0':
                        gledger_write('paybill',bdat.Jo,bdat.bAccount,bdat.pAccount)
                    else:
                        err.append('No Account for Fund Withdrawal')

                    bdata = Bills.query.order_by(Bills.bDate).all()
                    cdata = People.query.filter((People.Ptype == 'Vendor') | (People.Ptype == 'TowCo') | (
                        People.Ptype == 'Overseas')).order_by(People.Company).all()
                    modata = Bills.query.get(bill)
                    pb = 1
                    #Attempt to remove the previous cache copy:
                    try:
                        last_file = addpath(f'tmp/{scac}/data/vchecks/{last_ckfile}')
                        os.remove(last_file)
                    except:
                        print(f'Could nor remove {last_file}')

            else:
                err.append('Must select exactly 1 Bill box to use this option.')


# ____________________________________________________________________________________________________________________B.Matching
        if match is not None:
            if bill > 0 and peep > 0 and numchecked == 2:
                myo = Bills.query.get(bill)
                myp = People.query.get(peep)
                myo.Pid = peep
                myo.Company = myp.Company
                myo.Description = myp.Associate1
                db.session.commit()
            if numchecked != 2:
                err.append('Must select exactly 2 boxes to use this option.')
# ____________________________________________________________________________________________________________________E.Matching
# ____________________________________________________________________________________________________________________B.Calendar.Billing
        if calendar is not None or calupdate is not None:
            leftscreen = 2
            if calupdate is not None:
                waft = request.values.get('waft')
                wbef = request.values.get('wbef')
                waft = nonone(waft)
                wbef = nonone(wbef)
                nweeks = [wbef, waft]
            else:
                nweeks = [2, 2]
            caldays, daylist, weeksum = calendar7_weeks('Billing', nweeks)

            if calupdate is not None:
                for j in range(len(daylist)):
                    ilist = daylist[j]
                    if ilist:
                        tid = ilist[0]
                        fnum = 'note'+str(tid)
                        fput = request.values.get(fnum)
                        if len(fput) > 3:
                            billno = f'{scac}_Bill_{str(tid)}'
                            input = ChalkBoard(Jo=billno, creator=username,
                                               comments=fput, status=1)
                            db.session.add(input)
                            db.session.commit()

                caldays, daylist, weeksum = calendar7_weeks('Billing', nweeks)
# ____________________________________________________________________________________________________________________E.Calendar.Billing

        if (modlink > 0 and bill > 0) or (modlink > 0 and peep > 0) or leftscreen == 0:
            leftsize = 8
        elif leftscreen == 2:
            leftsize = 10
        else:
            leftsize = 10
    else:
        err = []
        hv = [0]*20
        hv[0] = 'X'
        hv[1] = '1'
        username = session['username'].capitalize()
        # ____________________________________________________________________________________________________________________B.BillingNotPost
        from viewfuncs import init_tabdata, timedata, nonone, init_billing_zero, init_billing_blank, nononef, erud, dataget_B
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        bill, peep, cache, modata, modlink, fdata, adata, cdat, pb, passdata, vdata, caldays, daylist, weeksum, nweeks = init_billing_zero()
        filesel = ''
        docref = ' '
        doctxt = ' '
        leftscreen = 1
        leftsize = 10
        addjobselect = 0
        dlist = ['on']*2
        dlist[1] = 'off'
        jobdata = 0
        modal = 0
        expdata = 0
        divdat = Divisions.query.all()

        err.append('All is well')
    leftsize = 8
    rightsize = 12 - leftsize
    today = datetime.date.today()
    critday = datetime.date.today()+datetime.timedelta(days=7)
    acdata = Accounts.query.filter((Accounts.Type == 'Bank') | (Accounts.Type == 'CC')).all()
    bdata, cdata = dataget_B(hv[1],hv[0])
    err = erud(err)

    return username, divdat, hv, bdata, cdata, bill, peep, err, modata, adata, acdata, expdata, modlink, caldays, daylist, weeksum, nweeks, addjobselect, jobdata, modal, dlist, fdata, today, cdat, pb, critday, vdata, leftscreen, docref, doctxt, leftsize, cache, filesel
