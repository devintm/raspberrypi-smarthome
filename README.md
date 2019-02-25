# README #

This repository stores all relevant code to the smart home and automation raspberry pi rig I am developing.  Most of the code is python but there may also be C code.

### TODO ###

# Adafruit DHT11 library
# DHT11 Humidity & Temperature Sensor

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo apt-get install build-essential python-dev
sudo python setup.py install



# Google Spreadsheet Logger
sudo pip install gspread oauth2client

sudo apt-get update
sudo apt-get install python-openssl


# Temperature & Humidity Logger Service
sudo cp temp_logger.sh /etc/init.d/temp_logger
sudo chmod +x /etc/init.d/temp_logger
sudo update-rc.d temp_logger defaults