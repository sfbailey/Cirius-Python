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
import datetime
import cgi, cgitb
import codecs
import time
start_time = time.time()

UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

form = cgi.FieldStorage()
idnumber = form.getvalue("idnumber")
print idnumber
"""
def print_header():
    f = codecs.open("header.html", 'r', 'utf-8')
    print f.read()

def print_footer():
    f = codecs.open("footer.html", 'r', 'utf-8')
    print f.read()

def writeResults(fn, userID):
    matchresults = UPLOAD_DIR + fn  + "_Match.csv"
    matchresults2 = UPLOAD_DIR + fn  + "_Match2.csv"

    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()

    hc = open(matchresults,"w")
    hc.write("filename locus allele read_dir sequence seq_Len count allele_Count allele_ratio total_ratio  \n")
    hc.close()
    hc = open(matchresults2,"w")
    hc.write("filename locus allele sequence seq_Len count allele_Count allele_ratio total_ratio  \n")
    hc.close()

    #get total number of reads
    queryTotal = "SELECT count(seq) As TotalReads FROM tempcontent WHERE userID = {}".format(userID)
    #print queryTotal
    queryCount = "SELECT locus, Count(seq) As TotalReads FROM tempcontent WHERE userID = {} Group by locus".format(userID)

    cursor2.execute (queryTotal)
    tReads = cursor2.fetchone()
    totalReads = tReads[0]
    print "total reads: " + str(totalReads)

    cursor2.execute (queryCount)
    Readresults = cursor2.fetchall()

    for rec in Readresults:
        locus = rec[0]


        sCount = rec[1]
        # sort and count number of reads
        #filename locus allele read_dir sequence seq_Len reads allele_Count allele_ratio total_ratio num_repeats
        query = "SELECT tempcontent.locus, allele, readdir, " +\
            "tempcontent.seq as seq, length(tempcontent.seq)  as seqLen, SUM(seqcount) as seqCounts, " +\
            "((SUM(tempcontent.seq))/{}.0)".format(sCount) + " As allele_ratio, ((SUM(tempcontent.seq))/{}.0)".format(totalReads) + " As total_ratio" +\
            "FROM tempcontent, tblrepeats  " +\
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {}".format(userID) +\
            " Group by allele, locus, readDir, tempcontent.seq " +\
            " Order by allele, locus, readdir, tempcontent.seq"


        cursor2.execute (query)
        getRecords = cursor2.fetchall()

        with open(matchresults,"a") as textfile:
            for seqRecord in getRecords:
                textfile.write(fn + ' ')
                textfile.write(' '.join(str(s).upper() for s in seqRecord) + '\n')
        textfile.close()

        locushead = ""
        locusname = ""
        print "File: " + fn + "<br/>"

        for seqRecord in getRecords:
            locus = seqRecord[0]
            allele = seqRecord[1]
            readdir = seqRecord[2]
            seq = seqRecord[3]
            seqLen = seqRecord[4]
            seqCounts = seqRecord[5]
            alleleRatio = seqRecord[6]
            totalRatio = seqRecord[7]

            if locusname <> locus:
                if len(locusname) > 1:
                    print "</table><br/><br/>"
                print "<table style='border-collapse:collapse; border: solid 1px black;'>"
                print "<tr><td colspan='8' style='border-style:solid;border-width: 0px 0px 1px 0px;'>" +\
                        locus + "</td></tr>"
                print "<tr><th>Allele</th><th>locus</th><th>Read Dir</th><th>Seq</th><th>Seq Length</th><th>Seq Counts</th>" +\
                        "<th>Allele Ratio</th><th>Total Ratio</th></tr>"

            print "<tr><td>" + allele + "</td>"
            print "<td>" + locus + "</td>"
            print "<td>" + readdir + "</td>"
            print "<td>" + str(seq) + "</td>"
            print "<td>" + str(seqLen) + "</td>"
            print "<td>" + str(seqCounts) + "</td>"
            print "<td>" + str(alleleRatio) + "</td>"
            print "<td>" + str(totalRatio) + "</td>"
            locusname = locus
        print "</table><br/>"

        query = "SELECT tempcontent.locus, allele, tempcontent.seq, length(tempcontent.seq)  as seqLen, SUM(seqcount) as seqCounts, " +\
            "(SUM(seqcount))/{}.0)".format(sCount) + " As allele_ratio, (SUM(seqcount))/{}.0)".format(totalReads) + " As total_ratio, " +\
            "FROM tempcontent, tblrepeats  " +\
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {}".format(userID) +\
            " Group by allele, locus, tempcontent.seq " +\
            " Order by allele, locus, tempcontent.seq"

        cursor2.execute (query)
        getRecords = cursor2.fetchall()

        with open(matchresults2,"a") as textfile2:
            for seqRecord in getRecords:
                textfile2.write(fn + ' ')
                textfile2.write(' '.join(str(s).upper() for s in seqRecord) + '\n')
        textfile2.close()

    #cursor2.execute("DELETE FROM tempuser WHERE userID = {}".format(userID))
    #cursor2.execute("DELETE FROM tempcontent WHERE userID = {}".format(userID))

    cursor2.close()
    DBconnections.closeDB(Con2)

def closeConnection(Con, cursor):
    cursor.close()
    DBconnections.closeDB(Con)
"""
if __name__ == '__main__':
    print "Content-Type: text/html\n\n"
    print_header();
    print "<div>"

    batchID = idnumber
    # ******** This will be web input ******
    """
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    query = "select tempuser.userID, tempuser.userfile, tempuser.allele, tempwork.batchID  " +\
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

        fname = filename.split(".")
        nfile = fname[0]
        ext = fname[1]

        writeResults(npath, userID)
    """
    print "</div>"
    print_footer()