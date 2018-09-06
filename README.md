# qualys-downloader
Uses Qualys API calls to download multiple scans for reporting

## Introduction

This script uses the Qualys API to download bulk scans pulled from a scan history file for analysis and reporting.

## Preparing the Script

This script requires Qualys API access. To begin, first download a scan history .csv file using the Qualys web UI. You can use search tools to filter your scans and download records only for specific scans you would like to download. Once you have thies file, you will need to provide the following information within the script:

1. Local path to the scan history .csv file
2. Local path to directory where the downloaded scans should be saved
3. Your Qualys username
4. Your Qualys password

Credentials are sent over HTTPS, but you should not store your credentials when not using the script. In addition to this information, you may also need to change the API URL provided depending on the location of your Qualys subscription and the file format you would like to download. The call provided will download scans in the extended .csv format, which is similar to the .csv format file you can download manually using the web UI.

## Note

The Qualys API will not respond if an 'X-Requested-With' header is not provided. This header can be modified, but must be sent with the API call.
