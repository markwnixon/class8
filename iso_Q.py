from runmain import app, db
from flask import render_template, flash, redirect, url_for, session, logging, request
from requests import get
from CCC_system_setup import apikeys
from CCC_system_setup import myoslist, addpath, tpath, companydata, usernames, passwords, scac, imap_url, accessorials, signoff
from viewfuncs import d2s, d1s
import imaplib, email
import math
import re

import datetime
from models import Quotes
from send_mimemail import send_mimemail

API_KEY_GEO = apikeys['gkey']
API_KEY_DIS = apikeys['dkey']
cdata = companydata()

date_y4=re.compile(r'([1-9]|0[1-9]|[12][0-9]|3[01]) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})')

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,True)

def search(key,value,con):
    result,data=con.search(None,key,'"{}"'.format(value))
    return data

def search_from_date(key,value,con,datefrom):
    result,data=con.search( None, '(SENTSINCE {0})'.format(datefrom) , key, '"{}"'.format(value) )
    return data

def get_emails(result_bytes,con):
    msgs=[]
    for num in result_bytes[0].split():
        typ,data=con.fetch(num,'(RFC822)')
        msgs.append(data)
    return msgs

def get_date(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            try:
                part = response_part[1].decode('utf-8')
                msg = email.message_from_string(part)
                date=msg['Date']
            except:
                date=None
    return date

def get_subject(data):
    subject = 'none'
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            subject=msg['Subject']
    return subject

def get_from(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1]
            try:
                part = part.decode('utf-8')
                msg = email.message_from_string(part)
                thisfrom=msg['From']
                return thisfrom
            except:
                return 'Nonefound'

def get_msgs():
    username = usernames['quot']
    password = passwords['quot']
    dayback = 100
    #datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(username, password)
    con.select('INBOX')
    result, data = con.search(None,'ALL')
    msgs = get_emails(data, con)
    return msgs


def compact(body):
    newbody = ''
    blines = body.splitlines()
    for line in blines:
        #Remove non-ascii characters
        line = re.sub(r'[^\x00-\x7F]+', ' ', line)
        line = re.sub(r'=[A-Z,0-9][A-Z,0-9]', '', line)
        if len(line.strip())>1:
            if 'Forwarded Message' in line or 'Subject:' in line or 'Date:' in line or 'To:' in line or 'CC:' in line or 'From:' in line or 'Content-Type' in line or 'Content-Transfer' in line:
                print('Line from FWD Preamble')
            else:
                newbody = newbody + line +'\n' + '<br>'
    return newbody

def hard_decode(raw):
    raw = str(raw)
    rawl = raw.splitlines()
    appendit = 0
    ebody=''
    efrom=''
    edate=''
    for line in rawl:
        test = line[0:5]
        line = re.sub(r'[^\x00-\x7F]+', ' ', line)
        line = re.sub(r'=[A-Z,0-9][A-Z,0-9]', '', line)
        line = line.replace('=09','')
        if 'Subj' in test:
            subject = line.split('Subject:')[1]
            subject = subject.replace('Fwd:','')
            subject = subject.strip()
            print(f'Subject:{subject}')
        if 'From' in test and '@' in line and 'firsteagle' not in line and 'onestop' not in line:
            print('efrom',line)
            efrom = line.split('From:')[1]
            efrom = efrom.strip()
            print(f'From:{efrom}')
        if 'Date' in test:
            edate = line.split('Date:')[1]
            edate = edate.strip()
            print(f'Date:{edate}')
        if 'Content-Type:' in line and 'plain' in line:
            print(f'BodyStart:{line}')
            appendit = 1
        if 'Content-Type:' in line and 'html' in line:
            print(f'BodyStop:{line}')
            appendit = 0
        if appendit == 1:
            line = line.strip()
            if len(line)>0:
                ebody=ebody+line+'\n'
    #print(f'ebody={ebody}')
    return subject,efrom,edate,ebody


def add_quote_emails():
    username = usernames['quot']
    password = passwords['quot']
    dayback = 7
    datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(username, password)
    con.select('INBOX')
    result, data = con.search(None,'ALL')
    msgs = get_emails(data, con)
    #msgs = get_emails(search_from_date('TO', usernames['quot'], con, datefrom), con)

    for j, msg in enumerate(msgs):
        raw = email.message_from_bytes(msg[0][1])
        body = get_body(raw)
        try:
            body = body.decode('utf-8')
            getdate = get_date(msg)
            thisfrom = get_from(msg)
            subject = get_subject(msg)
            print(f'For email {j}: Status OK')
            # Check to see if this is a forwarded message in which case use a hard decode:
            if 'Fwd:' in subject or 'Fwd=' in subject:
                print(f'For email {j}: Fwd Message Use Hard Decode')
                subject, thisfrom, getdate, body = hard_decode(raw)

        except:
            print(f'For email {j}: Decode failed')
            subject, thisfrom, getdate, body = hard_decode(raw)

        if getdate is not None:
            print('getdate=',getdate)
            datep = date_y4.findall(getdate)
            if datep:
                print(datep)
                test = datep[0]
                print(test)
                print(test[0])
                print(datep[0][0])
                date = f'{datep[0][0]} {datep[0][1]} {datep[0][2]}'
            else:
                date = getdate[4:16]
                date = date.strip()
            print(date)
            n = datetime.datetime.strptime(date, "%d %b %Y")
            newdate = datetime.date(n.year, n.month, n.day)
        else:
            newdate = datetime.date.today()

        body = compact(body)
        if len(body) > 500:
            body = body[0:500]

        if len(thisfrom) > 45:
            thisfrom = thisfrom[0:45]

        if len(subject) > 90:
            subject = subject[0:90]


        qdat = Quotes.query.filter((Quotes.Title == subject) & (Quotes.From==thisfrom) & (Quotes.Date==newdate)).first()
        if qdat is None:
            input = Quotes(Date=newdate,From=thisfrom,Title=subject,Body=body,Response=None,Amount=None,Location=None,Status=0,Responder=None,RespDate=None,Start='Seagirt Marine Terminal, Baltimore, MD')
            db.session.add(input)
            db.session.commit()


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def direct_resolver(json):
    di, du, ht, la, lo = [],[],[],[],[]
    t1 = json['routes'][0]['legs'][0]['steps']
    for t2 in t1:
        di.append(t2['distance']['text'])
        du.append(t2['duration']['text'])
        ht.append(t2['html_instructions'])
        la.append(t2['end_location']['lat'])
        lo.append(t2['end_location']['lng'])

    return di, du, ht, la, lo

def route_resolver(json):
    ##print(json)
    final = json['rows']
    final = final[0]
    next = final['elements']
    next = next[0]
    bi = next['distance']
    ci = next['duration']
    di = bi['text']
    du = ci['text']
    return di, du

def address_resolver(json):
    final = {}
    if json['results']:
        data = json['results'][0]
        for item in data['address_components']:
            for category in item['types']:
                data[category] = {}
                data[category] = item['long_name']
        final['street'] = data.get("route", None)
        final['state'] = data.get("administrative_area_level_1", None)
        final['city'] = data.get("locality", None)
        final['county'] = data.get("administrative_area_level_2", None)
        final['country'] = data.get("country", None)
        final['postal_code'] = data.get("postal_code", None)
        final['neighborhood'] = data.get("neighborhood",None)
        final['sublocality'] = data.get("sublocality", None)
        final['housenumber'] = data.get("housenumber", None)
        final['postal_town'] = data.get("postal_town", None)
        final['subpremise'] = data.get("subpremise", None)
        final['latitude'] = data.get("geometry", {}).get("location", {}).get("lat", None)
        final['longitude'] = data.get("geometry", {}).get("location", {}).get("lng", None)
        final['location_type'] = data.get("geometry", {}).get("location_type", None)
        final['postal_code_suffix'] = data.get("postal_code_suffix", None)
        final['street_number'] = data.get('street_number', None)
    return final

def checkcross(lam,la_last,la,lom,lo_last,lo):
    lacross = 0
    locross = 0
    if (la_last<lam and la>lam) or (la_last>lam and la<lam):
        lacross = 1
    if (lo_last<lom and lo>lom) or (lo_last>lom and lo<lom):
        locross = 1
    return lacross, locross

def maketable():
    bdata = '<br><br>\n'
    bdata = bdata + '<table>\n'
    for key,value in accessorials.items():
        ##print(key, value[0], value[1])
        bdata = bdata + f'<tr><td><font size="+0">{key}&nbsp;</font></td><td><font size="+0">{value[0]}&nbsp;</font></td><td><font size="+0">${value[1]}&nbsp;</font></td></tr>\n'
    bdata = bdata + '</table><br><br>'
    bdata = bdata + f'<em>{signoff}</em>'

    return bdata


def sendquote(bidthis):
    etitle = request.values.get('edat0')
    ebody = request.values.get('edat1')
    emailin1 = request.values.get('edat2')
    emailin2 = request.values.get('edat3')
    emailcc1 = request.values.get('edat4')
    emailcc2 = request.values.get('edat5')
    emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2]
    # Add the accessorial table and signature to the email body:
    send_mimemail(emaildata,'quot')
    #print(etitle)
    #print(ebody)
    #print(emailin1)
    #print(emailcc1)
    return emaildata




