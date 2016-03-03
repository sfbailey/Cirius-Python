#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        openBrowser.py
# Purpose:      The purpose of this program is to 1) upload the Fastq file,
#               2) determine whether fasta conversion is necessary, 3) parse
#               if necessary, 4) possibly put in database as temporary use?
#
# Author:      sfbailey
#
# Created:     1/22/2016
# Copyright:   (c) sfbailey 2015
#-------------------------------------------------------------------------------
import webbrowser
new = 2 # open in a new tab, if possible

# open a public URL, in this case, the webbrowser docs
def openResults(userID):
    url = "results.py"
    webbrowser.open(url,new=new)
