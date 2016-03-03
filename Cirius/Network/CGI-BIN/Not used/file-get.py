#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        file_get.py
# Purpose:
#
# Author:      sfbailey
#
# Created:     15/01/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Import modules for CGI handling
import cgi, cgitb
cgitb.enable()
# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
first_name = form.getvalue('first_name')
last_name  = form.getvalue('last_name')

print "Content-Type: text/html\n\n"
print "<html>"
print "<head>"
print "<title>Hello - Second CGI Program</title>"
print "</head>"
print "<body>"
print "<h2>Hello %s %s</h2>" % (first_name, last_name)
print "</body>"
print "</html>"