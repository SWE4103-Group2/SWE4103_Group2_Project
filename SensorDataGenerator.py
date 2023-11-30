#####################################################
'''
   (SensorDataGenerator.py)   OGR

env: Windows

'''
################### BASIC IMPORTS ###################
import datetime
import time
import random
from random import randint
import json
# pip install mysql-connector-python
import mysql.connector
from SensorApplication4 import *

############### END: BASIC IMPORTS ##################

s_ConfigFilePath = "config.json"

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

lst_SerialNumbers         = config["lst_SerialNumbers"]
i_SamplingRate            = config["i_SamplingRate"]
s_TimeFormat              = config["s_TimeFormat"]
s_TimeZone                = config["s_TimeZone"]
f_RangeMin                = config["f_RangeMin"]
f_RangeMax                = config["f_RangeMax"]
s_User                    = config["User"]
s_Password                = config["Password"]
s_Host                    = config["Host"]
s_DatabasePath            = config["DatabasePath"]
############## END: CONFIGURATION ###################

# Initialize Database Connections
conn = mysql.connector.connect(user=s_User, password=s_Password, host=s_Host, database=s_DatabasePath)
cursor = conn.cursor()

# Function to generate simulated sensor data
def generate_sensor_data():
    if randint(0, 100) < 90:  # 99.9% chance of valid data
        return random.uniform(f_RangeMin, f_RangeMax) # return a value in a set range (can be made configurable) assumed float
    else:
        return -1 
    
# Function to update the database
def update_database(s_SerialNumber, i_DataValue):
    now = datetime.datetime.now() # get current time
    timestamp = now.strftime(s_TimeFormat) # make current time into timestamp
    select_query = "SELECT id FROM sensor WHERE serialnumber = %s"
    cursor.execute(select_query, (s_SerialNumber,))
    sensor_id = cursor.fetchone()

    if sensor_id is not None:
        sensor_id = sensor_id[0]
        insert_query = "INSERT INTO value (sensorid, val, timestamp, serialnum) VALUES (%s, %s, %s, %s)"
        values = (sensor_id, i_DataValue, timestamp, s_SerialNumber)
        cursor.execute(insert_query, values)
        conn.commit()
        return timestamp
    else:
        print(f"Could not update database with values for '{s_SerialNumber}'.")

def main():
    for i in range(2): # generate 5 values for sensors in list
        for serialNumber in lst_SerialNumbers: # to get name of file
            value = generate_sensor_data() # simulate sensor data generation
            timestamp = update_database(serialNumber, value)
            print(f"{serialNumber}\t{timestamp}\t{value}")
        time.sleep(i_SamplingRate) # wait for the next sampling interval
   
if __name__ == "__main__":
    main()
