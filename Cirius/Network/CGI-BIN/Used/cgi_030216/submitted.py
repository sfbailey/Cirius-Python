#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        submitted.py
# Purpose:      Takes data from human Cirius page and uploads files, data
#
# Author:      sfbailey
#
# Created:     10/02/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import DBconnections
import os, sys
import time, datetime
import codecs
from Bio.Seq import Seq
from Bio import SeqIO
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess
import cgi, cgitb
import shlex
import psutil
import pymysql
import extProcess
import binascii
import uuid
import fileRemoval
import json
import sortfile
from StringIO import StringIO
cgitb.enable()

UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

form = cgi.FieldStorage()
allele = form.getvalue("fallele")
markers = form.getvalue("markers")
filenum = form.getvalue("filenum")
email = form.getvalue("femail")
usergui = form.getvalue("ugui")
timesubm = form.getvalue("timesubm")
rmvsingles = form.getvalue("singletons")

def convert_file(ffile, extension):
    message = ""

    #print ffile, extension

    cpath = UPLOAD_DIR + ffile + "-" + timesubm +  ".fasta"

    try:
        if extension == 'fastq':
            qpath = UPLOAD_DIR + ffile + "-" + timesubm + ".fastq"
            SeqIO.convert(qpath, "fastq", cpath, "fasta")

        with open(cpath,"r+b") as inputFile:
            content = inputFile.read()
            inputFile.seek(0)
            inputFile.write(content.lower())
        return message

    except Exception, e:
        message = message + "File (" + ffile + ") does not seem to be FASTQ or FASTA file. <br/>" +\
            "File removed. <br/>"
        #fileRemoval.removal_of_file(cpath)
        return message

def print_header():
    f = codecs.open("header.html", 'r', 'utf-8')
    print f.read()

def print_footer():
    f = codecs.open("footer.html", 'r', 'utf-8')
    print f.read()

def setUserID(tstamp, filelist):
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    key = usergui

    sqst = "SELECT * FROM tempwork where batchID = '" + key + "' AND tsubmit = '" + tstamp + "'"
    cursor1.execute(sqst)
    rows =  cursor1.fetchone()

    if rows is None:
     for file in filelist:
        sqst = "INSERT INTO tempuser (userfile, allele, email, rsingles) VALUES " +\
            "('" + file + "', '" + allele + "', '" + email + "', '" + rmvsingles + "')"

        cursor1.execute(sqst)
        cursor1.execute("COMMIT")
        cursor1.execute("SELECT LAST_INSERT_ID() AS id")
        usID = cursor1.fetchone()
        userID = usID[0]
        sqst = "INSERT INTO tempWork (userID, batchID, tsubmit) VALUES ( %d, '%s', '%s')" % (userID, key, timesubm)
        cursor1.execute(sqst)
        cursor1.execute("COMMIT")

     if markers.find(",") > 0:
        for m in markers:
            sqst = "INSERT INTO tempmarker (batchID, marker) VALUES ('" +\
                key + "', '" + m + "')"
     else:
        sqst = "INSERT INTO tempmarker (batchID, marker) VALUES ('" +\
                key + "', '" + markers + "')"
     cursor1.execute(sqst)
     cursor1.execute("COMMIT")

    cursor1.close()
    DBconnections.closeDB(Con1)

    return key

if __name__ == '__main__':
    print "Content-Type: text/html\n\n"
    print_header();
    print "<div style='float:left;'>"

    files = []
    fileItems = form["fname"]
    if type(fileItems) != type([]):
        fileItems = [fileItems]

    message = ""
    gflag = "True"
    allelestr = "All"
    filepathlist = []
    dispfiles = ""
    dispnewfile = ""

    if int(filenum) > 1:
        files = form.getvalue("fpath").split(',')
        fileItems = form["fname"]
        count = 0
        for file in files:

            if len(dispfiles) > 1:
                dispfiles = dispfiles + ", "
                dispnewfile = dispnewfile + ", "
            dispfiles = dispfiles + file
            fcomp = file.split(".")
            ffile = fcomp[0]
            extension = fcomp[1]
            new_file_name = ffile + "-" + timesubm + "." + extension
            dispnewfile = dispnewfile + new_file_name
            new_path = UPLOAD_DIR + new_file_name
            filecontents = fileItems[count].file.read()
            filepathlist.append(new_file_name)

            output_file = open(new_path, 'wb')
            output_file.write(filecontents)
            output_file.close()
            messagesv = convert_file(ffile, extension)
            message = message + messagesv
            count += 1
    else:
        file_path = form.getvalue("fpath")
        dispfiles = file_path
        filename = os.path.basename(file_path)
        filecontents = form.getvalue("fname")
        fcomp = filename.split(".")
        ffile = fcomp[0]
        extension = fcomp[1]
        new_file_name = ffile + "-" + timesubm + "." + extension
        dispnewfile = dispnewfile + new_file_name
        new_path = UPLOAD_DIR + new_file_name
        filepathlist.append(new_file_name)

        output_file = open(new_path, 'wb')
        output_file.write(filecontents)
        output_file.close()
        messagesv = convert_file(ffile, extension)
        message = message + messagesv


    if allele != 'All':
            if allele == "AnY":
                allelestr = "Autosomal and Y"
            elif allele == "AnX":
                allelestr = "Autosomal and X"
            elif allele == "XnY":
                allelestr = "X and Y"
            elif allele == "A":
                allelestr = "Autosomal"
            elif allele == "X":
                allelestr = "X"
            elif allele == "Y":
                allelestr = "Y"
            elif allele == "powerSeq":
                allelestr = "PowerSeq"


    dispMarkers = "All"
    if markers.find(",") > 0:
        io = StringIO()
        dispMarkers = str(markers).strip('[]')
    else:
        dispMarkers = str(markers)

    print "<h2>Cirius Selections: </h2>" +\
        "<table>" +\
        "<tr><th width='160px'>Email address:</th><td>%s </td></tr>" % email  +\
        "<tr><th>Allele:</th><td>" +  allelestr + " </td></tr>" +\
        "<tr><th valign='top'>Selected markers:</th><td valign='top'>" + dispMarkers +"</td></tr>" +\
        "<tr><th valign='top'>Uploaded files:</th><td valign='top'>" + dispfiles + "</td></tr>"
    if len(message) > 1:
        print "<tr><th>Messages:</th><td>" + message +  "</td></tr>"
    print "</table><br/><br/>"


    workID = setUserID(timesubm, filepathlist)

    print "File(s) have been submitted to be analyzed. <br/>" +\
        "At completion, an email will be be sent to " + email + ". <br/>" +\
        "The email will contain an <b>Identification number</b>. <br/>" +\
        "Follow the link to the site to view your results." +\
        "<br/><br/>" +\
        "<a href='http://localhost/index.html'><button>Start over</button></a><br/><br/>"



    #print "User-Agent:", os.environ.get("HTTP_USER_AGENT", "N/A")

    print "</div>"
    print_footer();
