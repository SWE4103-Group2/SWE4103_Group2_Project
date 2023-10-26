#####################################################
'''
   (Test.py)   OGR

env: Windows

'''
################### BASIC IMPORTS ###################
import datetime
import time
import random
from random import randint
import json
# pip install firebase_admin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
############### END: BASIC IMPORTS ##################

s_ConfigFilePath = 'C:/Users/olivi/Desktop/Fall_2023/SWE4103/Project/config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

s_ServiceAccountKeyPath   = config["s_ServiceAccountKeyPath"]
s_DatabaseURL             = config["s_DatabaseURL"]
s_SensorPath              = config["s_SensorPath"]
s_DataPath                = config["s_DataPath"]
s_SerialNumber            = config["s_SerialNumber"]
i_SamplingRate            = config["i_SamplingRate"]
s_TimeFormat              = config["s_TimeFormat"]
s_TimeZone                = config["s_TimeZone"]
f_RangeMin                = config["f_RangeMin"]
f_RangeMax                = config["f_RangeMax"]
############## END: CONFIGURATION ###################

# Initialize Database Connections
ref = ""
cred = credentials.Certificate(s_ServiceAccountKeyPath)
firebase_admin.initialize_app(cred, {'databaseURL': s_DatabaseURL})

# Function to generate simulated sensor data
def generate_sensor_data():
    # Simulate data or generate an error
    if randint(0, 100) < 90:  # 99.9% chance of valid data
        return random.uniform(f_RangeMin, f_RangeMax) # return a value in a set range (can be made configurable) assumed float
    else:
        return -1 # equivalent to null
    
# Function to update the data file
def update_data_file(s_SerialNumber, i_DataValue):
    now = datetime.datetime.now() # get current time
    timestamp = now.strftime(s_TimeFormat) # make current time into timestamp
    lst_toAdd = []

    data_row = {"timestamp": timestamp, "id": s_SerialNumber, "value": i_DataValue}

    lst_toAdd.append(data_row)
    
    ref = db.reference(s_DataPath) # re-directs
    for key in lst_toAdd:
        ref.push().set(key)

def main():
    lst_serial_numbers = [f"{s_SerialNumber}"]
    last_seen = None
    #while True:
    for i in range(0,16): # print 16 values for 3 sensors
        for serialNum in lst_serial_numbers: # to get name of file
            data_value = generate_sensor_data() # Simulate sensor data generation
            update_data_file(serialNum, data_value)
        time.sleep(i_SamplingRate) # Wait for the next sampling interval

if __name__ == "__main__":
    #create_sensor()
    main()