from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from CCC_system_setup import scac, machine, statpath, dbp

app = Flask(__name__, static_folder = "tmp")
####################################################################
########## SET DATABASE STRUCTURES #################################
####################################################################
a=statpath('1')
print(scac, machine,a)

SQLALCHEMY_DATABASE_URI = dbp[0] +"{username}:{password}@{hostname}/{databasename}".format(
            username=dbp[1],
            password=dbp[2],
            hostname=dbp[3],
            databasename=dbp[4]
        )
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.secret_key = dbp[5]

db = SQLAlchemy(app)
from iso_A import *
if __name__ == '__main__':
    app.run()
