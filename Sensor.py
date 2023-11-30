
#####################################################
'''
   (Sensor.py)   OGR

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
# pip install firebase
import firebase_admin
from firebase_admin.exceptions import FirebaseError
from firebase_admin import credentials
from firebase_admin import db
# for testing
import unittest
############### END: BASIC IMPORTS ##################

s_ConfigFilePath = "config.json"

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
cred = credentials.Certificate(s_ServiceAccountKeyPath)
firebase_admin.initialize_app(cred, {'databaseURL': s_DatabaseURL})

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
  
  # Function to generate a unique serial number with the format: SensorType_Location_S000X
  def generate_serial_number(self):
    ref = db.reference(s_SensorPath)
    existing_sensors = ref.get()
    last_numbers = [int(key[-4:]) for key in existing_sensors if key.startswith(f"{self.s_SensorType}_{self.s_Location}_S")]
    if last_numbers:
        max_last_number = max(last_numbers)
    else:
        max_last_number = 0
    next_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{max_last_number + 1:04d}"
    return next_serial_number
  
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
  def get_last_sampled_time(self, s_SensorPath):
    try:
        print("Sensor Serial Number:", self.s_SerialNumber)
        s_DataPath = f"/{self.s_SensorType.lower()}data" # go to correct table in database based on sensor type
        data_ref = db.reference(s_DataPath) # set reference
        sensor_data_query = data_ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # query by the serial number

        if sensor_data_query: # if sensor exists
            data_values = list(sensor_data_query.values()) # get the values for that serial number
            data_values.sort(key=lambda x: x['timestamp'], reverse=True) # sort timestamps from the bottom (most recent timestamp/value)
            
            most_recent_entry = None # variable to to hold most recent entry
            for entry in data_values: # loop through each entry in the sorted values to find the first value that is valid (i.e. not NoneType)
                if entry.get("value") is not None:
                    most_recent_entry = entry
                    break

            if most_recent_entry: # if a most recent entry is found (i.e. has data)
                most_recent_value = most_recent_entry.get("value") # pull most recent value
                if most_recent_value == -1: # if the most recent value is out of bounds... (i.e. -1)
                    previous_sampled_time = None # variable to hold the previously sampled time
                    for entry in data_values: # loop through each entry in the sorted values to find the first value that is valid (i.e. not -1)
                        if entry.get("value") != -1:
                            previous_sampled_time = entry.get("timestamp")
                            break

                    if previous_sampled_time: # if there exists a previously sampled time
                        expected_time = datetime.datetime.strptime(previous_sampled_time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=self.i_SamplingRate) # get the expected time for the last sample
                        if ((most_recent_entry.get("timestamp")) <= (expected_time.strftime("%Y-%m-%d %H:%M:%S"))): # if the most recent entry is less than the expected sample time
                            print(f"Error: '{self.s_SerialNumber}' is out of bounds.") # notify
                            print(f"Last Sampled Time: {previous_sampled_time}") # get the last sampled time
                            flagged_ref = db.reference(f'/{s_SensorPath}') # reference the sensor table in the database
                            flagged_sensor_data_query = flagged_ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # get the sensor
                            for key in flagged_sensor_data_query: # loop through sensors in sensor table
                                entry = flagged_sensor_data_query[key] # grab the correct sensor
                                entry['errorflag'] = 1 # flag it
                                flagged_ref.child(key).update(entry) # update sensor
                    else: # no previously sampled time
                        print(f"'{self.s_SerialNumber}' is out of bounds, and no previous entry with a different value was found.")
                elif most_recent_value is None:
                    raise ValueError(f"ValueError: Sensor '{self.s_SerialNumber}' does not exist or has a value of None.")
                else: # no most recent value
                  last_sampled_time = most_recent_entry.get("timestamp")
                  print(f"Last Sampled Time: {last_sampled_time}")
            else: # no most recent entry
                raise ValueError(f"ValueError: No valid data found for '{self.s_SerialNumber}' in {s_DataPath}.")
        else: # no sensor exists
            raise ValueError(f"ValueError: No data found for '{self.s_SerialNumber}' in {s_DataPath}.")
    except FirebaseError as e:
        print(f"Firebase Error: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
  
  # Function that returns all current historical data for sensor
  def get_current_historical_data(self, s_SensorPath):
    try:
        s_DataPath = f"/{(self.s_SensorType).lower()}data"
        data_ref = db.reference(s_DataPath) # access data table
        sensor_ref = db.reference(s_SensorPath) # access sensor table

        query_result = data_ref.order_by_child("id").equal_to(self.s_SerialNumber).get() # query by serial number in data table
        if query_result: # if serial number exists
            i = 0 # for counting purposes adds an index beginning at 1
            for item_key in query_result: # return entries
                i = i + 1
                print(f"{i}: {query_result[item_key]}") 

        if not query_result: # no exisiting entries for sensor
            print(f"Sensor with serial number '{self.s_SerialNumber}' does not have data.") # Error Case: serial number doesn't exist.
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

  #def set_historical_data(self, val):
    #if len(Sensor.df_HistoricalData) > 0 and val[0] in Sensor.df_HistoricalData['t'].values:
    #  Sensor.df_HistoricalData.loc[Sensor.df_HistoricalData['t'] == val[0], 'S'+self.s_SerialNumber[-4:]] = val[1]
    #else:
    #  df = pd.DataFrame({'t':[val[0]], ('S'+self.s_SerialNumber[-4:]):[val[1]]})
    #  Sensor.df_HistoricalData = pd.concat([Sensor.df_HistoricalData, df], ignore_index=True)
    #return Sensor.df_HistoricalData # output to verify
  
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
  def get_sampling_rate(self, s_SensorPath):
    try:
        sensor_ref = db.reference(s_SensorPath) # reference to sensor table in database
        data_query = sensor_ref.order_by_child('id').equal_to(self.s_SerialNumber).get() # query by serial number in sensor table
        print(data_query)
        for key in data_query:
          entry = data_query[key]['samplingRate'] # get entry for sensor in sensor table
          print(f"Sampling rate of '{self.s_SerialNumber}': {entry} sec/sample")
          return entry
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.
  
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
    ref = db.reference(s_SensorPath) # access sensor table
    ref.child(serial_number).set({
        'errorflag': 0, # assume no issues upon instantiation
        'id': serial_number,
        'type': sensor.get_type(),
        'samplingRate': i_SamplingRate
    }) # set default values
    return sensor # return new sensor

# Function to return Sensor Object from database and allows use of sensor functionality
def getSensor(s_SerialNumber, s_SensorPath):
    ref = db.reference(s_SensorPath) # access sensor table
    serial_number_parts = s_SerialNumber.split("_")
    s_Location = serial_number_parts[1] # get location from serial number
    sensor_data = ref.order_by_child('id').equal_to(s_SerialNumber).get() # query by the serial number
    if sensor_data: # if sensor exists
        sensor_key = list(sensor_data.keys())[0] # gets key for sensor
        x = sensor_data[sensor_key] # variable to hold sensor data
        print("Sensor data:", x) # pulls sensor by key
        sensor = Sensor(x['type'], s_Location, x['samplingRate'], s_SerialNumber)  # Use the sensor data directly 
        return sensor # object that can be manipulated
    else: # sensor doesn't exist
        print(f"Sensor '{s_SerialNumber}' not found.")

# Function to delete the sensor by s_SerialNumber from the DB.
def deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_SensorPath, s_SerialNumber):
    try:
        serial_number_parts = s_SerialNumber.split("_")
        s_DataPath = f"/{(serial_number_parts[0]).lower()}data" # establish table path
        data_ref = db.reference(s_DataPath)
        sensor_ref = db.reference(s_SensorPath) # access sensor table

        query_result = data_ref.order_by_child("id").equal_to(s_SerialNumber).get() # query by serial number in data table
        if query_result: # if sensor exists
            for item_key in query_result.keys():
                data_ref.child(item_key).delete() # delete all entries from data table
            print(f"Sensors with serial number '{s_SerialNumber}' deleted from '{s_DataPath}' successfully.")

        query_result_sensor = sensor_ref.order_by_child("id").equal_to(s_SerialNumber).get() # query by serial number in sensor table
        if query_result_sensor:
            for item_key_sensor in query_result_sensor.keys():
                sensor_ref.child(item_key_sensor).delete() # delete entry from sensor table
            print(f"Sensors with serial number '{s_SerialNumber}' deleted from 'sensors' successfully.")
        
        if not query_result and not query_result_sensor: # no sensor or entries
            print(f"Sensor with serial number '{s_SerialNumber}' does not exist.") # Error Case: serial number doesn't exist.
    except FirebaseError as e: # firebase issue
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

############### END: FUNCTIONS ###################

def main():
    serial_number_parts = s_SerialNumber.split("_")
    #sensor = createSensor(serial_number_parts[0], serial_number_parts[1], i_SamplingRate)
    #sensor = getSensor(s_SerialNumber, s_SensorPath)
    sensor = getSensor("Water_Field_2_S0001", s_SensorPath)

    #deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_SensorPath, "Water_Field_2_S0002")

    #sensor.get_current_historical_data(s_SensorPath)
    #sensor.get_last_sampled_time(s_SensorPath) # testing function
    #sensor.set_state(s_SensorPath, 0) # testing function
    #sensor.get_state(s_SensorPath)
    #sensor.get_sampling_rate(s_SensorPath)
    #sensor.set_value("2023-10-26 12:56:11", 3.333)
    #sensor.get_value("2023-10-26 01:30:31", s_SensorPath)
    #sensor.get_type(s_SensorPath)

    
if __name__ == "__main__":
    main()