def get_address_details(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    url = url + 'address='+ address.replace(" ","+")
    url = url + f'&key={API_KEY_GEO}'
    #print(url)
    response = get(url)
    data  = address_resolver(response.json())
    data['address'] = address
    lat = data['latitude']
    lon = data['longitude']
    #print(lat,lon)
    return data

def get_distance(start,end):
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={start}&destinations={end}'
    url = url + f'&key={API_KEY_DIS}'
    #print(url)
    response = get(url)
    #print(response)
    data = route_resolver(response.json())
    return data

def get_directions(start,end):
    dists, duras, lats, lons = [], [], [], []
    tot_dist = 0.0
    tot_dura = 0.0
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}'
    url = url + f'&key={API_KEY_DIS}'
    #print(url)
    response = get(url)
    dis, dus, hts, las, los  = direct_resolver(response.json())

    #Convert all mixed units to miles, hours and convert from text to floats
    for di in dis:
        if 'mi' in di:
            nu = float(di.replace('mi',''))
        elif 'ft' in di:
            nu = float(di.replace('ft',''))/5280.0
        else:
            nu = 0.0
        dists.append(nu)
        tot_dist += nu

    for du in dus:
        dul = du.split()
        if len(dul) == 4:
            hr = float(dul[0])
            min = float(dul[2])
            hrs = hr + min/60.0
        elif len(dul) == 2:
            if 'hr' in du:
                hrs = float(dul[0])
            elif 'min' in du:
                hrs = float(dul[0])/60.0
            else:
                hrs = 0.0
        duras.append(hrs)
        tot_dura += hrs

    for la in las:
        lats.append(float(la))
    for lo in los:
        lons.append(float(lo))

    return dists, duras, lats, lons, hts, tot_dist, tot_dura

