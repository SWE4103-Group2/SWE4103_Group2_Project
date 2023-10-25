import pandas as pd
import numpy as np
import time
import datetime
import random
from random import randint
import os
import json
from json import loads, dumps

# pip install firebase
import firebase_admin
from firebase_admin.exceptions import FirebaseError
from firebase_admin import credentials
from firebase_admin import db

# for testing
import unittest

# CONFIG
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

s_ServiceAccountKeyPath = config["s_ServiceAccountKeyPath"]
s_DatabaseURL = config["s_DatabaseURL"]
s_SensorPath = config["s_SensorPath"]
s_SerialNumber = config["s_SerialNumber"]
#

cred = credentials.Certificate(s_ServiceAccountKeyPath)
firebase_admin.initialize_app(cred, {'databaseURL': s_DatabaseURL})

# Error Messages
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
#

# Sensor Object Class
class Sensor:

  i_NumObjects = {} # number of existing sensors
  #df_HistoricalData = pd.DataFrame() # 2D array holding historical data OR get_historical_data()

  def __init__(self, s_SensorType, s_Location, i_SamplingRate):
        self.s_SensorType = s_SensorType
        self.s_Location = s_Location
        self.s_SerialNumber = self.generate_serial_number()
        self.f_Value = [-1,-1]
        self.i_SamplingRate = i_SamplingRate
  
  # Function to generate a unique serial number with the format: SensorType_Location_S000X
  def generate_serial_number(self):
    # Query Firebase for existing sensors at your specified reference point
    ref = db.reference("/sensors")
    existing_sensors = ref.get()

    # Extract the last 4 digits of the serial numbers and find the maximum
    last_numbers = [int(key[-4:]) for key in existing_sensors if key.startswith(f"{self.s_SensorType}_{self.s_Location}_S")]
    if last_numbers:
        max_last_number = max(last_numbers)
    else:
        max_last_number = 0

    # Generate the next unique serial number
    next_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{max_last_number + 1:04d}"

    return next_serial_number
  
  def change_serial_number(self):
      i_LastNum = int(self.s_SerialNumber[-4:])
      if i_LastNum > 1:
          new_last_number = i_LastNum - 1
          new_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{new_last_number:04d}"
          self.s_SerialNumber = new_serial_number
      else:
          print("Error: Couldn't adjust serial number.")

  def get_type(self):
     return self.s_SensorType

  def get_value(self, t0=""):
    file_path = "C:/Users/olivi/Desktop/Fall_2023/SWE4103/Project/S" + self.s_SerialNumber[-4:] + ".csv" # read file at this location (simulated data)
    with open(file_path, "r") as file:
      if t0 == '':
        t, sn, d, val = file.readlines()[-1].split(',')
      else:
        for line in file.readlines():
          if line.split(',')[0].split()[1] == t0:
            t, sn, d, val = line.split(',')
      t = t.split()[1]
      if val.strip() == 'None':
        val = 0
        self.set_state(self.lst_States,False,False)
      else:
        val = float(val.strip())
      if self.s_SensorType == 'Energy' and (val < 0 or val > 50):
          raise_energy_sensor_value_error(val)
      if self.s_SensorType == 'Water' and (val < 2 or val > 4):
          raise_water_sensor_value_error(val)
      self.f_Value = [t, val]
      self.set_historical_data([t, val]) # setting historical data
      return(self.f_Value)
    return "FILE READ ERROR: CANNOT OPEN FILE AT THIS PATH."
  
  def set_value(self, new_data, row, col): # for scientist corrections
    if self.s_SensorType == 'Energy' and (new_data < 0 or new_data > 50):
        raise_energy_sensor_value_error(new_data)
    if self.s_SensorType == 'Water' and (new_data < 2 or new_data > 4):
        raise_water_sensor_value_error(new_data)
    Sensor.df_HistoricalData.at[row, col] = float(new_data)
    return Sensor.df_HistoricalData.at[row, col]
  
  def get_last_sampled_time(self, s_SensorPath):
    try:
        s_DataPath = f"/{self.s_SensorType.lower()}data"
        data_ref = db.reference(s_DataPath)
        sensor_data_query = data_ref.order_by_child('id').equal_to(self.s_SerialNumber).get()

        if sensor_data_query:
            data_values = list(sensor_data_query.values())
            data_values.sort(key=lambda x: x['timestamp'], reverse=True)

            most_recent_entry = None
            for entry in data_values:
                if entry.get("value") is not None:
                    most_recent_entry = entry
                    break

            if most_recent_entry:
                most_recent_value = most_recent_entry.get("value")
                if most_recent_value == -1:
                    previous_sampled_time = None
                    for entry in data_values:
                        if entry.get("value") != -1:
                            previous_sampled_time = entry.get("timestamp")
                            break

                    if previous_sampled_time:
                        expected_time = datetime.datetime.strptime(previous_sampled_time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=self.i_SamplingRate)
                        if most_recent_entry.get("timestamp") <= expected_time.strftime("%Y-%m-%d %H:%M:%S"):
                            print(f"Error: '{self.s_SerialNumber}' is out of bounds.")
                            print(f"Last Sampled Time: {previous_sampled_time}")
                            flagged_ref = db.reference(f'/{s_SensorPath}')
                            flagged_sensor_data_query = flagged_ref.order_by_child('id').equal_to(self.s_SerialNumber).get()
                            for key in flagged_sensor_data_query:
                                entry = flagged_sensor_data_query[key]
                                entry['errorflag'] = 1
                                flagged_ref.child(key).update(entry)
                    else:
                        print(f"'{self.s_SerialNumber}' is out of bounds, and no previous entry with a different value was found.")
                elif most_recent_value is None:
                    raise ValueError(f"ValueError: Sensor '{self.s_SerialNumber}' does not exist or has a value of None.")
                else:
                  last_sampled_time = most_recent_entry.get("timestamp")
                  print(f"Last Sampled Time: {last_sampled_time}")
            else:
                raise ValueError(f"ValueError: No valid data found for '{self.s_SerialNumber}' in {s_DataPath}.")
        else:
            raise ValueError(f"ValueError: No data found for '{self.s_SerialNumber}' in {s_DataPath}.")
    except FirebaseError as e:
        print(f"Firebase Error: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


  def get_current_historical_data(self):
    return Sensor.df_HistoricalData
  
  def set_historical_data(self, val):
    if len(Sensor.df_HistoricalData) > 0 and val[0] in Sensor.df_HistoricalData['t'].values:
      Sensor.df_HistoricalData.loc[Sensor.df_HistoricalData['t'] == val[0], 'S'+self.s_SerialNumber[-4:]] = val[1]
    else:
      df = pd.DataFrame({'t':[val[0]], ('S'+self.s_SerialNumber[-4:]):[val[1]]})
      Sensor.df_HistoricalData = pd.concat([Sensor.df_HistoricalData, df], ignore_index=True)
    return Sensor.df_HistoricalData # output to verify
  
  def get_state(self):
    return self.lst_States # returns current states for online/offline and out/in-bounds
  
  def set_state(self, s_SensorPath, i_State):
    flagged_ref = db.reference(f'/{s_SensorPath}')
    flagged_sensor_data_query = flagged_ref.order_by_child('id').equal_to(self.s_SerialNumber).get()
    for key in flagged_sensor_data_query:
      entry = flagged_sensor_data_query[key]
      if i_State == 1:
        entry['errorflag'] = 1
        print(f"Sensor {self.s_SerialNumber} state changed. {self.s_SerialNumber} is out of bounds.")
      elif i_State == 0:
        entry['errorflag'] = 0
        print(f"Sensor {self.s_SerialNumber} state changed. {self.s_SerialNumber} is within bounds.")
      else:
        return print(f"Error: Incorrect State Type, must be 1 or 0")
      flagged_ref.child(key).update(entry)
  
  def get_sampling_rate(self):
    return self.i_SamplingRate
  
  def set_sampling_rate(self, i_newSamplingRate):
    self.i_SamplingRate = i_newSamplingRate
    return self.i_SamplingRate # output to verify
    i_NumSensors = 5 # Create an unspecfied number of sensors (could be in config file)
    lst_Sensors = []
    for i in range(i_NumSensors):
        s_SensorType = "Water"  # Replace with the type of sensor
        s_Location = "Field_1"  # Replace with the location
        i_SamplingRate = 15 # Water samples once every 15 seconds
        sensor = Sensor(s_SensorType, s_Location, i_SamplingRate)
        lst_Sensors.append(sensor)

    lst_Sensors2 = []
    Sensor.i_NumObjects = 0

    for i in range(i_NumSensors):
        s_SensorType2 = "Energy"  # Replace with the type of sensor
        s_Location2 = "Field_2"  # Replace with the location
        i_SamplingRate = 1 # Energy samples once every 1 second
        sensor2 = Sensor(s_SensorType2, s_Location2, i_SamplingRate)
        lst_Sensors2.append(sensor2)

    print("----------TEST CASES----------")
    for i in range(0,15):
      file_path = "C:/Users/olivi/Desktop/Fall_2023/SWE4103/Project/S0001.csv"
      with open(file_path, "r") as file:
        t, sn, d, val = file.readlines()[i].split(',')
        t = t.split()[1]
      for sensor in lst_Sensors2:
        sensor.get_value(t)
        sensor.get_last_sampled_time()
    sensor.set_value(3, 0, 'S'+sensor.s_SerialNumber[-4:])
    print(Sensor.df_HistoricalData)
    print("------------------------------")

    sensor = lst_Sensors2[0] # pulling one sensor for testing

    print("----------TEST CASES----------")
    print(f"sensor.get_state()\t{sensor.get_state()}")
    print(f"sensor.set_state()\t{sensor.set_state(sensor.lst_States, b_isOnline=True, b_isOutOfBounds=True)}")
    print(f"sensor.get_state()\t{sensor.get_state()}")
    print("------------------------------")
    print(f"sensor.get_sampling_rate()\t{sensor.get_sampling_rate()}")
    print(f"sensor.set_sampling_rate()\t{sensor.set_sampling_rate(i_newSamplingRate=3)}") # set new sampling rate to 3 seconds
    print(f"sensor.get_sampling_rate()\t{sensor.get_sampling_rate()}")
    print("------------------------------")

# Function to create sensor objects and push default information
def createSensor(s_SensorType, s_Location, i_SamplingRate):
    sensor = Sensor(s_SensorType, s_Location, i_SamplingRate)
    serial_number = sensor.generate_serial_number()
    ref = db.reference(s_SensorPath)
    ref.child(serial_number).set({
        'errorflag': 0, # assume no issues upon instantiation
        'id': serial_number,
        'type': sensor.get_type(),
        'samplingRate': i_SamplingRate
    })
    return sensor

# Function to return Sensor Object from database and allows use of sensor functionality
def getSensor(s_SerialNumber, s_SensorPath):
    serial_number_parts = s_SerialNumber.split("_")
    s_Location = serial_number_parts[1]
    ref = db.reference(s_SensorPath)
    sensor_data = ref.order_by_child('id').equal_to(s_SerialNumber).get()

    if sensor_data:
        sensor_key = list(sensor_data.keys())[0]
        print("Sensor data:", sensor_data[sensor_key])
        x = sensor_data[sensor_key]
        sensor = Sensor(x['type'], s_Location, x['samplingRate'])
        sensor.change_serial_number()
        return sensor
    else:
        print("Sensor not found.")

# Function to delete the sensor by s_SerialNumber from the DB.
def deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_SensorPath, s_SerialNumber):
    try:
        serial_number_parts = s_SerialNumber.split("_")
        s_DataPath = F"/{(serial_number_parts[0]).lower()}data"
        data_ref = db.reference(s_DataPath)
        sensor_ref = db.reference(s_SensorPath)

        query_result = data_ref.order_by_child("id").equal_to(s_SerialNumber).get()
        if query_result:
            for item_key in query_result.keys():
                data_ref.child(item_key).delete()
            print(f"Sensors with serial number '{s_SerialNumber}' deleted from '{s_DataPath}' successfully.")

        query_result_sensor = sensor_ref.order_by_child("id").equal_to(s_SerialNumber).get()
        if query_result_sensor:
            for item_key_sensor in query_result_sensor.keys():
                sensor_ref.child(item_key_sensor).delete()
            print(f"Sensors with serial number '{s_SerialNumber}' deleted from 'sensors' successfully.")
        
        if not query_result and not query_result_sensor:
            print(f"Sensor with serial number '{s_SerialNumber}' does not exist.") # Error Case: serial number doesn't exist.
    except FirebaseError as e:
        print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
    except Exception as e:
        print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.

def main():
    #sensor = createSensor("Water", "HydroElectricDam", 15)
    sensor = getSensor(s_SerialNumber, s_SensorPath)
    sensor.get_last_sampled_time(s_SensorPath) # testing function
    sensor.set_state(s_SensorPath, 0) # testing function
    #deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_SensorPath, s_SerialNumber)
if __name__ == "__main__":
    main()
