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
#import multiprocessing
#from multiprocessing import Pool, Queue, Manager
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess
import cgi, cgitb
import shlex
import psutil
import MySQLdb
import pp
import extProcess

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

def start_extProcess(userID):
    print userID
    userID2 = str(userID)
    #cmd = ["python", "extProcess.py", userID2]
    #output = subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
    #print output
    cmd = "python extProcess.py {}".format(userID2)
    print cmd
    output = subprocess.check_call(cmd, shell=True, stderr=subprocess.STDOUT)
    print output

def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""
    return psutil.cpu_count()


def setUserID():
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    if isinstance(markers, str) == True:
        strMarkers = markers
    else:
        strMarkers = 'NULL'

    sqst = "INSERT INTO tempuser (user, userfile, species, allele, markers, numanal) VALUES (" +\
            "'temp','" + filename + "', '" + species + "','" + allele + "', '" +\
            strMarkers + "', '" + str(numanal) + "')"

    cursor1.execute(sqst)
    cursor1.execute("COMMIT")
    cursor1.execute("SELECT LAST_INSERT_ID() AS id")
    batchID = cursor1.fetchone()
    userID = batchID[0]
    cursor1.close()
    DBconnections.closeDB(Con1)
    return userID

def writeTextResults(fn, userID):
    matchresults = SAVE_DIR + fn + "_Match.txt"
    matchresults2 = SAVE_DIR + fn + "_Match2.txt"

    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()


    print "compiling complete"
    print("--- %s seconds ---" % (time.time() - start_time))

    print "Writing results to file"
    hc = open(matchresults,"w")
    hc.write("filename locus allele read_dir sequence seq_Len count allele_Count allele_ratio total_ratio  \n")
    hc.close()
    hc = open(matchresults2,"w")
    hc.write("filename locus allele sequence seq_Len count allele_Count allele_ratio total_ratio  \n")
    hc.close()



    #get total number of reads
    queryTotal = "SELECT count(seq) As TotalReads FROM tempcontent WHERE userID = {0}".format(userID)
    #print queryTotal
    queryCount = "SELECT locus, Count(seq) As TotalReads FROM tempcontent WHERE userID = {0} Group by locus".format(userID)

    cursor2.execute (queryTotal)
    tReads = cursor2.fetchone()
    totalReads = tReads[0]
    print "total reads: " + str(totalReads)

    cursor2.execute (queryCount)
    Readresults = cursor2.fetchall()

    for rec in Readresults:
        locus = rec[0]


        sCount = rec[1]
        print locus + ": " + str(sCount)
        # sort and count number of reads
        #filename locus allele read_dir sequence seq_Len reads allele_Count allele_ratio total_ratio num_repeats
        query = "SELECT tempcontent.locus, allele, readDir, " +\
            "IF(readDir = 'FWD',tempcontent.seq, tempcontent.seq_rev) as seq, length(tempcontent.seq)  as seqLen, IF(readDir = 'FWD', count(tempcontent.seq), count(tempcontent.seq_rev)) as seqTotal, " +\
            "((count(tempcontent.seq))/{}.0)".format(sCount) + " As allele_ratio, ((count(tempcontent.seq))/{}.0)".format(totalReads) + " As total_ratio, " +\
            "Concat((length(tempcontent.seq) div tblrepeats.replen),'.',(length(tempcontent.seq) mod tblrepeats.replen)) As repeats " +\
            "FROM tempcontent, tblrepeats  " +\
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {0}".format(userID) +\
            " Group by locus, allele, readDir, tempcontent.seq "


        cursor2.execute (query)
        getRecords = cursor2.fetchall()

        with open(matchresults,"a") as textfile:
            for seqRecord in getRecords:
                textfile.write(fn + ' ')
                textfile.write(' '.join(str(s).upper() for s in seqRecord) + '\n')
        textfile.close()

        query = "SELECT tempcontent.locus, allele, tempcontent.seq, length(tempcontent.seq)  as seqLen, count(tempcontent.seq) as seqTotal, " +\
            "((count(tempcontent.seq))/{}.0)".format(sCount) + " As allele_ratio, ((count(tempcontent.seq))/{}.0)".format(totalReads) + " As total_ratio, " +\
            "Concat((length(seq) div tblrepeats.replen),'.',(length(tempcontent.seq) mod tblrepeats.replen)) As repeats " +\
            "FROM tempcontent, tblrepeats  " +\
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {0}".format(userID) +\
            " Group by locus, allele, tempcontent.seq "

        cursor2.execute (query)
        getRecords = cursor2.fetchall()

        with open(matchresults2,"a") as textfile2:
            for seqRecord in getRecords:
                textfile2.write(fn + ' ')
                textfile2.write(' '.join(str(s).upper() for s in seqRecord) + '\n')
        textfile2.close()

    cursor2.execute("DELETE FROM tempuser WHERE userID = {}".format(userID))
    cursor2.execute("DELETE FROM tempcontent WHERE userID = {}".format(userID))

    cursor2.close()
    DBconnections.closeDB(Con2)

def writeScreenResults():
    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()
    queryOrig = "SELECT UNIQUE"
    queryScreen = "SELECT tempcontent.locus, allele, readDir, oseq, " +\
            "IF(readDir = 'FWD',tempcontent.seq, tempcontent.seq_rev) as seq, " +\
            "length(tempcontent.seq)  as seqLen, IF(readDir = 'FWD', count(tempcontent.seq), " +\
            "count(tempcontent.seq_rev)) as seqTotal, " +\
            "((count(tempcontent.seq))/{}.0)".format(sCount) + " As allele_ratio, " +\
            "((count(tempcontent.seq))/{}.0)".format(totalReads) + " As total_ratio, " +\
            "Concat((length(tempcontent.seq) div tblrepeats.replen),'.',(length(tempcontent.seq) mod tblrepeats.replen)) As repeats " +\
            "FROM tempcontent, tblrepeats  " +\
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus +\
            "' AND userID = {0}".format(userID) +\
            " Group by locus, allele, readDir, tempcontent.seq "
    cursor2.execute(query)
    getRecords = cursor2.fetchall()



    print "<table border=1 style='border-collapse:collapse;'>"
    print "<tr><th>Filename</th><th>Locus</th><th>Allele</th><th>Read Dir</th>" +\
        "<th>Shortened Sequence</th><th>Seq Length</th><th>Count</th>" +\
        "<th>Count in allele</th><th>Allele Ratio</th><th>Total Ratio</th></tr>"
    for seqRecord in getRecords:
        locus = seqRecord[0]
        allele = seqRecord[1]
        readDir = seqRecord[2]
        orig_seq = seqRecord[3]
        shseq = seqRecord[4]
        seqLen = seqRecord[5]
        seqCount = seqRecord[6]
        alleleRatio = seqRecord[7]
        totRatio = seqRecord[8]
        numRepeats = seqRecord[9]
        print locus, readDir

def startProcess():
    processes = []
    userID = setUserID()

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
    numCPU = available_cpu_count()
    #pool = multiprocessing.Pool(numCPU)
    results = []
    job_server = pp.Server()
    extProcess.setSQL(userID)
    f1 = job_server.submit(extProcess.setProcess, (userID,))



    #start_extProcess(userID)
    #writeTextResults (nfile, userID)
    #writeScreenResults(userID)

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