def get_place(body):
    bodylines = body.splitlines()
    for line in bodylines:
        try:
            backend = line.split('to ')[1]
            backend = backend.strip()
            return backend
        except:
            continue
    location = '500 Hampton Park Blvd, Capitol Heights, MD  20743'
    return location

def friendly(emailin):
    try:
        efront = emailin.split('<')[0]
        efront = efront.replace('"','')
        return efront
    except:
        return emailin

def emailonly(emailin):
    try:
        eback = emailin.split('<')[1]
        eback = eback.replace('>','')
        return eback
    except:
        return emailin

def isoQuote():
    username = session['username'].capitalize()
    quot=0
    qdat=None
    from viewfuncs import dataget_Q, nonone, numcheck
    if request.method == 'POST':
        emailgo = request.values.get('Email')
        updatego = request.values.get('GetQuote')
        updatebid = request.values.get('Update')
        updateE = request.values.get('UpdateE')
        returnhit = request.values.get('Return')
        bidthis = request.values.get('bidthis')
        bidthis = d2s(bidthis)
        locfrom = request.values.get('locfrom')
        thismuch = request.values.get('thismuch')
        taskbox = request.values.get('taskbox')
        taskbox = nonone(taskbox)
        quotbut = request.values.get('optradio')

        qdata = dataget_Q(thismuch)
        #quot, numchecked = numcheck(1, qdata, 0, 0, 0, 0, ['quot'])

        if quotbut is not None:
            quot=nonone(quotbut)
        if quot == 0:
            quot = request.values.get('quotpass')
            quot = nonone(quot)
        qdat = Quotes.query.get(quot)
        print(quot, quotbut, username)

        if returnhit is not None:
            taskbox = 0
            quot = 0

        if taskbox == 2:
            qdat.Status = -1
            db.session.commit()
            taskbox = 0

        if taskbox == 3:
            qdat.Status = 0
            db.session.commit()
            taskbox = 0

        if taskbox == 4:
            qdat.Status = 3
            db.session.commit()
            taskbox = 0

        if taskbox == 1:
            if quot>0 and qdat is not None:
                locto = qdat.Location
                if locto is None:
                    locto = get_place(qdat.Body)
                    qdat.Location = locto
                    db.session.commit()
                emailto = qdat.From
                if emailto is None:
                    emailto = qdat.From
                    qdat.From = emailto
                    db.session.commit()

            if quot > 0:
                locfrom = qdat.Start
                if locfrom is None:
                    locfrom = 'Seagirt Marine Terminal, Baltimore, MD 21224'

                if updatego is not None or updatebid is not None or emailgo is not None or updateE is not None:
                    locto = request.values.get('locto')
                    if locto is None:
                        locto = 'Capitol Heights, MD  20743'
                    locfrom = request.values.get('locfrom')
                    emailto = request.values.get('edat2')
                    respondnow = datetime.datetime.now()
                    qdat.Start = locfrom
                    qdat.Location = locto
                    qdat.From = emailto
                    qdat.Amount = bidthis
                    qdat.Responder = username
                    qdat.RespDate = respondnow
                    qdat.Status = 1
                    db.session.commit()

                if emailgo is not None:
                    qdat.Status = 2
                    db.session.commit()
                    emaildata = sendquote(bidthis)
                    taskbox=0
                    quot=0


                print('Running Directions:',locfrom,locto,bidthis,taskbox,quot)
                try:
                    ####################################  Directions Section  ######################################
                    miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom,locto)
                    #print(f'Total distance {d1s(tot_dist)} miles and total duration {d1s(tot_dura)} hours')

                    #Calculate road tolls
                    tollroadlist = ['I-76','NJ Tpke']
                    tollroadcpm = [.784, .275]
                    legtolls = len(dirdata)*[0.0]
                    legcodes = len(dirdata)*['None']
                    for lx,mi in enumerate(miles):
                        for nx,tollrd in enumerate(tollroadlist):
                            if tollrd in dirdata[lx]:
                                legtolls[lx] = tollroadcpm[nx]*mi
                                legcodes[lx] = tollrd

                    #Calculate plaza tolls
                    fm_tollbox =  [39.267757, -76.610192, 39.261248, -76.563158]
                    bht_tollbox = [39.259962, -76.566240, 39.239063, -76.603324]
                    fsk_tollbox = [39.232770, -76.502453, 39.202279, -76.569906]
                    bay_tollbox = [39.026893, -76.417512, 38.964938, -76.290104]
                    sus_tollbox = [39.585193, -76.142883, 39.552328, -76.033975]
                    new_tollbox = [39.647121, -75.774523, 39.642613, -75.757187] #Newark Delaware Toll Center
                    dmb_tollbox = [39.702146, -75.553479, 39.669730, -75.483284]
                    tollcodes = ['FM', 'BHT', 'FSK', 'BAY', 'SUS', 'NEW', 'DMB']
                    tollboxes = [fm_tollbox, bht_tollbox, fsk_tollbox, bay_tollbox, sus_tollbox, new_tollbox, dmb_tollbox]

                    for jx,lat in enumerate(lats):
                        stat1 = 'ok'
                        stat2 = 'ok'
                        stat3 = 0
                        stat4 = 0
                        tollcode = 'None'
                        la = float(lat)
                        lo = float(lons[jx])
                        for kx, tollbox in enumerate(tollboxes):
                            lah = max([tollbox[0],tollbox[2]])
                            lal = min([tollbox[0], tollbox[2]])
                            loh = max([tollbox[1],tollbox[3]])
                            lol = min([tollbox[1], tollbox[3]])
                            if la > lal and la < lah:
                                stat1 = 'toll'
                                if lo > lol and lo < loh:
                                    stat2 = 'toll'
                                    tollcode = tollcodes[kx]
                                    legtolls[jx] = 24.00
                                    legcodes[jx] = tollcode
                            if jx > 0:
                                lam = (lah + lal)/2.0
                                lom = (loh + lol)/2.0
                                la_last = float(lats[jx-1])
                                lo_last= float(lons[jx-1])
                                stat3, stat4 = checkcross(lam,la_last,la,lom,lo_last,lo)
                                if stat3 == 1 and stat4 ==1:
                                    tollcode = tollcodes[kx]
                                    legtolls[jx] = 24.00
                                    legcodes[jx] = tollcode
                        ##print(lat,lons[jx],stat1, stat2, stat3, stat4, tollcode)

                    tot_tolls = 0.00
                    ex_drv = 27.41
                    ex_fuel = .48
                    ex_toll = 24.00
                    ex_insur = 4.00
                    ex_rm = .22
                    ex_misc = .04
                    ex_ga = 15
                    expdata = [d2s(ex_drv), d2s(ex_fuel), d2s(ex_toll), d2s(ex_insur), d2s(ex_rm), d2s(ex_misc), d2s(ex_ga)]

                    porttime = 1.4
                    loadtime = 2.0
                    triptime = tot_dura * 2.0
                    glidetime = 1.0 + triptime*.01
                    tottime = porttime + loadtime + triptime + glidetime
                    timedata = [d1s(triptime), d1s(porttime), d1s(loadtime), d1s(glidetime), d1s(tottime)]

                    tripmiles = tot_dist * 2.0
                    portmiles = .4
                    glidemiles = 10 + .005*tripmiles
                    totmiles = tripmiles + portmiles + glidemiles
                    distdata = [d1s(tripmiles), d1s(portmiles), '0.0', d1s(glidemiles), d1s(totmiles)]

                    newdirdata=[]
                    for lx, aline in enumerate(dirdata):
                        tot_tolls += legtolls[lx]
                        aline = aline.replace('<div style="font-size:0.9em">Toll road</div>','')
                        aline = aline.strip()
                        #print(aline)
                        #print(f'Dist:{d1s(miles[lx])}, Time:{d1s(hours[lx])}, ')
                        if legtolls[lx] < .000001:
                            newdirdata.append(f'{d1s(miles[lx])} MI {d2s(hours[lx])} HRS {aline}')
                        else:
                            newdirdata.append(f'{d1s(miles[lx])} MI {d2s(hours[lx])} HRS {aline} Tolls:${d2s(legtolls[lx])}, TollCode:{legcodes[lx]}')

                    # Cost Analysis:
                    cost_drv = tottime * ex_drv
                    cost_fuel = totmiles * ex_fuel
                    cost_tolls = 2.0 * tot_tolls

                    cost_insur = tottime * ex_insur
                    cost_rm = totmiles * ex_rm
                    cost_misc = totmiles * ex_misc

                    cost_direct = cost_drv + cost_fuel + cost_tolls + cost_insur + cost_rm + cost_misc
                    cost_ga = cost_direct * ex_ga/100.0
                    cost_total = cost_direct + cost_ga
                    costdata = [d2s(cost_drv),d2s(cost_fuel),d2s(cost_tolls),d2s(cost_insur), d2s(cost_rm), d2s(cost_misc), d2s(cost_ga), d2s(cost_direct), d2s(cost_total)]

                    bid = cost_total * 1.2
                    cma_bid = bid/1.13
                    std_bid = 250. + 2.1*totmiles


                    biddata = [d2s(roundup(bid)),d2s(roundup(std_bid)),d2s(roundup(cma_bid))]
                    if updatego is not None or quotbut is not None:
                        bidthis = d2s(roundup(bid))

                except:
                    costdata = None
                    biddata = None
                    newdirdata = None
                    bidthis = None
                    ex_drv = 27.41
                    ex_fuel = .48
                    ex_toll = 24.00
                    ex_insur = 4.00
                    ex_rm = .22
                    ex_misc = .04
                    ex_ga = 15
                    expdata = [d2s(ex_drv), d2s(ex_fuel), d2s(ex_toll), d2s(ex_insur), d2s(ex_rm), d2s(ex_misc), d2s(ex_ga)]
                    timedata = []
                    distdata = []


                if quotbut is not None:
                    #Set the email data:
                    etitle = f'{cdata[0]} Quote to {locto} from {locfrom}'
                    if qdat is not None:
                        customer = friendly(qdat.From)
                    else:
                        customer = friendly(emailto)
                    ebody = f'Hello {customer}, \n\n<br><br>{cdata[0]} is pleased to offer a quote of <b>${bidthis}</b> for this load to {locto}.\nThe quote is inclusive of tolls, fuel, and 2 hrs of load time.  Additional accessorial charges may apply and are priced according the following table:\n\n'
                    ebody = ebody + maketable()
                    emailin1 = request.values.get('edat2')
                    if updatego is None:
                        emailin1 = emailonly(emailto)
                    emailin2 = None
                    emailcc1 = usernames['info']
                    emailcc2 = usernames['expo']
                    emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2]
                else:
                    #Set the email data:
                    if updatebid is not None or updatego is not None:
                        etitle = f'{cdata[0]} Quote to {locto} from {locfrom}'
                        if qdat is not None:
                            customer = friendly(qdat.From)
                        else:
                            customer = friendly(emailto)
                        ebody = f'Hello {customer}, \n\n<br><br>{cdata[0]} is pleased to offer a quote of <b>${bidthis}</b> for this load to {locto}.\nThe quote is inclusive of tolls, fuel, and 2 hrs of load time.  Additional accessorial charges may apply and are priced according the following table:\n\n'
                        ebody = ebody + maketable()
                    else:
                        etitle = request.values.get('edat0')
                        ebody = request.values.get('edat1')
                    emailin1 = request.values.get('edat2')
                    emailin2 = request.values.get('edat3')
                    emailcc1 = request.values.get('edat4')
                    emailcc2 = request.values.get('edat5')
                    emaildata = [etitle, ebody, emailin1, emailin2, emailcc1, emailcc2]
                    #qdat.Response = ebody
                    db.session.commit()


        else:
            qdata = dataget_Q(thismuch)
            quot = request.values.get('optradio')
            if quot is not None:
                qdat = Quotes.query.get(quot)
            locto = 'Capitol Heights, MD  20743'
            locfrom = 'Baltimore Seagirt'
            etitle = f'{cdata[0]} Quote for Drayage to {locto} from {locfrom}'
            if qdat is not None:
                ebody = qdat.Body
            else:
                ebody = f'Regirgitation from the input'
            efrom = usernames['quot']
            eto1 = 'unknown'
            eto2 = ''
            ecc1 = usernames['expo']
            ecc2 = usernames['info']
            emaildata = [etitle, ebody, eto1, eto2, ecc1, ecc2, efrom]
            costdata = None
            biddata = None
            newdirdata = None
            bidthis = None


            ex_drv = 27.41
            ex_fuel = .48
            ex_toll = 24.00
            ex_insur = 4.00
            ex_rm = .22
            ex_misc = .04
            ex_ga = 15
            expdata = [d2s(ex_drv), d2s(ex_fuel), d2s(ex_toll), d2s(ex_insur), d2s(ex_rm), d2s(ex_misc), d2s(ex_ga)]
            timedata = []
            distdata = []


    else:

        username = session['username'].capitalize()
        qdat=None
        locto = 'Capitol Heights, MD  20743'
        locfrom = 'Baltimore Seagirt'
        etitle = f'{cdata[0]} Quote for Drayage to {locto} from {locfrom}'
        ebody = f'Regirgitation from the input'
        efrom = usernames['quot']
        eto1 = 'unknown'
        eto2 = ''
        ecc1 = usernames['expo']
        ecc2 = usernames['info']
        emaildata = [etitle, ebody, eto1, eto2, ecc1, ecc2, efrom]
        costdata = None
        biddata = None
        newdirdata = None
        bidthis = None

        ex_drv = 27.41
        ex_fuel = .48
        ex_toll = 24.00
        ex_insur = 4.00
        ex_rm = .22
        ex_misc = .04
        ex_ga = 15
        expdata = [d2s(ex_drv), d2s(ex_fuel), d2s(ex_toll), d2s(ex_insur), d2s(ex_rm), d2s(ex_misc), d2s(ex_ga)]
        timedata = []
        distdata = []
        add_quote_emails()
        thismuch = '1'
        taskbox = 0
        quot=0

    qdata = dataget_Q(thismuch)
    print(quot)
    return costdata, biddata, expdata, timedata, distdata, emaildata, locto, locfrom, newdirdata, qdata, bidthis, taskbox, thismuch, quot, qdat