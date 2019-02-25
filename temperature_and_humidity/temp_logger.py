#!/usr/bin/python

# Google Spreadsheet DHT Sensor Data-logging Example

# Depends on the 'gspread' and 'oauth2client' package being installed.  If you
# have pip installed execute:
#   sudo pip install gspread oauth2client

# Also it's _very important_ on the Raspberry Pi to install the python-openssl
# package because the version of Python is a bit old and can fail with Google's
# new OAuth2 based authentication.  Run the following command to install the
# the package:
#   sudo apt-get update
#   sudo apt-get install python-openssl

# import json
import sys
import time
import datetime

import Adafruit_DHT
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT11

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN = 24
# Example of sensor connected to Beaglebone Black pin P8_11
# DHT_PIN  = 'P8_11'

# Google Docs OAuth credential JSON file.  Note that the process for authenticating
# with Google docs has changed as of ~April 2015.  You _must_ use OAuth2 to log
# in and authenticate with the gspread library.  Unfortunately this process is much
# more complicated than the old process.  You _must_ carefully follow the steps on
# this page to create a new OAuth service in your Google developer console:
#   http://gspread.readthedocs.org/en/latest/oauth2.html
#
# Once you've followed the steps above you should have downloaded a .json file with
# your OAuth2 credentials.  This file has a name like SpreadsheetData-<gibberish>.json.
# Place that file in the same directory as this python script.
#
# Now one last _very important_ step before updating the spreadsheet will work.
# Go to your spreadsheet in Google Spreadsheet and share it to the email address
# inside the 'client_email' setting in the SpreadsheetData-*.json file.  For example
# if the client_email setting inside the .json file has an email address like:
#   149345334675-md0qff5f0kib41meu20f7d1habos3qcu@developer.gserviceaccount.com
# Then use the File -> Share... command in the spreadsheet to share it with read
# and write acess to the email address above.  If you don't do this step then the
# updates to the sheet will fail!
GDOCS_OAUTH_JSON = 'RaspberryPiSmartHomeSpreadsheetCredentials.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'Raspberry Pi Smart Home'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 30


def check_initialization(worksheet):
    try:
        row_iter = iter(worksheet.get_all_values())
        first_row = row_iter.next()
        if "Date" in first_row or "Humidity" in first_row:
            print("The spreadsheet has already been initialized.")
            return
        else:  # Need to initialize
            initalize_spreadsheet(worksheet)
    except:  # No values, need to intialize
        initalize_spreadsheet(worksheet)


def initalize_spreadsheet(worksheet):
    """Initializes the spreadsheet by deleting the empty rows and writing a header."""
    print("Initializing spreadsheet now...")
    worksheet.resize(1)
    worksheet.insert_row(["Date", "Temp (C)", "Humidity"])


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        # Check spreadsheet is setup for data logging
        check_initialization(worksheet)
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)


def get_sensor_reading():
    # Attempt to get sensor reading.
    humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temp is None:
        time.sleep(2)
        continue

    print('Temperature: {0:0.1f} C'.format(temp))
    print('Humidity:    {0:0.1f} %'.format(humidity))

    return humidity, temp


def main():
    print('Logging sensor measurements to {0} every {1} seconds.'.format(
        GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')
    worksheet = None
    while True:
        # Login if necessary.
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

        (humidity, temp) = get_sensor_reading()

        # Append the data in the spreadsheet, including a timestamp
        try:
            worksheet.append_row((datetime.datetime.now(), temp, humidity))
        except:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again')
            worksheet = None
            time.sleep(FREQUENCY_SECONDS)
            continue

        # Wait 30 seconds before continuing
        print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
        time.sleep(FREQUENCY_SECONDS)

if __name__ == "__main__":
    main()
