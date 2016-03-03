#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        web_output.py
# Purpose:
#
# Author:      sfbailey
#
# Created:     15/01/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import cgi, cgitb
cgitb.enable()
import os, sys
import time, datetime
import codecs
from Bio.Seq import Seq
from Bio import SeqIO

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

UPLOAD_DIR = "/pythonScripts/upload/"
SAVE_DIR = "/pythonScripts/Results/"
new_path = ""
new_file_name = ""
nfile = ""
flag = False

# Create instance of FieldStorage
def save_uploaded_file(filename):
    global new_path
    global new_file_name
    global nfile
    message = ""

    filecontents = form.getvalue("fname")
    fcomp = filename.split(".")
    ffile = fcomp[0]

    extension = fcomp[1]
    #print ffile + ", " +  extension + "<br/>"

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
    new_file_name = ffile + "-" + st + "." + extension
    new_path = UPLOAD_DIR + new_file_name
    #print "new filename: " + new_file_name + "<br/>"
    #print "new path: " + new_path + "<br/>"

    output_file = open(new_path, 'wb')
    output_file.write(filecontents)
    output_file.close()

    cpath = UPLOAD_DIR + ffile + "-" + st +  ".fasta"
    nfile = ffile + "-" + st

    if extension == 'fastq':
        qpath = UPLOAD_DIR + ffile + "-" + st + ".fastq"
        SeqIO.convert(qpath, "fastq", cpath, "fasta")
        message = "File converted to fasta. <br>"


    with open(cpath,"r+b") as inputFile:
            content = inputFile.read()
            inputFile.seek(0)
            inputFile.write(content.lower())
    message = message + "File made to lower case. <br/>"

    return message

def print_header():
    print "content-type: text/html\n"
    f = codecs.open("header.html", 'r', 'utf-8')
    print f.read()

def print_footer():
    f = codecs.open("footer.html", 'r', 'utf-8')
    print f.read()



def page_has_loaded():
    self.log.info("Checking if {} page is loaded.".format(self.driver.current_url))
    try:
        new_page = browser.find_element_by_tag_name('html')
        return new_page.id != old_page.id
    except NoSuchElementException:
        return False

if __name__ == '__main__':
    form = cgi.FieldStorage()


    species=form.getvalue("species")
    numanal=form.getvalue("numanal")
    allele = form.getvalue("fallele")
    markers=form.getvalue("markers")
    file_path = form.getvalue("fpath")
    messagesave = ""
    allelestr = "All"
    sqlstr = " "

    #print "file path: " + file_path
    #print "file name: " +os.path.basename(file_path) + "<br/>"
    try:
        filename = os.path.basename(file_path)
        messagesave = save_uploaded_file(filename)
        print "Content-Type: text/html\n\n"
        print_header();

        if allele != 'All':
            if allele == "AnY":
                allelestr = "Autosomal and Y"
            elif allele == "AnX":
                allelestr = "Autosomal and X"
            elif allele == "XnY":
                allelestr = "X and Y"
            elif allele == "A":
                allelestr = "Autosomal"
            elif allele == "X":
                allelestr = "X"
            elif allele == "Y":
                allelestr = "Y"

        """"<div class='comments white-bg col-md-9 col-sm-12'>" """
        HTML_SELECTIONS = "<div class='col-md-9'><h2>Cirius Selections: </h2>" +\
        "uploaded: %s <br/>" % filename +\
        "new file name: %s <br /> " % new_file_name +\
        "species: %s <br/>" % species +\
        "Number to analyze: %s <br/>" % numanal +\
        "Allele: %s <br/>" % allelestr +\
        "Selected markers: %s <br/>" % markers +\
        "%s" % (messagesave) +\
        "<br/><br/>"

        mc = 0
        strMarkers = ""
        if markers != 'All':
            if isinstance(markers, str) == True:
                strMarkers = markers
            else:
              for m in mymarkers:
                if m != 'All':
                    if len(strMarkers) > 1 :
                        strMarkers = strMarkers + "|"
                    strMarkers = strMarkers + m
                mc+=1


        HTML_FORM="<form action='results.py' method='post' id='fstart' class='comment-form' enctype='multipart/form-data'>" +\
        "<input type='text' id='fallele' name='fallele' value='%s'><br/>" % allele +\
        "<input type='text' id='fmarkers' name='fmarkers' value='%s'><br/>" % strMarkers +\
        "<input type='text' id='fspecies' name='fspecies' value='%s'><br/>" % species +\
        "<input type='text' id='ffile' name='ffile' value='%s'><br/>" % new_file_name +\
        "<input type='text' id='fnum' name='fnum' value='%s'><br/>" % numanal +\
        "If the above are correct, please click 'Submit'. The time to analyze your <br/>" +\
        "file will be relative to the number of markers selected. <br/>" +\
        "For example, running 100,000 records over 94 markers (all) will take approximately 1.5 hrs. <br/>" +\
        "<input type='submit' name='submit' id='submit' class='submit' value='Submit' >" +\
        "&nbsp;&nbsp;<input type='button' name='cancel' value='Cancel' onclick='window.history.back();'/> " +\
        "</form>"


        print HTML_SELECTIONS
        print HTML_FORM

        #print "User-Agent:", os.environ.get("HTTP_USER_AGENT", "N/A")

        print "</div>"
        print_footer();

    except TypeError as e:
        print "<div class='comments white-bg col-md-9 col-sm-12'>"
        print "File does not appear to be a FASTA file."
        print "</div>"
        print_footer();



