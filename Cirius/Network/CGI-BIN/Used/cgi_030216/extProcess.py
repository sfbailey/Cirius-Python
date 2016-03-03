#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        extProcess.py
# Purpose:      This module is fired from a shell subprocess of results.py.
# The application will read the uploaded file and fire off a pool of processes.
# Each process takes with it a string containing userID, the header of the fasta file,
# the sequence of the fasta file and the filename of the fasta file. The previously
# database inserted user selections are pulled per process to develop the appropriate
# SQL string. The resulting sequnce (if match) is put into table tempContent.
# NOTES - MySQLdb was previously used, but was changed to pymysql 2/1/2016. The
#   Apache server kept losing the connection to the module.
#
# Author:      sfbailey
#
# Created:     28/01/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.pairwise2 import format_alignment
from itertools import groupby
from Bio import pairwise2
import DBconnections
import pymysql
import argparse
import sys
import psutil
import multiprocessing
from multiprocessing import Pool, Queue, Manager
import time


numanal = 0
UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"

def processSeq(strfasta):
    #print strfasta
    #str(userID) + "||" + nfile + "||" + str(allele) + "||" + mlist + "||" + recid + "||" + recseq + "||" + str(reccount)
    sSplit = strfasta.split("||")

    userID = sSplit[0]
    #print userID
    nfile = str(sSplit[1])
    #print nfile
    allele = str(sSplit[2])
    #print allele
    #mlist = str(sSplit[3])

    seqHeader = str(sSplit[3])
    #print seqHeader
    sequence = str(sSplit[4])
    #print sequence
    seqCnt = str(sSplit[5])
    seqCount = int(seqCnt)
    mrkrlist = sSplit[6]

    mlist = ""
    if len(mrkrlist)> 3:
        mSplit = mrkrlist.split("|")
        mlist = "','".join([str(item) for item in mSplit] )
        mlist = mlist + "'"
    else:
        if mrkrlist == 'All':
            mlist = ""
        else:
            mlist = mrkrlist

    Con3 = DBconnections.openDB()
    cursor3 = Con3.cursor()

    matchpath = SAVE_DIR + nfile + "_Match.fasta"
    otherpath = SAVE_DIR + nfile + "_Other.fasta"

    oseq = Seq(sequence)
    mkrev_seq = oseq
    rev_seq = mkrev_seq.reverse_complement()
    seqlocus = ""
    newseq = ""
    readDir = ""
    sqlstr = ""


    #Get SQL string
    sqlstr = sqlstr + "species LIKE 'human' "

    if allele != 'powerSeq':
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

    if len(mlist)> 3:
        if len(sqlstr) < 3:
            sqlstr = sqlstr + "AND"
        mcount = 0
        sqlstr = sqlstr + " AND locName IN ('"
        sqlstr = sqlstr + mlist
        sqlstr = sqlstr + ") "


    # Get locus information
    squery = "SELECT locName, fwd_start, fwd_end, locType FROM tblloci "
    if len(sqlstr) > 0:
        squery = squery + "WHERE " + sqlstr

    cursor3.execute(squery)
    primerData = cursor3.fetchall()

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

                if (Aend - 51) > 0:
                    lflank = oseq[Aend-51:Aend-1]
                else:
                    lflank = oseq[:Aend-1]
                if (Bbegin + 51) < len(oseq):
                    rfend = Bbegin + 51
                    rflank = oseq[Bbegin+1: rfend]
                else:
                    rflank = oseq[Bbegin+1:]
                seqlocus = row[0]
                allele = row[3]
                readDir ="FWD"
                startpt = Aend
                endpt = Bbegin
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

                    if (Cend - 51) > 0:
                        lflank = oseq[Cend-51:Cend-1]
                    else:
                        lflank = oseq[:Cend-1]
                    if (Dbegin + 51) < len(oseq):
                        rfend = Dbegin + 51
                        rflank = oseq[Dbegin+1: rfend]
                    else:
                        rflank = oseq[Dbegin+1:]
                    seqlocus = row[0]
                    allele = row[3]
                    readDir ="REV"
                    startpt = Cend
                    endpt = Dbegin

    if seqlocus == 'DYS389II':
        print "SAVE: " + seqlocus
        if len(str(newseq)) > 1:
            if readDir == "FWD":
                qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, lflank, rflank, startpt, endpt, seqcount, filename) " +\
                "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}', {}, {}, {},'{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(oseq), str(newseq), str(lflank), str(rflank), int(startpt), int(endpt), int(seqCount), nfile)
                #print qInsert
                seq = newseq
            else:
                qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, rev_seq, lflank, rflank, startpt, endpt, seqcount, filename) " +\
                "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}','{}',{}, {}, {}, '{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(oseq), str(newseq), str(newseq.reverse_complement()), str(lflank), str(rflank), int(startpt), int(endpt), int(seqCount), nfile)
                #print qInsert
                seq = newseq

            cursor3.execute(qInsert)
            cursor3.execute("COMMIT")
            hc = open(matchpath,"a")
            hc.write(">" + seqHeader + " 1:n:0:7 " + str(seqCount) + "\n" + sequence + "\n")
            hc.close()

            newseqlocus = 'DYS389I'
            locusFwdSeqEnd = 'tacatagataat'
            locFwdLenE = len(locusFwdSeqStart)

            b = getPairwise2Alignment(seq, locusFwdSeqEnd)
            Ba1,Ba2, Bscore, Bbegin, Bend = b
            lenFMB = int(Bend) - int(Bbegin)
            if ((int(locFwdLenE)) >= lenFMB) and Bscore >20:

                    seqI = seq[:Bbegin]
                    endpt = startpt + len(seqI) + 1
                    if readDir == "FWD":
                        qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, lflank, startpt, endpt, seqcount, filename) " +\
                            "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}', {}, {}, {},'{}')".format(userID, str(seqHeader), str(newseqlocus), str(allele), readDir, str(oseq), str(seqI), str(lflank), int(startpt), int(endpt), int(seqCount), nfile)
                    else:
                        qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, rev_seq, lflank, startpt, endpt, seqcount, filename) " +\
                        "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}', {}, {}, {}, '{}')".format(userID, str(seqHeader), str(newseqlocus), str(allele), readDir, str(oseq), str(seqI), str(seqI.reverse_complement()), str(lflank), int(startpt), int(endpt), int(seqCount), nfile)
                    #print qInsert
                    print "SAVE: " + newseqlocus
                    cursor3.execute(qInsert)
                    cursor3.execute("COMMIT")
            else:

                locusRevSeqEnd = Seq(locusFwdSeqEnd).reverse_complement()
                d = getPairwise2Alignment(seq, locusRevSeqEnd)
                Da1,Da2, Dscore, Dbegin, Dend = d
                print Da1, Da2, Dscore
                lenFMD = int(Dend) - int(Dbegin)
                if ((int(locFwdLenE)) >= lenFMD) and Dscore >20 :

                    seqI = seq[:Dbegin]
                    print str(seqI)
                    endpt = startpt + len(seqI) + 1
                    print readDir
                    if readDir == "FWD":
                        qNInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, lflank, startpt, endpt, seqcount, filename) " +\
                            "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}', {}, {}, {},'{}')".format(userID, str(seqHeader), str(newseqlocus), str(allele), readDir, str(oseq), str(seqI), str(lflank), int(startpt), int(endpt), int(seqCount), nfile)
                    else:
                        qNInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, rev_seq, lflank, startpt, endpt, seqcount, filename) " +\
                        "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}', {}, {}, {}, '{}')".format(userID, str(seqHeader), str(newseqlocus), str(allele), readDir, str(oseq), str(seqI.reverse_complement()), str(seqI), str(lflank), int(startpt), int(endpt), int(seqCount), nfile)
                    #print qNInsert
                    print "SAVE: " + newseqlocus
                    cursor3.execute(qNInsert)
                    cursor3.execute("COMMIT")
        else:
            hc = open(otherpath,"a")
            hc.write(">" + seqHeader + " 1:n:0:7 " + str(seqCount) + "\n" + sequence + "\n")
            hc.close()

    else:
        if len(str(newseq)) > 1:
            print "SAVE: " + seqlocus
            if readDir == "FWD":
                qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, lflank, rflank, startpt, endpt, seqcount, filename) " +\
                "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}', {}, {}, {},'{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(oseq), str(newseq), str(lflank), str(rflank), int(startpt), int(endpt), int(seqCount), nfile)
            else:
                qInsert = "INSERT INTO tempcontent (userID, header, locus, allele, readdir, oseq, seq, rev_seq, lflank, rflank, startpt, endpt, seqcount, filename) " +\
                "VALUES ( {},'{}', '{}','{}', '{}', '{}', '{}','{}','{}','{}',{}, {}, {}, '{}')".format(userID, str(seqHeader), str(seqlocus), str(allele), readDir, str(oseq), str(newseq), str(newseq.reverse_complement()), str(lflank), str(rflank), int(startpt), int(endpt), int(seqCount), nfile)

            #print qInsert

            cursor3.execute(qInsert)
            cursor3.execute("COMMIT")

            hc = open(matchpath,"a")
            hc.write(">" + seqHeader + " 1:n:0:7 " + str(seqCount) + "\n" + sequence + "\n")
            hc.close()

        else:
            hc = open(otherpath,"a")
            hc.write(">" + seqHeader + " 1:n:0:7 " + str(seqCount) + "\n" + sequence + "\n")
            hc.close()

    cursor3.close()
    DBconnections.closeDB(Con3)
    return True

