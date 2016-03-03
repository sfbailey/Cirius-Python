#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      sfbailey
#
# Created:     28/01/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.pairwise2 import format_alignment
from itertools import groupby
from Bio import pairwise2
import DBconnections
#import MySQLdb
import pymysql
import argparse
import sys
import psutil
#import multiprocessing
#from multiprocessing import Pool, Queue, Manager
import pp


sqlstr = ""
numanal = 0
UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

def processSeq(strfasta):
    sSplit = strfasta.split("||")
    userID = int(sSplit[0])
    fn = sSplit[1]
    seqHeader = sSplit[2]
    sequence = sSplit[3]
    print "sequence: " + sequence

    matchpath = SAVE_DIR + fn + "_Match.fasta"
    otherpath = SAVE_DIR + fn + "_Other.fasta"

    oseq = Seq(sequence)
    mkrev_seq = oseq
    rev_seq = mkrev_seq.reverse_complement()
    seqlocus = ""
    allele = ""
    newseq = ""
    readDir = ""

    #get locus
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    squery = "SELECT locName, fwd_start, fwd_end, locType FROM tblloci WHERE " + sqlstr
    print squery + "\n"
    cursor1.execute(squery)
    primerData = cursor1.fetchall()

    for row in primerData:
        locusFwdSeqStart = row[1].lower()
        locusFwdSeqEnd = row[2].lower()

        locFwdLenS = len(locusFwdSeqStart)
        locFwdLenE = len(locusFwdSeqEnd)

        # Forward Start
        a = getPairwise2Alignment(oseq, locusFwdSeqStart)
        Aa1, Aa2, Ascore, Abegin, Aend = a
        lenFMA = int(Aend) - int(Abegin)
        if ((int(locFwdLenS)) >= lenFMA) and Ascore >20:
            b = getPairwise2Alignment(oseq, locusFwdSeqEnd)
            Ba1,Ba2, Bscore, Bbegin, Bend = b
            lenFMB = int(Bend) - int(Bbegin)

            if ((int(locFwdLenE)) >= lenFMB) and Bscore >20 and Bbegin > Aend:
                newseq = oseq[Aend:Bbegin]
                lseq = oseq[:Aend]
                rseq = oseq[Bbegin:]
                seqlocus = row[0]
                allele = row[3]
                readDir ="FWD"
        else:
            #check reverse
            c = getPairwise2Alignment(rev_seq,locusFwdSeqStart)
            Ca1, Ca2, Cscore, Cbegin, Cend = c

            lenCMA = int(Cend) - int(Cbegin)
            if ((int(locFwdLenS)) >= lenCMA) and Cscore >20:
                d = getPairwise2Alignment(rev_seq,locusFwdSeqEnd)
                Da1,Da2, Dscore, Dbegin, Dend = d
                lenCMB = int(Dend) - int(Dbegin)
                if ((int(locFwdLenE)) >= lenCMB) and Dscore >20 and Dbegin > Cend:
                    newseq = rev_seq[Cend:Dbegin]
                    lseq = oseq[:Cend]
                    rseq = oseq[Dbegin:]
                    seqlocus = row[0]
                    allele = row[3]
                    readDir ="REV"

    cursor1.close()
    DBconnections.closeDB(Con1)

    if len(seqlocus) > 1:
        #q.put((seqHeader, sequence, seqlocus, allele, readDir, newseq))
        #print seqlocus, allele, readDir, newseq
        #print q.qsize()
        Con1 = DBconnections.openDB()
        cursor1 = Con1.cursor()
        if readDir == "FWD":
            qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, seq, lseq, rseq) " +\
                "VALUES ( {},'{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(newseq), str(lseq), str(rseq))

        else:
            qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, seq, seq_rev, lseq, rseq) " +\
                "VALUES ( {},'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(newseq), str(newseq.reverse_complement(), str(lseq), str(rseq)))
        print qInsert
        cursor1.execute(qInsert)
        cursor1.execute("COMMIT")
        cursor1.close()
        DBconnections.closeDB(Con1)
        hc = open(matchpath,"a")
        hc.write(">" + seqHeader + " 1:n:0:7 \n" + sequence + "\n")
        hc.close()
        print "Sequence match: FWD"
    else:
        hc = open(otherpath,"a")
        hc.write(">" + seqHeader + " 1:n:0:7 \n" + sequence + "\n")
        hc.close()
        print "Sequence match: REV"
    return True

def getPairwise2Alignment(seq,locus):
    for a in pairwise2.align.localms(seq,locus, 2, -1, -1, -.1, one_alignment_only=True):
        #a1,a2, score, begin, end = a
        #return a1, a2, score, begin, end
        return a

def setSQL(userID):
    global sqlstr
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    cursor1.execute("SELECT species, allele, markers, numanal FROM tempuser WHERE userID = {0}".format(int(userID)))
    rows = cursor1.fetchall()
    for row in rows:
        species = row[0]
        allele = row[1]
        markers = row[2]
        numanal = int(row[3])
    if species == 'animal':
        sqlstr = sqlstr + "species LIKE 'animal' "
    else:
        sqlstr = sqlstr + "species LIKE 'human' "
    if len(sqlstr) > 1:
        sqlstr = sqlstr + " AND "
    if allele == 'AnY':
        sqlstr = sqlstr + "locType LIKE 'Autosomal' or locType LIKE 'Y' "
    elif allele == 'AnX':
        sqlstr = sqlstr + "locType LIKE 'Autosomal' or locType LIKE 'X' "
    elif allele == 'XnY':
        sqlstr = sqlstr + "locType LIKE 'X' or locType LIKE 'Y' "
    elif allele == 'A':
        sqlstr = sqlstr + "locType LIKE 'Autosomal' "
    elif allele == "X":
        sqlstr = sqlstr + "locType LIKE 'X' "
    elif allele == "Y":
        sqlstr = sqlstr + "locType LIKE 'Y' "
    else:
        sqlstr = sqlstr + "locType LIKE 'Autosomal' OR locType Like 'X' OR locType Like 'Y' "

    if markers != 'NULL':
            if len(sqlstr) < 3:
                sqlstr = sqlstr + "AND"
            if markers.find("|") > -1:
                markerList = markers.split("|")
                mcount = 0
                sqlstr = sqlstr +" AND locName IN ('"
                for m in markerList:
                    if mcount > 0:
                        sqlstr = sqlstr + "', '"
                    sqlstr = sqlstr + m
                    mcount += 1
                sqlstr = sqlstr + "') "
            else:
                sqlstr = sqlstr +" AND locName LIKE '" + markers + "'"


def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""
    return psutil.cpu_count()

def getFile(userID):
    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()
    query = "SELECT userfile, allele, markers, species, numanal from tempuser " +\
        "WHERE userID = {0}".format(userID)
    cursor2.execute(query)
    getRecords = cursor2.fetchall()
    for rec in getRecords:
        userfile = rec[0]
        allele = rec[1]
        markers = rec[2]
        species = rec[3]
        numanal = rec[4]
    print userfile, allele, markers, species, numanal
    cursor2.close()
    DBconnections.closeDB(Con2)
    return userfile, allele, markers, species, numanal

def main(userID):
    filename, allele, markers, species, numanal = getFile(userID)

    fname = filename.split(".")
    nfile = fname[0]
    ext = fname[1]
    cpath = UPLOAD_DIR + nfile + "." + ext
    setSQL(userID)

    print str(userID)+ "<br/>"
    print nfile + "<br/>"
    print str(fasta.id) + "<br/>"
    print str(fasta.seq.lower()) + "<br/>" + "<br/>"
    print sqlstr + "<br/>" + "<br/>"
    cRecords = 0
    numCPU = available_cpu_count()
    #pool = multiprocessing.Pool(numCPU)
    results = []
    print numCPU

    fasta_handle = open(cpath, 'rU')
    for fasta in SeqIO.parse(fasta_handle,"fasta"):
        if cRecords < int(numanal):


            passfasta = str(userID) + " " + nfile + " " + str(fasta.id) + " " + str(fasta.seq.lower())

            #results.append(pool.imap_unordered(start_extProcess, (cmd,)))
            p = pool.imap_unordered(processSeq, (passfasta,))

        else:
            break

        cRecords += 1


    pool.close()
    pool.join()

    fasta_handle.close()

if __name__ == '__main__':
    print
    userID = sys.argv[1]
    print userID

    main(userID)
