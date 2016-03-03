#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        extProcess.py
# Purpose:      This is the external file to process the fasta lines
#
# Author:      sfbailey
#
# Created:     27/01/2016
# Copyright:   (c) sfbailey 2016
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
import DBconnections
import argparse
import sys

sqlstr = ""
numanal = 0
UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

def processSeq(userID, nfile, seqHeader, sequence):
    """
    sSplit = strfasta.split("||")
    userID = int(sSplit[0])
    nfile = sSplit[1]
    seqHeader = sSplit[2]
    sequence = sSplit[3]
    """

    matchpath = SAVE_DIR + nfile + "_Match.fasta"
    otherpath = SAVE_DIR + nfile + "_Other.fasta"

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
                nseqm1 = oseq[Aend-1:Bbegin]
                nseqm1l = oseq[:Aend-1]
                nseqm1r = oseq[Bbegin:]
                rstart = len(lseq)+1
                rend = rstart + len(newseq)

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
                    lseq = rev_seq[:Cend]
                    rseq = rev_seq[Dbegin:]
                    nseqm1 = rev_seq[Cend-1:Dbegin]
                    nseqm1l = rev_seq[:Cend-1]
                    nseqm1r = rev_seq[Dbegin:]
                    rstart = len(lseq)+1
                    rend = rstart + len(newseq)

                    seqlocus = row[0]
                    allele = row[3]
                    readDir ="REV"

    cursor1.close()
    DBconnections.closeDB(Con1)

    print len(seqlocus)

    if len(seqlocus) > 1:
        Con1 = DBconnections.openDB()
        cursor1 = Con1.cursor()
        if readDir == "FWD":
            print readDir
            qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, seq, lseq, rseq," +\
                "oseq, seqm1, lm1, rm1, startpt, endpt) " +\
                "VALUES ({},'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {})".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(newseq), str(lseq), str(rseq), str(sequence), str(nseqm1), str(nseqm1l), str(nseqm1r), int(rstart), int(rend))

        else:
            print readDir
            qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, seq, seq_rev, lseq, rseq, " +\
                "oseq, seqm1, seqm1_rev, lm1, rm1, startpt, endpt)" +\
                "VALUES ({},'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {})".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(newseq.reverse_complement()), str(newseq), str(lseq), str(rseq), str(sequence), str(nseqm1.reverse_complement()), str(nseqm1), str(nseqm1l), str(nseqm1r), int(rstart), int(rend))

        print qInsert
        cursor1.execute(qInsert)
        cursor1.execute("COMMIT")
        cursor1.close()
        DBconnections.closeDB(Con1)
        hc = open(matchpath,"a")
        hc.write(">" + seqHeader + " 1:n:0:7 \n" + sequence + "\n")
        hc.close()
    else:
        hc = open(otherpath,"a")
        hc.write(">" + seqHeader + " 1:n:0:7 \n" + sequence + "\n")
        hc.close()
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



if __name__ == '__main__':
    print
    print sys.argv[0]
    userID = sys.argv[1]
    nfile = sys.argv[2]
    header = sys.argv[3]
    fasta = sys.argv[4]
    setSQL(userID)
    processSeq(userID, nfile, header, fasta)
