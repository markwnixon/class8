from runmain import db
import requests
import json
from CCC_system_setup import apikeys
from models import Autos
import datetime
today = datetime.datetime.today()
today = today.date()


def getvindata(vintoget):
    url = "https://vindecoder.p.rapidapi.com/decode_vin"
    querystring = {"vin":vintoget}

    headers = {
        'x-rapidapi-host': "vindecoder.p.rapidapi.com",
        'x-rapidapi-key': apikeys['vinkey']
        }

    r = requests.request("GET", url, headers=headers, params=querystring)
    dataret = r.json()
    print(dataret)
    suc = dataret['success']
    print(suc)
    if suc is True:
        print('Successful pull of VIN')
        specs = dataret['specification']
        vin = specs['vin']
        year = specs['year']
        make = specs['make']
        model = specs['model']

        input = Autos(Jo=None, Hjo=None, Year=year, Make=make, Model=model, Color=None, VIN=vin,
                      Title='', State='', EmpWeight='Star', Dispatched=None, Value='Star',
                      TowCompany=None, TowCost=None, TowCostEa=None, Original='',
                      Status='New', Date1=today, Date2=today, Pufrom=None, Delto=None, Ncars=1, Orderid=None)
        db.session.add(input)
        db.session.commit()
    else:
        specs = 0

    return suc, specs
