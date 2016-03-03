#-------------------------------------------------------------------------------
# Name:        getFastQ2.py
# Purpose:      The purpose of this program is to 1) upload the Fastq file,
#               2) determine whether fasta conversion is necessary, 3) parse
#               if necessary, 4) possibly put in database as temporary use?
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
import multiprocessing
from multiprocessing import Pool, Queue, Manager
import time
start_time = time.time()

q = Queue()
def convertQ2A( qd, qname):
    qpath = qd + "/" + qname + ".fastq"
    cpath = qd + "/" + qname + ".fasta"
    SeqIO.convert(qpath, "fastq", cpath, "fasta")
    print "converted file to fasta"

    return cpath

def toLowerCase(cpath):
    with open(cpath,"r+b") as inputFile:
            content = inputFile.read()
            inputFile.seek(0)
            inputFile.write(content.lower())
    print "file in lower case"
    inputFile.close()

def putFile(fpath, fname):
        matchpath = fpath + "/" + fname + "_Match.fasta"
        otherpath = fpath + "/" + fname + "_Other.fasta"
        cpath = fpath + "/" + fname + ".fasta"
        matchresults = fpath + "/" + fname + "_Match.txt"

        # create a file if doesn't exist, or clear file if exists
        unmatched_handle = open(otherpath,"w")
        matched_handle = open(matchpath, "w")
        unmatched_handle.close()
        matched_handle.close()

        # make fasta in lower case
        toLowerCase(cpath)


def getFasta(fpath, fname):
    try:
        matchpath = fpath + "/" + fname + "_Match.fasta"
        otherpath = fpath + "/" + fname + "_Other.fasta"
        cpath = fpath + "/" + fname + ".fasta"
        matchresults = fpath + "/" + fname + "_Match.txt"

        # open fasta file

        cRecords = 0
        cLocusReads = 1

    except Exception, err:
        print str(err)

def processSeq(strfasta):
    sSplit = strfasta.split("||")
    userID = int(sSplit[0])
    fd = sSplit[1]
    fn = sSplit[2]
    seqHeader = sSplit[3]
    sequence = sSplit[4]

    #seqHeader = str(fasta.id)
    #sequence = str(fasta.seq.lower())
    matchpath = fd + "/" + fn + "_Match.fasta"
    otherpath = fd + "/" + fn + "_Other.fasta"

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
    cursor1.execute("SELECT locName, fwd_start, fwd_end, locType FROM tblloci ")
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
    else:
        hc = open(otherpath,"a")
        hc.write(">" + seqHeader + " 1:n:0:7 \n" + sequence + "\n")
        hc.close()
    return True



def writeResults(fd, fn):
    matchresults = fd + "/" + fn + "_Match.txt"
    matchresults2 = fd + "/" + fn + "_Match2.txt"

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

    cursor2.execute("DELETE FROM tempuser WHERE userID = {}".format(userID))
    cursor2.execute("DELETE FROM tempcontent WHERE userID = {}".format(userID))

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

def getFile():
    try:
        root = Tkinter.Tk()
        root.withdraw()
        fp = askopenfilename(parent=root)
        fpath = os.path.split(fp)
        fdir = os.path.dirname(fp)
        #print "fdir: " + fdir
        fnameext = os.path.basename(fp)
        fname = fnameext.split(".")
        return fdir, fname[0], fname[1]
    except IndexError as e:
        print "User cancelled file selection"

def getPairwise2Alignment(seq,locus):
    for a in pairwise2.align.localms(seq,locus, 2, -1, -1, -.1, one_alignment_only=True):
        #a1,a2, score, begin, end = a
        #return a1, a2, score, begin, end
        return a

def setUserID():
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    cursor1.execute("INSERT INTO tempuser (user) VALUES ('temp')")
    cursor1.execute("SELECT LAST_INSERT_ID() AS id")
    batchID = cursor1.fetchone()
    userID = batchID[0]
    cursor1.close()
    DBconnections.closeDB(Con1)
    return userID

if __name__ == '__main__':
    # get fastQ file - fd: file directory, fn: file name
    try:
        processes = []

        fd, fn, fex = getFile()
        print fd, fn, fex
        if fex == 'fastq':
        # convert good quality data to fasta
            fileA = convertQ2A(fd, fn)
        elif fex == 'fasta':
        # put the fastA file into temporary database
            putFile (fd, fn)

            userID = setUserID()
            print "UserID: " + str(userID)

            cpath = fd + "/" + fn + ".fasta"
            fasta_handle = open(cpath, 'rU')

            matchpath = fd + "/" + fn + "_Match.fasta"
            otherpath = fd + "/" + fn + "_Other.fasta"
            hc = open(matchpath,"w")
            hc.close()
            hc = open(otherpath,"w")
            hc.close()

            cRecords = 0
            #processPull = []
            numCPU = multiprocessing.cpu_count()
            print "Number of CPUs: {}".format(numCPU)
            pool = multiprocessing.Pool(numCPU)

            for fasta in SeqIO.parse(fasta_handle,"fasta"):
                if cRecords < 500:
                    passfasta = str(userID) + "||" + fd + "||" + fn + "||" + str(fasta.id) + "||" + str(fasta.seq.lower())
                    p = pool.imap_unordered(processSeq, (passfasta,))
                else:
                    break

                cRecords += 1

            pool.close()
            pool.join()

            fasta_handle.close()

            writeResults (fd, fn)
            print "Thank you for your patience"
            print("--- %s seconds ---" % (time.time() - start_time))
    except TypeError as e:
        print "File does not appear to be a FASTA file."
