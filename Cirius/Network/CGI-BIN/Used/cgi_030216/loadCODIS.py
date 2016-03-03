#-------------------------------------------------------------------------------
# Name:       loadCODIS.py
# Purpose:      upload contents of known file into animalsq db
#
# Author:      sfbailey
#
# Created:     10/11/2015
# Copyright:   (c) sfbailey 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pymysql
import sys
import Tkinter
import tkFileDialog
from tkFileDialog import askopenfilename
import DBconnections

def loadToSQL():
    root = Tkinter.Tk()
    root.withdraw()
    file_path = askopenfilename(parent=root)
    print file_path

    db = DBconnections.openDB()
    cursor = db.cursor()
    count = 0

    with open(file_path, 'r') as f:
        for line in f:

                pl = line.split(',')
                print "START"
                query = "INSERT INTO tblCODIS (locName, seqLen, codis) VALUES ("
                query = query + "'{}',{}, '{}')".format(pl[0], pl[1], pl[2].strip(" ").rstrip('\n'))
                print query

                cursor.execute(query)


    f.close()
    db.commit()
    db.close()

    #closeDB(Con)
    #Con.close()


def main():
    loadToSQL()
main()