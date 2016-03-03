#!c:/Python27/python -u
#-------------------------------------------------------------------------------
# Name:        waitHTML.py
# Purpose:      The purpose of this program is to 1) upload the Fastq file,
#               2) determine whether fasta conversion is necessary, 3) parse
#               if necessary, 4) possibly put in database as temporary use?
#
# Author:      sfbailey
#
# Created:     1/22/2016
# Copyright:   (c) sfbailey 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)