def getPairwise2Alignment(seq,locus):
    for a in pairwise2.align.localms(seq,locus, 2, -1, -1, -.1, one_alignment_only=True):
        #a1,a2, score, begin, end = a
        #return a1, a2, score, begin, end
        return a

def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""
    return psutil.cpu_count()

def writeFile(userID, fn):
    matchresults = SAVE_DIR + fn  + "_MatchResults.txt"

    Con2 = DBconnections.openDB()
    cursor2 = Con2.cursor()

    hc = open(matchresults,"w")
    hc.write(fn + "\nlocus allele read_dir sequence seq_Len count allele_Count total_ratio codis \n")
    hc.close()

    #get total number of reads
    queryTotal = "SELECT SUM(seqcount) As TotalReads FROM tempcontent WHERE userID = {}".format(userID)
    qLocus = "SELECT locus FROM tempcontent WHERE userID = {} Group by locus".format(userID)
    cursor2.execute (queryTotal)
    tReads = cursor2.fetchone()
    totalReads = tReads[0]
    print "<br/>total reads: " + str(totalReads)

    cursor2.execute (qLocus)
    locuslinks = cursor2.fetchall()
    links = 0

    queryCount = "SELECT locus, SUM(seqcount) As TotalReads FROM tempcontent WHERE userID = {} Group by locus".format(userID) +\
            " ORDER BY locus"

    cursor2.execute (queryCount)
    Readresults = cursor2.fetchall()

    for rec in Readresults:
        locus = rec[0]
        sCount = rec[1]
        # sort and count number of reads
        #filename locus allele read_dir sequence seq_Len reads allele_Count allele_ratio total_ratio num_repeats
        query = "SELECT tempcontent.locus, allele, readdir, tempcontent.seq as seq, length(tempcontent.seq)  as tcseqlen, " +\
            "SUM(seqcount) as seqCounts, " +\
            "((SUM(tempcontent.seqcount))/{}.0)".format(sCount) + " As allele_ratio, " +\
            "((SUM(tempcontent.seqcount))/{}.0)".format(totalReads) + " As total_ratio, " +\
            "tblcodis.codis " +\
            "FROM tempcontent, tblcodis  " +\
            "WHERE tempcontent.locus = '" + locus + "' AND userID = {} ".format(userID) +\
            "AND tempcontent.locus = tblcodis.locName AND length(tempcontent.seq) = tblcodis.seqlen " +\
            " Group by allele, locus, readDir, tempcontent.seq " +\
            " Order by SUM(seqcount) desc, tempcontent.seq, readdir "

        cursor2.execute (query)
        getRecords = cursor2.fetchall()

        with open(matchresults,"a") as textfile:

            for seqRecord in getRecords:
                textfile.write(' '.join(str(s) for s in seqRecord) + '\n')
        textfile.close()

    cursor2.close()
    DBconnections.closeDB(Con2)

