
#####################################################
'''
   (SensorApplication.py)   OGR

env: Windows

'''
################### BASIC IMPORTS ###################
import pandas as pd
import numpy as np
import time
import datetime
import random
from random import randint
import os
import json
from datetime import datetime, timedelta
# pip install mysql-connector-python
import mysql.connector
# for testing
import unittest
############### END: BASIC IMPORTS ##################

s_ConfigFilePath = 'main/config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

s_User                    = config["User"]
s_Password                = config["Password"]
s_Host                    = config["Host"]
s_DatabasePath            = config["DatabasePath"]
############## END: CONFIGURATION ###################

# Initialize Database Connections
conn = mysql.connector.connect(user=s_User, password=s_Password, host=s_Host, database=s_DatabasePath)
cursor = conn.cursor()

# Sensor Object Class
class Sensor:

    i_NumObjects = {} # number of existing sensors

    def __init__(self, s_SensorType, s_Location, i_SamplingRate, s_SerialNumber=None):
            self.s_SensorType = s_SensorType
            self.s_Location = s_Location
            if s_SerialNumber is None:
                self.s_SerialNumber = self.generate_serial_number()
            else:
                self.s_SerialNumber = s_SerialNumber
            self.i_SamplingRate = i_SamplingRate
            self.i_ErrorFlag = 0
            self.s_Status = "ON"

    # Function to generate a unique serial number with the format: SensorType_Location_S000X 
    def generate_serial_number(self):
        try:
            cursor.execute("SELECT MAX(id) FROM sensor")
            result = cursor.fetchone()
            if result and result[0] is not None:
                max_id = result[0]
                next_id = max_id + 1
            else:
                next_id = 1  # If no records exist, start with ID 1
            next_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{next_id:04d}"
            insert_query = "INSERT INTO sensor (id, type, location, samplingRate, serialnumber) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (next_id, self.s_SensorType, self.s_Location, self.i_SamplingRate, next_serial_number))
            conn.commit()  # commit the changes to the database
            return next_serial_number
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    
    # Function that returns the sensor type
    def get_type(self):
        print(self.s_SensorType)
        return self.s_SensorType
  
    # Function to return the value of the sensor at a given timestamp
    def get_value(self, s_Timestamp):
        try:
            # Define your MySQL SELECT query to retrieve sensor data by timestamp
            select_query = "SELECT serialnum, val FROM value WHERE timestamp = %s AND serialnum = %s"

            cursor.execute(select_query, (s_Timestamp, self.s_SerialNumber, ))
            sensor_data = cursor.fetchone()

            if sensor_data:
                serial_number, value = sensor_data
                if self.s_SensorType == 'Energy':
                    if (value >= 0 and value <= 50):
                        print(f"Value of '{self.s_SerialNumber}' at '{s_Timestamp}' is: {value} KW")
                    else:
                        self.set_errorflag(1)
                        self.i_ErrorFlag = 1
                        print(f"An unexpected error occurred: unable to set state for '{self.s_SerialNumber}'")

                if self.s_SensorType == 'Water':
                    if (value >= 2 and value <= 4):
                        print(f"Value of '{self.s_SerialNumber}' at '{s_Timestamp}' is: {value} L/hour")
                    else:
                        self.set_errorflag(1)
                        self.i_ErrorFlag = 1
                        print(f"An unexpected error occurred: unable to set state for '{self.s_SerialNumber}'")
                return serial_number, value
            else:
                print(f"No data found for '{self.s_SerialNumber}' with timestamp: {s_Timestamp}")
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    # Function to set the value of the sensor at a specific timestamp in the historical data database
    def set_value(self, s_Timestamp, f_NewValue):
        try:
            update_query = "UPDATE value SET val = %s WHERE timestamp = %s AND serialnum = %s"
            cursor.execute(update_query, (f_NewValue, s_Timestamp, self.s_SerialNumber,))
            conn.commit()
            print(f"Sensor '{self.s_SerialNumber}' value updated successfully.")
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    # Function to pull the last sampled time stamp from a value that isn't -1 (out of bounds)
    def get_last_sampled_time(self):
        try:
            select_query = "SELECT serialnum, timestamp, val FROM value WHERE serialnum = %s ORDER BY timestamp DESC"  # query to get sensor data sorted by timestamp in descending order
            cursor.execute(select_query, (self.s_SerialNumber,))
            sensor_data = cursor.fetchall()  # fetch all data
            if sensor_data:  # if sensor exists
                most_recent_entry = None
                for serial_number, timestamp, value in sensor_data:  # loop through each entry in the sorted values
                    if value is not None:
                        most_recent_entry = {"serial_number": self.s_SerialNumber, "timestamp": str(timestamp), "value": value}
                        break
                if most_recent_entry:  # if a most recent entry is found (i.e., has data)
                    most_recent_value = most_recent_entry["value"]  # pull the most recent value
                    if most_recent_value == -1:  # if the most recent value is out of bounds... (i.e., -1)
                        previous_sampled_time = None  # variable to hold the previously sampled time                
                        for serial_number, timestamp, value in sensor_data:  # loop through each entry in the sorted values
                            if value != -1:
                                previous_sampled_time = timestamp
                                break
                        if previous_sampled_time:  # if there exists a previously sampled time
                            expected_time = datetime.strptime(str(previous_sampled_time), "%Y-%m-%d %H:%M:%S") + timedelta(seconds=self.i_SamplingRate)  # get the expected time for the last sample
                            if most_recent_entry["timestamp"] <= str(expected_time):  # if the most recent entry is less than the expected sample time
                                print(f"Error: '{self.s_SerialNumber}' is out of bounds.")  # notify
                                print(f"Last Sampled Time: {previous_sampled_time}")  # get the last sampled time
                                # Update the error flag in the sensor table
                                update_query = "UPDATE sensor SET errorflag = 1 WHERE serialnum = %s"
                                cursor.execute(update_query, (self.s_SerialNumber,))
                                conn.commit()
                        else:  # no previously sampled time
                            print(f"'{self.s_SerialNumber}' is out of bounds, and no previous entry with a different value was found.")
                    elif most_recent_value is None:
                        raise ValueError(f"ValueError: Sensor '{self.s_SerialNumber}' does not exist or has a value of None.")
                    else:  # no most recent value
                        last_sampled_time = most_recent_entry["timestamp"]
                        print(f"Last Sampled Time: {last_sampled_time}")
                else:  # no most recent entry
                    raise ValueError(f"ValueError: No valid data found for '{self.s_SerialNumber}' in value.")
            else:  # no sensor exists
                raise ValueError(f"ValueError: No data found for '{self.s_SerialNumber}' in value.")

        except mysql.connector.Error as e:
            print(f"Error grabbing value data: {e}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    # Function to get the current errorflag of the sensor
    def get_errorflag(self):
        print(self.i_ErrorFlag)
        return self.i_ErrorFlag
    
    # Function to set the errorflag of the sensor system in the s_SensorPath reference point
    def set_errorflag(self, i_NewState):
        try:
            self.i_ErrorFlag = i_NewState
            update_query = "UPDATE sensor SET errorflag = %s WHERE serialnumber = %s"
            cursor.execute(update_query, (i_NewState, self.s_SerialNumber))
            conn.commit()
            print(f"Sensor '{self.s_SerialNumber}' errorflag changed to {i_NewState}")
        except mysql.connector.Error as err:
            print(f"MySQL error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    # Function to get the current status of the sensor
    def get_status(self):
        print(self.s_Status)
        return self.s_Status
    
    # Function to set the status of the sensor system in the s_SensorPath reference point
    def set_status(self, i_NewStatus):
        try:
            self.s_Status = i_NewStatus
            update_query = "UPDATE sensor SET status = %s WHERE serialnumber = %s"
            cursor.execute(update_query, (i_NewStatus, self.s_SerialNumber))
            conn.commit()
            print(f"Sensor '{self.s_SerialNumber}' status changed to {i_NewStatus}")
        except mysql.connector.Error as err:
            print(f"MySQL error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    # Function to get the sampling rate of the sensor
    def get_sampling_rate(self):
        print(self.i_SamplingRate)
        return self.i_SamplingRate
    
    # Function that sets the sensor's sampling rate
    def set_sampling_rate(self, i_NewSamplingRate):
        try:
            self.i_SamplingRate = i_NewSamplingRate
            update_query = "UPDATE sensor SET samplingrate = %s WHERE serialnumber = %s"
            cursor.execute(update_query, (i_NewSamplingRate, self.s_SerialNumber))
            conn.commit()
            print(f"Sensor {self.s_SerialNumber} sampling rate changed to {i_NewSamplingRate}")
        except mysql.connector.Error as err:
            print(f"MySQL error: {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

################### FUNCTIONS ###################

# Function to create sensor objects and push default information
def createSensor(s_SensorType, s_Location, i_SamplingRate):
    sensor = Sensor(s_SensorType, s_Location, i_SamplingRate)  # Create a new sensor
    return sensor  # Return the newly created sensor

# Function to return Sensor Object from database and allows use of sensor functionality
def getSensor(s_SerialNumber):
    try:
        select_query = "SELECT id, serialnumber, samplingrate, type, location, errorflag, status FROM sensor WHERE serialnumber = %s"
        cursor.execute(select_query, (s_SerialNumber,))
        sensor_data = cursor.fetchone()
        if sensor_data:
            sensor = Sensor(
                s_SensorType=sensor_data[3],
                s_Location=sensor_data[4],
                i_SamplingRate=sensor_data[2],
                s_SerialNumber=s_SerialNumber
            )
            return sensor
        else:
            print(f"Sensor with serial number '{s_SerialNumber}' not found in the database.")
            return None
    except mysql.connector.Error as e:
        print(f"Error getting sensor data: {e}")

# Function to delete the sensor by s_SerialNumber from the DB.
def deleteSensor(s_SerialNumber):
    try:
        select_query = "SELECT * FROM sensor WHERE serialnumber = %s"
        cursor.execute(select_query, (s_SerialNumber,))
        sensor_data = cursor.fetchone()
        
        if sensor_data:
            delete_query = "DELETE FROM sensor WHERE serialnumber = %s"
            cursor.execute(delete_query, (s_SerialNumber,))
            conn.commit()
            print(f"Sensor with serial number '{s_SerialNumber}' was deleted successfully.")
        else:
            print(f"Sensor with serial number '{s_SerialNumber}' not found in the database, delete query was not executed.")
            
    except mysql.connector.Error as e:
        print(f"Error deleting record: {e}")

def getCurrentHistoricalData(s_SerialNumber=None):
    try: 
        if s_SerialNumber is None:
            select_query = "SELECT serialnum, val, timestamp FROM value ORDER BY serialnum"
            cursor.execute(select_query)
            sensor_data = cursor.fetchall()
            if sensor_data: 
                data = []
                for row in sensor_data:
                    serial_number, value, timestamp = row
                    record = {"serialnum": serial_number, "value": value, "timestamp": str(timestamp)}
                    data.append(record)
                    print(record)
                return data
            else:
                print(f"Sensor data does not exist")
        else: # serial number not none
            select_query = "SELECT serialnum, timestamp, val  FROM value WHERE serialnum = %s"
            cursor.execute(select_query, (s_SerialNumber,))
            sensor_data = cursor.fetchall()
            if sensor_data: 
                data = []
                for row in sensor_data:
                    serial_number, timestamp, value = row
                    record = {"serialnum": serial_number, "value": value, "timestamp": str(timestamp)}
                    data.append(record)
                    print(record)
                return data
            else:
                print(f"Sensor with serial number '{s_SerialNumber}' does not have historical data")
    except mysql.connector.Error as e:
        print(f"Error grabbing historical data: {e}")
        return None
    
############### END: FUNCTIONS ###################

def main():

    #sensor = createSensor(s_SensorType="Water", s_Location="LakeHuron", i_SamplingRate=1)
    sensor = getSensor(s_SerialNumber="Water_LakeHuron_S0003")
    #deleteSensor(s_SerialNumber="Water_LakeHuron_S0006")
    #getCurrentHistoricalData(s_SerialNumber=None)

    #sensor.set_sampling_rate(10)
    #sensor.get_sampling_rate()
    
    #sensor.set_value("2023-11-08 14:10:13", -1)
    #sensor.get_value("2023-11-08 14:10:12")

    #sensor.set_status("off")
    #sensor.get_status()
    
    #sensor.set_errorflag(0)
    #sensor.get_errorflag()
    
    sensor.get_last_sampled_time()
    
if __name__ == "__main__":
    main()
