#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        results.py
# Purpose:
#
# Author:      sfbailey
#
# Created:     15/01/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import DBconnections
import os, sys
import time, datetime
import codecs
import ciriusv1Web
from Bio.Seq import Seq
from Bio import SeqIO
import multiprocessing
from multiprocessing import Pool, Queue, Manager
import subprocess32
import cgi, cgitb

cgitb.enable()
form = cgi.FieldStorage()
allele = form.getvalue("fallele")
markers = form.getvalue("fmarkers")
species = form.getvalue("fspecies")
numanal =form.getvalue("fnum")
numproc = int(numanal)
filename  =form.getvalue("ffile")

UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"
start_time = time.time()

def print_header():
    print "content-type: text/html\n"
    f = codecs.open("header.html", 'r', 'utf-8')
    print f.read()

def print_footer():
    f = codecs.open("footer.html", 'r', 'utf-8')
    print f.read()

def remove_file():
    os.remove(UPLOAD_DIR + filename)

def start_extProcess():
    #cmd = 'python C:\Apache24\cgi-bin\extProcess.py %' + userID + '%'
    cmd = 'python C:\Apache24\cgi-bin\extProcess.py %4%'
    subprocess32.call(cmd, shell=True)

def setUserID(filename,species, allele, markers, numanal):
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    if isinstance(markers, str) == True:
        strMarkers = markers
    else:
        strMarkers = 'NULL'

    sqst = "INSERT INTO tempuser (user, userfile, species, allele, markers, numanal) VALUES (" +\
            "'temp','" + filename + "', '" + species + "','" + allele + "', '" +\
            strMarkers + "', '" + str(numanal) + "')"
    print sqst
    cursor1.execute(sqst)
    cursor1.execute("SELECT LAST_INSERT_ID() AS id")
    batchID = cursor1.fetchone()
    userID = batchID[0]
    cursor1.close()
    DBconnections.closeDB(Con1)
    print "SetUser: UserID = {0} <br/>".format(userID)
    return userID

def startProcess():

    processes = []
    userID = setUserID(filename,species, allele, markers, numanal)
    print "main: UserID: {0}<br/>".format(userID)


    fname = filename.split(".")
    nfile = fname[0]
    ext = fname[1]
    cpath = UPLOAD_DIR + nfile + "." + ext
    matchpath = SAVE_DIR + nfile + "_Match.fasta"
    otherpath = SAVE_DIR + nfile + "_Other.fasta"
    hc = open(matchpath,"w")
    hc.close()
    hc = open(otherpath,"w")
    hc.close()

    cRecords = 0
    start_extProcess()

    """ciriusv1Web.writeResults (filename, userID)
    print "The resulting files are available for download. <br/>" """

    print "Thank you for your patience"
    print("--- %s seconds ---" % (time.time() - start_time)) + "<br/>"

if __name__ == '__main__':
    print_header();
    HTML_RESULTS = "<div class='comments white-bg col-md-9 col-sm-12'>" +\
        "<h2>Results</h2>"
    print HTML_RESULTS
    startProcess()

    print "</div>"
    print_footer();