
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
# pip install mysql-connector-python
import mysql.connector
# for testing
import unittest
############### END: BASIC IMPORTS ##################

s_ConfigFilePath = '/Users/briannaorr/Documents/Github/SWE4103_Group2_Project/config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

s_ServiceAccountKeyPath   = config["s_ServiceAccountKeyPath"]
s_DatabaseURL             = config["s_DatabaseURL"]
s_SensorPath              = config["s_SensorPath"]
s_SerialNumber            = config["s_SerialNumber"]
i_SamplingRate            = config["i_SamplingRate"]
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
  
  # TO-DO:
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
 
        cursor.execute(insert_query, (next_id, self.s_SensorType, self.s_Location, i_SamplingRate, next_serial_number))
        conn.commit()  # commit the changes to the database
        return next_serial_number
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
  # Function that returns the sensor type
  def get_type(self):
    return self.s_SensorType
  
  # Function to return the value of the sensor at a given timestamp
  def get_value(self, s_Timestamp, s_SensorPath):
    try:
        s_DataPath = f"/{self.s_SensorType.lower()}data" # data table path based on type of sensor
        data_ref = db.reference(s_DataPath) # access data table
        time_query = data_ref.order_by_child('timestamp').equal_to(s_Timestamp).get() # query by timestamps
        timestamp = ''  # default variables
        value = None # default variables

        if time_query: # if the timestamp exists
            for key in time_query: # loop through simulation table
                serial_number = time_query[key]['id'] # save the serial number
                timestamp = time_query[key]['timestamp'] # save the timestamp
                value = time_query[key]['value'] # save value

            if self.s_SensorType == 'Energy': # if the sensor is Energy type
                if (value < 0 or value > 50) or (value == -1): # if the value is out of bounds
                    self.set_state(s_SensorPath, 1) # flag
                    raise_energy_sensor_value_error(value) # raise error
                                      
                if self.s_SensorType == 'Water':
                    if (value < 2 or value > 4) or (value == -1): # if the value is out of bounds
                        self.set_state(s_SensorPath, 1) # flag
                        raise_water_sensor_value_error(value) # raise error

            self.set_state(s_SensorPath, 0) 
            data_row = {"timestamp": timestamp, "id": serial_number,"value": value}
            data_ref.push().set(data_row)
            print(f"Value at '{timestamp}' is: {value}")
            return timestamp, value
        else: # no sensor exists or no data
            print(f"No data found for '{self.s_SerialNumber}' with timestamp: {s_Timestamp}")        
    except FirebaseError as e:
        print(f"Firebase Error: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

  def get_last_sampled_time(self):
    try:
        select_query = "SELECT timestamp FROM value WHERE serialnum = %s"
        cursor.execute(select_query, (self.s_SerialNumber,))
        sensor_data = cursor.fetchall()
        if sensor_data: # if sensor was sampled
            data_values = list(sensor_data) # get the timestamps for sampling of sensor
            data_values.sort(reverse=True) # sort timestamps from the bottom (most recent timestamp/value)
            
            most_recent_entry = None # variable to to hold most recent entry
            for entry in data_values: # loop through each entry in the sorted values to find the first value that is valid (i.e. not NoneType)
                if entry is not None:
                    most_recent_entry = entry
                    break

            if most_recent_entry: # if a most recent entry is found (i.e. has data)
                print(most_recent_entry)
                select_query_val = "SELECT  val  FROM value WHERE timestamp = %s"

                
                most_recent_value = cursor.execute(select_query_val, (datetime.datetime.strptime(str(most_recent_entry[0]), "%Y-%m-%d %H:%M:%S"),)) # 
                #most_recent_value = most_recent_value .fetchone()[0]
                print("most_recent_value", most_recent_value)
                print(datetime.datetime.strptime(str(most_recent_entry[0]), "%Y-%m-%d %H:%M:%S"))
                if most_recent_value != None:
                    most_recent_value.fetchone()[0]
                    if most_recent_value == -1: # if the most recent value is out of bounds... (i.e. -1)
                        previous_sampled_time = None # variable to hold the previously sampled time
                        for entry in data_values: # loop through each entry in the sorted values to find the first value that is valid (i.e. not -1)
                            if entry is not None:
                                if cursor.execute(select_query_val, (datetime.datetime.strptime(str(entry[0]), "%Y-%m-%d %H:%M:%S"),)).fetchone()[0] != -1:
                                    select_query_val = "SELECT val FROM value WHERE timestamp  = %s"
                                    previous_sampled_time = entry
                                    break
                    if previous_sampled_time: # if there exists a previously sampled time
                        expected_time = datetime.datetime.strptime(previous_sampled_time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=self.i_SamplingRate) # get the expected time for the last sample
                        if (most_recent_entry <= (expected_time.strftime("%Y-%m-%d %H:%M:%S"),)): # if the most recent entry is less than the expected sample time
                            print(f"Error: '{self.s_SerialNumber}' is out of bounds.") # notify
                            print(f"Last Sampled Time: {previous_sampled_time}") # get the last sampled time
                            select_query_sensorid = "SELECT sensorid FROM value WHERE serialnum = %s"
                            sensorid = cursor.execute(select_query_sensorid, (self.s_SerialNumber,))
                            if sensorid is not None: 
                                sensorid.fetchone()[0]
                                #update_query = "UPDATE sensor SET errorflag = %s  WHERE id = %s "
                                #cursor.execute(update_query, (1,sensorid)).fetchone()[0]
                            
                    else: # no previously sampled time
                        print(f"'{self.s_SerialNumber}' is out of bounds, and no previous entry with a different value was found.")
                elif most_recent_value is None:
                    raise ValueError(f"ValueError: Sensor '{self.s_SerialNumber}' does not exist or has a value of None.")
                else: # no most recent value
                  last_sampled_time = most_recent_entry
                  print(f"Last Sampled Time: {last_sampled_time}")
            else: # no most recent entry
                raise ValueError(f"ValueError: No valid data found for '{self.s_SerialNumber}'.")
        else: # no sensor exists
            raise ValueError(f"ValueError: No data found for '{self.s_SerialNumber}'.")
    except mysql.connector.Error as e:
        print(f"Database Connector Error: {e}")
    except Exception as e:
        print(f"Error occured getting last time sampled: {e}")
    
  # Function to set the value of the sensor at a specific timestamp in the historical data database
  def set_value(self, s_Timestamp, f_NewValue): # for scientist corrections
    try:
        ref = db.reference(f'/{self.s_SensorType.lower()}data') # reference to sensor table in the database
        data_query = ref.order_by_child('timestamp').equal_to(s_Timestamp).get() # query by timestamp
        if data_query:
            key = list(data_query.keys())[0] # Assuming there's only one entry with the specified timestamp
            entry = data_query[key]
            value = entry['value']
            entry['value'] = f_NewValue
            print(f"Sensor {self.s_SerialNumber} value {value} changed to {f_NewValue}")
            ref.child(key).update(entry) # update entry
        else: # no sensor or data
            print(f"No data found with timestamp: {s_Timestamp}")
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

  # Function to pull the last sampled time stamp from a value that isn't -1 (out of bounds)
  # TO-DO develop functionality to account for all out of bound cases other than incorrect ones
  
  # Function to get the current state of the sensor
  def get_state(self, s_Sensorpath):
    try:
        flagged_ref = db.reference(f'{s_SensorPath}') # reference to sensor table in database
        flagged_sensor_data_query = flagged_ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # query by serial number in sensor table
        for key in flagged_sensor_data_query:
          entry = flagged_sensor_data_query[key]['errorflag'] # get entry for sensor in sensor table
          print(f"State of '{self.s_SerialNumber}': {entry}")
          return entry
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.
  
  # Function to set the state of the sensor system in the s_SensorPath reference point
  def set_state(self, s_SensorPath, i_State):
    try:
        flagged_ref = db.reference(f'{s_SensorPath}') # reference to sensor table in database
        flagged_sensor_data_query = flagged_ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # query by serial number in sensor table
        for key in flagged_sensor_data_query:
          entry = flagged_sensor_data_query[key] # get entry for sensor in sensor table
          if i_State == 1: # want to flag sensor?
            entry['errorflag'] = 1 # flag it!
            print(f"Sensor {self.s_SerialNumber} state changed. {self.s_SerialNumber} is out of bounds.")
          elif i_State == 0: # want to resolve sensor?
            entry['errorflag'] = 0 # remove flag!
            print(f"Sensor {self.s_SerialNumber} state changed. {self.s_SerialNumber} is within bounds.")
          else:
            return print(f"Error: Incorrect State Type, must be 1 or 0")
          flagged_ref.child(key).update(entry) # update entry
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

  # Function to get the sampling rate of the sensor
  def get_sampling_rate(self):
    return self.i_SamplingRate
  
  # Function that sets the sensor's sampling rate
  def set_sampling_rate(self, i_NewSamplingRate, s_SensorPath):
    try:
        ref = db.reference(f'{s_SensorPath}') # reference to sensor table in database
        data_query = ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # query by serial number in sensor table
        for key in data_query:
          entry = data_query[key] # get entry for sensor in sensor table
          entry['samplingRate'] = i_NewSamplingRate
          ref.child(key).update(entry) # update entry
          print(f"Sensor {self.s_SerialNumber} sampling rate changed to {i_NewSamplingRate}")
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

############# ERROR FUNCTIONS ###################

class WaterSensorValueError(Exception):
    min_wv = 2
    max_wv = 4

    def __init__(self, f,  *args):
        super().__init__(args)
        self.f = f

    def __str__(self):
        return f'{self.f} is not in the valid range {self.min_wv, self.max_wv}'

def raise_water_sensor_value_error(val):
    raise WaterSensorValueError(val)

class EnergySensorValueError(Exception):
    min_ev = 0
    max_ev = 50
    
    def __init__(self, f,  *args):
        super().__init__(args)
        self.f = f

    def __str__(self):
        return f'{self.f} is not in the valid range {self.min_ev, self.max_ev}'

def raise_energy_sensor_value_error(val):
    raise EnergySensorValueError(val)

class CustomErrorMessage(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def energy_sensor_error_msg():
    error_message = "Energy sensor value is out of bounds."
    raise CustomErrorMessage(error_message)

def water_sensor_error_msg():
    error_message = "Water sensor value is out of bounds."
    raise CustomErrorMessage(error_message)

def negative_error_msg():
    error_message = "Sensor value can not be a negative."
    raise CustomErrorMessage(error_message)

############# END: ERROR FUNCTIONS ##############

################### FUNCTIONS ###################

# Function to create sensor objects and push default information
def createSensor(s_SensorType, s_Location, i_SamplingRate):
    sensor = Sensor(s_SensorType, s_Location, i_SamplingRate) # create a new sensor 
    serial_number = sensor.generate_serial_number() # generate serial number
    insert_query = "INSERT INTO sensor (serialnumber, samplingrate, type, location, errorflag, status) VALUES (%s, %s, %s, %s, 0, 'ON')"
    values = (serial_number, sensor.get_sampling_rate(), sensor.get_type(), s_Location)
    cursor.execute(insert_query, values)
    conn.commit()
    return sensor # return new sensor

# Function to return Sensor Object from database and allows use of sensor functionality
def getSensor(s_SerialNumber):
    # Define your MySQL SELECT query to retrieve sensor data by serial number
    select_query = "SELECT id, serialnumber, samplingrate, type, location, errorflag, status FROM sensor WHERE serialnumber = %s"
    cursor.execute(select_query, (s_SerialNumber,))
    sensor_data = cursor.fetchone()

    if sensor_data:
        sensor = Sensor(s_SensorType=sensor_data[3], s_Location=sensor_data[4], i_SamplingRate=sensor_data[2], s_SerialNumber=s_SerialNumber)
        return sensor
    else:
        print(f"Sensor with serial number '{s_SerialNumber}' not found in the database.")
        return None

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
            print(f"Sensor with serial number '{s_SerialNumber}' was deleted.")
        else:
            print(f"Sensor with serial number '{s_SerialNumber}' not found in the database, delete query was not executed.")
            
    except mysql.connector.Error as e:
        print(f"Error deleting record: {e}")
    
# Function that returns historical data for the sensor specified or all the historical data in the value table
def get_current_historical_data(s_SerialNumber = None):
    if s_SerialNumber == None:
        try: 
            select_query = "SELECT timestamp, val  FROM value"
            cursor.execute(select_query)
            table_data = cursor.fetchall()
            if table_data: 
                data = []
                for row in table_data:
                    timestamp, value = row
                    record = {"value": value, "timestamp": str(timestamp)}
                    data.append(record)
                print(data)
                print("Number of records: ", len(data))
                return data
            else:
                print(f"There is no historical data at this time.")
        except mysql.connector.Error as e:
            print(f"Error grabbing historical data: {e}")
            return None
    else: 
        try: 
            select_query = "SELECT timestamp, val  FROM value WHERE serialnum = %s"
            cursor.execute(select_query, (s_SerialNumber,))
            sensor_data = cursor.fetchall()
            if sensor_data: 
                data = []
                for row in sensor_data:
                    timestamp, value = row
                    record = {"value": value, "timestamp": str(timestamp)}
                    data.append(record)
                print(data)
                print("Number of records: ", len(data))
                return data
            else:
                print(f"Sensor with serial number '{s_SerialNumber}' does not have historical data")
        except mysql.connector.Error as e:
            print(f"Error grabbing historical data: {e}")
            return None


    
  

############### END: FUNCTIONS ###################

def main():
   
    sensor = getSensor(s_SerialNumber)
    #createSensor('Water', 'River', 1)
    #deleteSensor(s_SerialNumber)
    #get_current_historical_data(s_SerialNumber)
    sensor.get_last_sampled_time()
    
if __name__ == "__main__":
    main()
