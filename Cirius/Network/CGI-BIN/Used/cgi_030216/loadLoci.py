#-------------------------------------------------------------------------------
# Name:       loadLoci.py
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
            if count > 0:
                pl = line.split(',')
                print "START"
                query = "INSERT INTO tblloci (locName, locType, fwd_start, fwd_end, species) VALUES ("
                query = query + "'{}','{}', '{}', '{}', '{}')".format(pl[0], pl[1], pl[2], pl[3], pl[4].strip(" ").rstrip('\n'))
                print query

                cursor.execute(query)
            count += 1

    f.close()
    db.commit()
    db.close()

    #closeDB(Con)
    #Con.close()


def main():
    loadToSQL()
main()