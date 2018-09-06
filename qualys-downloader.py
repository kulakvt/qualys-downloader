#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
qualys-downloader.py
v0.1
Updated on Wed Sep  5 23:29:02 2018

Written and tested using: Python 2.7.15, macOS 10.13.6 (17G65), Darwin 17.7.0

This script uses the Qualys API to bulk download scan CSV files
for all processed scans listed in a scan history CSV when given:

1. API URL with desired options
2. Headers
3. Username
4. Password

The default API URL provided will download standard CSV scan reports. Headers
do not need to be changed, but do need to be specified for the call to be successful.
Username and password are the same that you use for web UI login. They are sent
via HTTPS, but you should secure this file and not store your password
here long term.

By adjusting variables, you can change the cooldown time period and retry attempts
per scan. Be careful when adjusting these to minimize calls to the API.

@author: andrew kulak
"""
# imports
import requests
import time
import os

# global variables

# local paths for history record and output
scansHistoryPath = './'
scanOutputPath = './'

# API details including username and password
baseAPIurl = 'https://qualysapi.qg3.apps.qualys.com/api/2.0/fo/scan/?action=fetch&output_format=csv_extended&scan_ref='
headers = { 'X-Requested-With': 'Python requests' }
username = ''
password = ''

# Specify retry attempts and cooldown to avoid flooding the API
retryAttempts = 5
timeToSleep = 3


try:
    # Check output path before proceeding
    try:
        if os.path.exists(scanOutputPath):
            print '[+] Files will be saved to %s' % (scanOutputPath)
        else:
            print '[-] %s not found, creating new directory...' % (scanOutputPath)
            os.mkdir(scanOutputPath)
    # Exception handling for OS-related error
    except IOError as e:
        print '[-] Could not open %s:' % (scansHistoryPath)
        print str(e)
    except Exception as e:
        print '[-] Unexpected error accessing %s:' % (scansHistoryPath)
        print str(e)
    
    # Read history file into script
    try:
        with open (scansHistoryPath, 'r') as file:
            rawList = file.readlines()
    # Exception handling for OS-related error
    except IOError as e:
        print '[-] Could not open %s:' % (scansHistoryPath)
        print str(e)
    except Exception as e:
        print '[-] Unexpected error accessing %s:' % (scansHistoryPath)
        print str(e)
    
    # Pull only scan data from history file
    try:
        scansList = []
        for line in rawList:
            if line.startswith('"Processed"'):
                scansList.append(line.split(',')[4].replace('"',''))
    # Exception handling for parsing error due to unusual file
    except IndexError as e:
        print '[-] Could not parse %s, please check original file:' % (scansHistoryPath)
        print str(e)
    except Exception as e:
        print '[-] Unexpected error parsing %s:' % (scansHistoryPath)
        print str(e)
        
    # Begin main loop over scans pulled from scan history file
    numScans = len(scansList)
    print '[+] Preparing to download %d scans read from scan history file' % (numScans)
    scanAttempt = 0
    for scan in scansList:
        if scanAttempt % 5 == 0:
            print '[+] %0.2f percent finished with scans...' % (100 * (float(scanAttempt) / numScans))
        scanID = scan
        attempts = 0
        
        # If there is a connection error, will retry set amount of times
        while attempts < retryAttempts:
            try:
                page = requests.post(baseAPIurl + scanID, headers = headers, auth = (username, password))
                if page.status_code != 200:
                    print '[-] Could not access page for %s' % (scanID)
                    print '[-] Sleeping and retrying...'
                    attempts = attempts + 1
                    time.sleep(10)
                else:
                    csvScanReport = page.content
                    break
            # Exception handling for error with requests library
            except Exception as e:
                print '[-] Error attempting connection to %s report:' % (scanID)
                print '[-] Retrying...'
                attempts = attempts + 1
                pass
        
        # If a scan could not be downloaded, will alert the user to stdout for retry
        if csvScanReport:
            print '[+] Success! %s was downloaded' % (scanID)
            try:
                with open (scanOutputPath + scanID.split('/')[1].replace('.','-') + '.csv', 'w') as file:
                    file.write(csvScanReport)
            # Exception handling for CSV file writing, will dump content to stdout if error occurs
            except IOError as e:
                print '[-] Could not write %s:' % (scanID)
                print str(e)
                print '[*] Dumping scan data:'
                print csvScanReport
            except Exception as e:
                print '[-] Unexpected error writing %s:' % (scanID)
                print str(e)
                print '[*] Dumping scan data:'
                print csvScanReport
            scanAttempt = scanAttempt + 1
        else:
            print '[-] Could not download scan report for %s after retrying' % (scanID)
            scanAttempt = scanAttempt + 1
        
        # Cools down before next call for set period of time
        print '[+] Sleeping for %d seconds before next call' % (timeToSleep)
        time.sleep(timeToSleep)     
    print '[+] All finished!'
# Exception handling for user-originated keyboard interrupt
except KeyboardInterrupt as e:
    print '[-] Keyboard interrupt detected. Exiting...'
except Exception as e:
    print '[-] Unexpected error encountered:'
    print str(e)
