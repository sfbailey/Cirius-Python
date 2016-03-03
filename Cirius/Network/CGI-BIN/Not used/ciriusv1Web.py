#-------------------------------------------------------------------------------
# Name:        ciriusv1Web.py
# Purpose:      The purpose of this program is to 1) the processing of web
#               inputs and then 2) processing the information back in web format.
#
# Author:      sfbailey
#
# Created:     11/11/2015
# Copyright:   (c) sfbailey 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import MySQLdb
import sqlite3
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.pairwise2 import format_alignment
from itertools import groupby
from Bio import pairwise2
import sys
import Tkinter
from tkFileDialog import askopenfilename
import DBconnections
import os
import psutil
import web_output
import urllib2



UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"
sqlstr = ""





def writeResults(fn, userID):
    global start_time
    matchresults = SAVE_DIR + fn + "_Match.txt"
    matchresults2 = SAVE_DIR + fn + "_Match2.txt"

    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()


    print "compiling complete" + "<br/>"

    print "Writing results to file" + "<br/>"
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
    print "total reads: " + str(totalReads) + "<br/>"

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
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {}".format(userID) +\
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
            "WHERE tempcontent.locus = tblrepeats.locus AND tempcontent.locus LIKE '" + locus + "' AND userID = {}".format(userID) +\
            " Group by locus, allele, tempcontent.seq "

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

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)


def getPairwise2Alignment(seq,locus):
    for a in pairwise2.align.localms(seq,locus, 2, -1, -1, -.1, one_alignment_only=True):
        #a1,a2, score, begin, end = a
        #return a1, a2, score, begin, end
        return a

def setUserID(filename,species, allele, markers, numanal):
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    sqst = "INSERT INTO tempuser (user, userfile,species, allele, markers, numanal) VALUES (" +\
            "'temp','" + filename + ", '" + species + "','" + allele + "', '" +\
            markers + "', '" + numanal + "')"
    cursor1.execute(sqst)
    cursor1.execute("SELECT LAST_INSERT_ID() AS id")
    batchID = cursor1.fetchone()
    userID = batchID[0]
    cursor1.close()
    DBconnections.closeDB(Con1)
    return userID



def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""

    return psutil.cpu_count()

