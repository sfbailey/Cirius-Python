#-------------------------------------------------------------------------------
# Name:         DBConnections.py
# Purpose:      Connect to MySQL
#
# Author:       sarah.bailey
#
# Created:     15/09/2015
# Copyright:   (c) sarah.bailey 2015
#-------------------------------------------------------------------------------
import MySQLdb
import configSQL

# openDB: Opens database connection. This should be in a config file.
def openDB():
    print
    usr = configSQL.users
    pswd = configSQL.passwrd
    #db = MySQLdb.Connect(host="faithlabmysql.cu794qp2wkwe.us-east-1.rds.amazonaws.com", port=3306, user= usr, passwd=pswd, db="animalsq")
    db = MySQLdb.Connect(host="127.0.0.1", port=3306, user= usr, passwd=pswd, db="animalsq")
    return db

# closeDB: Close the database connection
def closeDB(conn):
    conn.close()
