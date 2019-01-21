#!/usr/bin/env python
# -*- coding: utf-8 -*-


from requests.packages.urllib3.exceptions import InsecureRequestWarning
from typing import Dict, List
from lxml import html, etree
import json
import os
import requests
author = 'Nathan Wu'
version = '1.0.0'


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# starting point .. the upass website
#
UPASS_TRANSLINK_URL = 'https://upassbc.translink.ca/'
# expected url after POST requests
# this website should be your schools authentication website after choosing
# your school from the dropdown box
UPASS_URL_POST = 'https://authentication.ubc.ca/idp/profile/SAML2'


class UPass():
    def __init__(self):
        self.load_config_files()
        print "Object created"

    def load_config_files(self):
        print "Config files loaded successfully"

    def request(self):
        print "Attempting to request"
        self.requestPass()

    def requestPass(self):
        r = requests.Session()

        # get upassbc website and make sure the connection is good (200)
        requestSite = r.get(UPASS_TRANSLINK_URL, verify=False)

        # select school from dropdown and make sure connection to authentication site is good
        requestSelectSchool = r.post(
            'https://upassbc.translink.ca/', data={'PsiId': 'ubc'}, verify=False)
        assert (requestSite.status_code == 200), "r1_error_status"
        assert (requestSite.url
                == UPASS_TRANSLINK_URL), "requestSite error: cannot access translink upass website"

        assert (requestSelectSchool.status_code
                == 200), "requestSelectSchool_error_status"
        assert (requestSelectSchool.url.startswith(UPASS_URL_POST)
                ), "requestSelectSchool error: chosen school does not match authentication site"

        # parse signin form, get all the hidden fields, combined them with username and password in the config file
        # tree = html.fromstring(requestSelectSchool.content)
        # form = tree.find('.//form[@class="signin-form"]')
        # hidden_fields = form.findall('.//input[@type="hidden"]')

            # school_data: Dict[str, str] = self.school_user_pass
            # for hidden_field in hidden_fields:
            #     school_data[hidden_field.name] = hidden_field.value

        # signin post request
        r3 = r.post(
            requestSelectSchool.url, data={'username' : 'USERNAME', 'password' : 'PASSWORD'})

        assert (r3.status_code == 200), "r3_error_status"
        # assert (r3.url.startswith(
        #     'https://idp.sfu.ca/idp/profile')), "r3_error_url"

        # below request r4 and r5 are due to python requests library doesn't load javascript in the webpage,
        # there are javascript to automatically submit those two forms in the webpage, here we mannally do it
        tree = html.fromstring(r3.content)
        form = tree.find('.//form')
        fields = form.findall('.//input')
        translink_data = {}
        for field in fields:
            translink_data[field.name] = field.value
        r4 = r.post('https://upassadfs.translink.ca/adfs/ls/',
                    data=translink_data)
        assert (r4.status_code == 200), "r4_error_status"
        assert (r4.url == 'https://upassadfs.translink.ca/adfs/ls/'), "r4_error_status"

        tree = html.fromstring(r4.content)
        form = tree.find('.//form')
        fields = form.findall('.//input')
        data = {}
        for field in fields:
            data[field.name] = field.value
        r5 = r.post('https://upassbc.translink.ca/fs/', data=data)
        assert (r5.status_code == 200), "r5 error"
        assert (r5.url == 'https://upassbc.translink.ca/fs/'), "r5 error: could not log into translink from your school website "

        # check if there are new month eligibility need to request
        tree = html.fromstring(r5.content)
        form = tree.find('.//form[@action="/fs/Eligibility/Request"]')
        hidden_fields = form.findall('.//input[@type="hidden"]')
        checkbox_fields = form.findall('.//input[@type="checkbox"]')
        data = {}
        for hidden_field in hidden_fields:
            data[hidden_field.name] = hidden_field.value
        for checkbox_field in checkbox_fields:
            data[checkbox_field.name] = 'true'
        if len(checkbox_fields) == 0:
            print('There is no new request')
        else:
            # request eligibility
            print('Request new month eligibility')
            r6 = r.post(
                'https://upassbc.translink.ca/fs/Eligibility/Request/', data=data)
            assert (r6.status_code == 200), "r6 error"
            # print(r6.url)
            # assert(r6.url.startswith('https://upassbc.translink.ca/'))

            # check if we request successful
            tree = html.fromstring(r6.content)
            form = tree.find('.//form[@action="/fs/Eligibility/Request"]')
            checkbox_fields = form.findall('.//input[@type="checkbox"]')
            if len(checkbox_fields) == 0:
                print('Request successful')
            else:
                print('Request failed')


def main():
    autopass = UPass()
    autopass.request()
    print "Successfully Requested"


if __name__ == '__main__':
    main()
