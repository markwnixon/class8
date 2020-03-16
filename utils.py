from CCC_system_setup import addpath, scac, tpath, companydata
from flask import request
import datetime
import calendar
import re
import os
import shutil
import subprocess
import img2pdf
import json

def requester(alist):
    areturn = ['0']*len(alist)
    for ix, al in enumerate(alist):
        areturn[ix] = request.values.get(al)
    return areturn