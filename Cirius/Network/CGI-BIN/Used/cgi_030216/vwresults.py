#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        writeResults
# Purpose:      Write the results to text file and to screen
#
# Author:      sfbailey
#
# Created:     22/02/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import pymysql
import DBconnections
import os, sys
import datetime
import cgi, cgitb
cgitb.enable()
import codecs
import time
import socket
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
start_time = time.time()
sys.stderr = sys.stdout

UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

"""
form = cgi.FieldStorage()
idnumber = form['idnumber'].value
locusname = form['locusname'].value
fileholder = form['fileholder'].value
filter = form['filter'].value
locfilter = form['locfilter'].value
"""
def print_header():
        f = codecs.open("header.html", 'r', 'utf-8')
        print f.read()

def print_footer():
        f = codecs.open("footer.html", 'r', 'utf-8')
        print f.read()



def writeResults(fn, userID, batchID, locusname, fileholder, filter, locfilter):

        Con2 = DBconnections.openDB()
        cursor2 = Con2.cursor()

        #get total number of reads
        queryTotal = "SELECT SUM(seqcount) As TotalReads FROM tempcontent WHERE userID = {}".format(userID)
        #print queryTotal

        qLocus = "SELECT locus FROM tempcontent WHERE userID = {} Group by locus".format(userID)

        cursor2.execute (queryTotal)
        tReads = cursor2.fetchone()
        totalReads = tReads[0]
        #print "<br/>total reads: " + str(totalReads)

        cursor2.execute (qLocus)
        locuslinks = cursor2.fetchall()
        links = 0
        # View Locus select list
        print "<hr/><br/><form action='' method='post' name='locfrm' id='locfrm' enctype='multipart/form-data' >" +\
                "<b>View Locus: </b><select id='locusname' name='locusname' onchange='javascript: getlocus(this);'>" +\
                "<option value=''"
        if locusname == "":
            print "selected>"
        else:
            print ">"
        print "All</option>"

        for lcs in locuslinks:
            print "<option value='" + str(lcs[0]) + "' "
            if locusname == str(lcs[0]):
                print "selected"
            print ">" + str(lcs[0]) + "</option>"
        print "</select>"

        # Allele Ratio Filter select list
        print "&nbsp;&nbsp;<b>Allele Ratio Filter: </b>" +\
        "<select id='filter' name='filter' style='width:100px;' onchange='javascript: getFilter(this);'>"
        num = 0
        perctg = 0
        for n in range(0,12):
            print "<option value='" + str(num) + "'"
            if str(filter) == str(num):
                print "selected"
            print ">"
            if num == 0:
                print "Nothing"
            else:
                print "> " + str(num)
            print "</option>"
            num = num + 0.001
        print "</select>"

        # Locus Filter list
        print "&nbsp;&nbsp;<b>Locus Ratio Filter: </b>" +\
        "<select id='locfilter' name='locfilter' style='width:100px;' onchange='javascript: getLocFilter(this);'>"
        num = 0
        perctg = 0
        for n in range(0,4):
            print "<option value='" + str(num) + "'"
            if str(locfilter) == str(num):
                print "selected"
            print ">"
            if num == 0:
                print "Nothing"
            else:
                print "> " + str(num)
            print "</option>"
            num = num + 0.01
        print "</select>"

        print "<br/><input type='hidden' name='idnumber' id='idnumber' value='" + batchID + "'>" +\
        "<input type='hidden' name='fileholder' id='fileholder' value='" + fileholder  + "'>" +\
        "</form>"

        if locusname == "":
            queryCount = "SELECT locus, SUM(seqcount) As TotalReads FROM tempcontent WHERE userID = {} Group by locus".format(userID) +\
            " ORDER BY locus"
        else:
            queryCount = "SELECT locus, SUM(seqcount) As TotalReads FROM tempcontent WHERE " +\
            "locus = '" + locusname + "' AND " +\
            "userID = {} Group by locus".format(userID) +\
            " ORDER BY locus"

        cursor2.execute (queryCount)
        Readresults = cursor2.fetchall()

        for rec in Readresults:
            locus = rec[0]
            sCount = rec[1]
            # sort and count number of reads
            #filename locus allele read_dir sequence seq_Len reads allele_Count allele_ratio total_ratio num_repeats
            query = "SELECT tempcontent.locus, allele, readdir, " +\
            "tempcontent.seq as seq, length(tempcontent.seq)  as seqLen, SUM(seqcount) as seqCounts, " +\
            "((SUM(tempcontent.seqcount))/{}.0)".format(sCount) + " As allele_ratio, ((SUM(tempcontent.seqcount))/{}.0)".format(totalReads) + " As total_ratio " +\
            "FROM tempcontent  " +\
            "WHERE tempcontent.locus = '" + locus + "' AND userID = {}".format(userID) +\
            " Group by allele, locus, readDir, tempcontent.seq "
            #if filter > 0:
                #query = query + " HAVING ((SUM(tempcontent.seqcount))/{}.0)".format(sCount) + " > " + filter
            query = query + " Order by length(tempcontent.seq), tempcontent.seq, readdir, SUM(seqcount) desc   "

            cursor2.execute (query)
            getRecords = cursor2.fetchall()


            print "<br/><table style='border-collapse:collapse; border: solid 1px black;font-size:12px;'>"
            count = 0
            aH = ""
            lH = ""
            sH = ""
            rdH = ""
            FRRH = ""
            slH = 0
            scH = 0
            arH = 0
            trH = 0
            flag = False
            for seqRecord in getRecords:
                locus = seqRecord[0]
                allele = seqRecord[1]
                readdir = seqRecord[2]
                seq = seqRecord[3]
                seqLen = seqRecord[4]
                seqCounts = seqRecord[5]
                alleleRatio = seqRecord[6]
                totalRatio = seqRecord[7]
                locusRatio = sCount/totalReads

                if count == 0:
                    print "<tr style='background-color: #cccccc;'><td colspan='8' style='border-style:solid;border-width: 0px 0px 1px 0px;'><b>" +\
                    locus + "</b><br/>" +\
                    "<b>Allele total: </b>" + str(sCount) + "&nbsp;&nbsp;<b>Total Count:</b> " + str(totalReads) +\
                    "&nbsp;&nbsp;<b>Locus Ratio: </b>" + "{0:.4f}".format(locusRatio) + "</td></tr>"
                    if float(locusRatio) > float(locfilter):
                        print "<tr style='background-color:#FAEBD7;border:1px solid black;'><th style='padding-right:5px;'>Allele</th><th style='padding-right:5px;'>locus</th>" +\
                        "<th style='padding-right:8px;'>Seq</th><th style='padding-right:8px;'>Seq<br/>Length</th>" +\
                        "<th style='padding-right:8px;'>Seq<br/>Counts</th><th style='padding-right:8px;'>FWD/REV</th>" +\
                        "<th style='padding-right:8px;'>Allele<br/>Ratio</th><th style='padding-right:8px;'>Total<br/>Ratio</th></tr>"
                    aH = allele
                    lH = locus
                    sH = seq
                    slH = seqLen
                    scH = seqCounts
                    arH = alleleRatio
                    trH = totalRatio
                    flag = True

                if float(locusRatio) > float(locfilter):
                    if count > 0:
                        if readdir == 'REV' and seq == sH:
                            aH = allele
                            lH = locus
                            sH = seq
                            slH = seqLen
                            FR = scH/(scH + seqCounts)
                            RR = seqCounts/(scH + seqCounts)
                            FRRH = "{0:.4f}".format(FR) + "/" + "{0:.4f}".format(RR)
                            scH = scH + seqCounts
                            arH = arH + alleleRatio
                            trH = trH + totalRatio

                            if float(arH) > float(filter):
                                print "<tr><td style='padding-left:5px;padding-right:5px;'>{}</th>".format(aH)
                                print "<th style='padding-right:5px;'>{}</th>".format(lH)
                                print "<th style='padding-right:5px;'>{}</th>".format(sH)
                                print "<th style='padding-right:8px;'>{}</th>".format(slH)
                                print "<th style='padding-right:8px;'>{}</th>".format(scH)
                                print "<th style='padding-right:8px;'>{}</th>".format(FRRH)
                                print "<th style='padding-right:8px;'>{}</th>".format(arH)
                                print "<th style='padding-right:8px;'>{}</th></tr>".format(trH)
                                flag = False

                        else:
                            if flag == True :
                                if float(arH) > float(filter):
                                    print "<tr><td style='padding-left:5px;padding-right:5px;'>{}</th>".format(aH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(lH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(sH)
                                    print "<th style='padding-right:8px;'>{}</th>".format(slH)
                                    print "<th style='padding-right:8px;'>{}</th>".format(scH)
                                    print "<th style='padding-right:8px;'>{}</th>".format(FRRH)
                                    print "<th style='padding-right:8px;'>{}</th>".format(arH)
                                    print "<th style='padding-right:8px;'>{}</th></tr>".format(trH)
                                    flag = False

                            aH = allele
                            lH = locus
                            sH = seq
                            slH = seqLen
                            scH = seqCounts
                            arH = alleleRatio
                            trH = totalRatio

                            if readdir == "FWD":
                                FRRH = "1/0"
                                flag = True
                            else:
                                FRRH = "0/1"
                                flag = False
                            if flag == False:
                                if float(arH) > float(filter):
                                    print "<tr><td style='padding-left:5px;padding-right:5px;'>{}</th>".format(aH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(lH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(sH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(slH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(scH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(FRRH)
                                    print "<th style='padding-right:5px;'>{}</th>".format(arH)
                                    print "<th style='padding-right:5px;'>{}</th></tr>".format(trH)
                                    flag = False



                    count += 1
                else:
                    print "<tr style='background-color:#ccffff'><td colspan='8' style='border-top:1px solid black;'>No Data</td></tr>"
                    break
            print "</table><br/>"



        cursor2.close()
        DBconnections.closeDB(Con2)

def closeConnection(Con, cursor):
        cursor.close()
        DBconnections.closeDB(Con)

if __name__ == '__main__':
    print "Content-Type: text/html\n\n"
    print_header();
    print "<div style='float:left;'>"

    try:
        form = cgi.FieldStorage()
        idnumber = form['idnumber'].value
        locusname = form['locusname'].value
        fileholder = form['fileholder'].value
        filter = form['filter'].value
        locfilter = form['locfilter'].value

        batchID = idnumber

        # ******** This will be web input ******

        Con1 = DBconnections.openDB()
        cursor1 = Con1.cursor()
        query = "select tempuser.userID, tempuser.userfile, tempwork.timeAnalyze, " +\
        "tempwork.onumlines, tempwork.numlines " +\
        "from tempuser, tempwork " +\
        "where tempuser.userID = tempwork.userID " +\
        "and tempwork.batchID = '{}'".format(batchID) +\
        " group by batchID " +\
        " order by tsubmit"
        cursor1.execute(query)

        getRecords = cursor1.fetchall()

        for rec in getRecords:
            userID = rec[0]
            filename = rec[1]
            tAnal = rec[2]
            onumlines = rec[3]
            numlines = rec[4]
            ttime = float(tAnal) * 60* 60

            fname = filename.split(".")
            nfile = fname[0]
            ext = fname[1]

            print "<table style='border-collapse:collapse;font-size:14px;'>"
            print "<tr><td colspan='2'><h3>Summary</h3></td></tr>"
            print "<tr><th>BatchID</th><td>" + batchID + "</td></tr>"
            print "<tr><th>Filename</th><td>" + nfile + "</td></tr>"
            print "<tr><th>Time to run</th><td>" + str(ttime) + "hrs </td></tr>"
            print "<tr><th>Lines analyzed</th><td>" + str(onumlines) + "</td></tr>"
            print "<tr><th>Lines matched</th><td>" + str(numlines) + "</td></tr>"
            print "<tr><th valign='top' style='padding-right:5px'>Available files for download:</th>" +\
                "<td valign='top'>" + nfile + "_Match.fasta - Fasta file of matched sequences<br/>" +\
                nfile + "_Other.fasta - FASTA file of unmatched sequences<br/>" +\
                nfile + "_MatchResults.csv - All data as below</td></tr>"
            print "<tr><td colspan='2'>&nbsp;***</td></tr></table><br/>"

            writeResults(nfile, userID, batchID, locusname, fileholder, filter, locfilter)

        print "</div>"
        #print_footer()
    except Exception:

        print "Please go back and type in your Identification number again. Something went wrong."
        print "</div>"