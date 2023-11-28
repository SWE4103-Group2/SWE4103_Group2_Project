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
# pip install mysql-connector-python
import mysql.connector

############### END: BASIC IMPORTS ##################

s_ConfigFilePath = 'main/config.json'

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
config = {
    'user': 'swegrp2',
    'password': 'D@tabase',
    'host': 'group2server.mysql.database.azure.com',
    'database': 'sweprojectdb',
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Function to generate simulated sensor data
def generate_sensor_data():
    # Simulate data or generate an error
    if randint(0, 100) < 90:  # 99.9% chance of valid data
        return random.uniform(f_RangeMin, f_RangeMax) # return a value in a set range (can be made configurable) assumed float
    else:
        return -1 # equivalent to null
    
# Function to update the database
def update_database(s_SerialNumber, i_DataValue):
    now = datetime.datetime.now() # get current time
    timestamp = now.strftime(s_TimeFormat) # make current time into timestamp
    select_query = "SELECT id FROM sensor WHERE serialnumber = %s"

    cursor.execute(select_query, (s_SerialNumber,))
    sensor_id = cursor.fetchone()
    if sensor_id != None:
        sensor_id = sensor_id[0]
        insert_query = "INSERT INTO value (sensorid, val, timestamp, serialnum) VALUES (%s, %s, %s, %s)"
        values = (sensor_id, i_DataValue, timestamp, s_SerialNumber)
        cursor.execute(insert_query, values)
        conn.commit()
    else:
        print("Could not update database.")
    
    
def main():
    lst_serial_numbers = ["Water_LakeHuron_S0003"]
    for i in range(0,5): # generate 5 values for sensors in list
        for serialNum in lst_serial_numbers: # to get name of file
            data_value = generate_sensor_data() # Simulate sensor data generation
            update_database(serialNum, data_value)
        time.sleep(i_SamplingRate) # Wait for the next sampling interval
   
    
    

if __name__ == "__main__":
    main()