def main():

    id_seq = {}
    seq_count = {}
    Con1 = DBconnections.openDB()
    cursor1 = Con1.cursor()
    query = "select tempuser.userID, tempuser.userfile, tempuser.rsingles, " +\
        "tempuser.allele, tempwork.batchID, tempuser.email " +\
        "from tempuser, tempwork " +\
        "where tempuser.userID = tempwork.userID " +\
        "and tempwork.pflag = 1 " +\
        "group by tempwork.batchID " +\
        "order by tsubmit"

    cursor1.execute(query)
    getRecords = cursor1.fetchall()

    for rec in getRecords:
        start_time = time.time()
        userID = rec[0]
        filename = rec[1]
        remvSingles = rec[2]
        allele = rec[3]
        batchID = rec[4]
        userEmail = rec[5]
        mlist = ""
        fname = filename.split(".")
        nfile = fname[0]
        ext = fname[1]

        sqlstr = "select marker from tempmarker, tempuser, tempwork where tempuser.userID = tempwork.userID AND tempwork.batchID = tempmarker.batchID AND tempuser.userID = %d" % (userID)
        cursor1.execute(sqlstr)
        markers = cursor1.fetchall()
        for m in markers:
            if len(mlist)> 1:
                mlist = mlist + "|"
            mlist += "".join(m)


        fname = filename.split(".")
        nfile = fname[0]
        ext = fname[1]
        cpath = UPLOAD_DIR + nfile + "." + ext


        cRecords = 0
        numCPU = available_cpu_count()
        pool = multiprocessing.Pool(numCPU)
        results = []

        records= list(SeqIO.parse(cpath,'fasta'))
        print "Total reads: %i" % len(records)

        for seqrecord in records:
            id_seq[seqrecord.id] = seqrecord.seq
            seq_count[seqrecord.seq] = seq_count.get(seqrecord.seq, 0) + 1

        sorted_seq_count = sorted(seq_count, key=seq_count.get, reverse=True)

        for k in sorted_seq_count:
            recseq = k
            reccount = seq_count[k]
            recid = id_seq.keys()[id_seq.values().index(k)]
            print str(reccount)
            if str(remvSingles) == 'True':
                if reccount > 1:
                #if cRecords < 20:
                    passfasta = str(userID) + "||" + nfile + "||" + str(allele)
                    passfasta = passfasta +  "||" + recid + "||" + recseq + "||" + str(reccount)
                    passfasta = passfasta +  "||" + mlist
                    p = pool.imap_unordered(processSeq, (passfasta,))

                    #cRecords += 1
                else:
                    break
            else:
                #if cRecords < 20:
                    passfasta = str(userID) + "||" + nfile + "||" + str(allele)
                    passfasta = passfasta +  "||" + recid + "||" + recseq + "||" + str(reccount)
                    passfasta = passfasta + "||" + mlist
                    p = pool.imap_unordered(processSeq, (passfasta,))

                    #hc.write(">" + str(recid) + " 1:n:0:7 " + str(reccount) + "\t" + str(recseq) + "\n")
                    cRecords += 1
                #else:
                    #break

        pool.close()
        pool.join()

        cursor1.close()
        DBconnections.closeDB(Con1)
        id_seq.clear()
        seq_count.clear()

        # put in user file information: timeAnalyze, onumlines, numlines
        timeComplete = (time.time() - start_time)
        timeAnalyzed =  "{0:.2f}".format( timeComplete)
        onumlines = len(records)

        Con1 = DBconnections.openDB()
        cursor1 = Con1.cursor()
        qsum = "SELECT SUM(seqcount) as scount from tempcontent where userID = {}".format(userID)

        cursor1.execute(qsum)
        numlines=cursor1.fetchone()[0]

        query = "UPDATE tempwork SET timeAnalyze = '{}', ".format(timeAnalyzed) +\
                "onumlines = {}, ".format(str(onumlines)) +\
                "numlines = {} ".format(str(numlines)) +\
                "WHERE userID = {}".format(userID)

        cursor1.execute(query)
        cursor1.execute("COMMIT")

        writeFile(userID, str(nfile))

        # update tempuser
        sqst = "UPDATE tempwork set pflag = 0 WHERE userID = {}".format(userID)

        cursor1.execute(sqst)
        cursor1.execute("COMMIT")
        # remove file from upload dir
        #fileRemoval.removal_of_file(cpath)

        print("--- %s seconds ---" % (time.time() - start_time))


    cursor1.close()
    DBconnections.closeDB(Con1)


if __name__ == '__main__':
    main()
