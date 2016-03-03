#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        sendEmail.py
# Purpose:
#
# Author:      sfbailey
#
# Created:     29/02/2016
# Copyright:   (c) sfbailey 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#def sendEmail(email, batchID):
def sendEmail():
    FROM = "sfbailey@ncsu.edu"
    TO = "sfb64@yahoo.com"
    msg = MIMEMultipart()
    msg['From'] = "sfbailey@ncsu.edu"
    msg['To'] = "sfb64@yahoo.com"
    msg['Subject'] = "ALTIUS Complete"


    body ="The Altius Database has completed your analysis. \n" +\
        "Please return to <a href='http://localhost/getResults.html'>ALTIUS RESULTS</a> " +\
        " then put the Identification number in the box, and click Submit. This will open " +\
        "your results. \n <b>IDENTIFICATION NUMBER: " + batchID + "</b>"

    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
#try:

    server = smtplib.SMTP('52.72.251.89')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.sendmail(FROM, TO, text)

    print "Successfully sent email"
    server.quit()
#except Exception:
    #print "Error: unable to send email