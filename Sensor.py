import pandas as pd
import numpy as np
import time
import unittest
import os
import datetime
import json
from json import loads, dumps
import firebase_admin
from firebase_admin.exceptions import FirebaseError
from firebase_admin import credentials
from firebase_admin import db

# CONFIG
with open('config.json') as config_file:
    config = json.load(config_file)

s_ServiceAccountKeyPath = config["s_ServiceAccountKeyPath"]
s_DatabaseURL = config["s_DatabaseURL"]
s_SensorPath = config["s_SensorPath"]
s_SerialNumber = config["s_SerialNumber"]

cred = credentials.Certificate(s_ServiceAccountKeyPath)
firebase_admin.initialize_app(cred, {'databaseURL': s_DatabaseURL})

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

class Sensor:
    i_NumObjects = 0 # number of existing sensors

    def __init__(self, s_SensorType, s_Location, i_SamplingRate, s_SerialNumber=None):
        self.s_SensorType = s_SensorType
        self.s_Location = s_Location
        if s_SerialNumber is None:
          self.s_SerialNumber = self.generate_serial_number()
        else:
          self.s_SerialNumber = s_SerialNumber
        self.f_Value = [-1,-1]
        self.i_SamplingRate = i_SamplingRate
        self.b_isOnline = False
        self.b_isOutOfBounds = False
        self.lst_States = [self.b_isOnline, self.b_isOutOfBounds] # should only be 2 values in order of isOnline? and isOutOfBounds?
    
    def generate_serial_number(self):
        Sensor.i_NumObjects += 1 # Increment the last number of objects
        return f"{self.s_SensorType}_{self.s_Location}_{Sensor.i_NumObjects:04d}" # formatted as: Water/Energy_Location_0000
  
    def get_serial_number(self):
        return self.s_SerialNumber
    
    def get_value(self, t0=""):
        try:
            s_DataPath = f"/{self.s_SensorType.lower()}data"
            data_ref = db.reference(s_DataPath)
            ref = db.reference("/simulation")
            data = ref.get()
            if t0 == '':
                for key in data:
                    if data[key]['id'] == self.s_SerialNumber:
                        sn = data[key]['id']
                        t = data[key]['timestamp']
                        val = data[key]['value']
            else:
                for key in data:
                    if data[key]['id'] == self.s_SerialNumber:
                        if data[key]['timestamp'] == t0:
                            sn = data[key]['id']
                            t = data[key]['timestamp']
                            val = data[key]['value']
            if self.s_SensorType == 'Energy':
                if val is None or (val < 0 or val > 50):
                    self.set_state(s_SensorPath, 1)
                    raise_energy_sensor_value_error(val)
            if self.s_SensorType == 'Water':
                if val is None or (val < 2 or val > 4):
                    self.set_state(s_SensorPath, 1)
                    raise_water_sensor_value_error(val)
            self.f_Value = [t, val]
            self.set_state(s_SensorPath, 0)
            data_row = {
                "timestamp": t,
                "id": sn,
                "value": val
            }
            data_ref.push().set(data_row)
            return(self.f_Value)
        except FirebaseError as e:
            print(f"Firebase Error: {e}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def set_value(self, new_data, timestamp): # for scientist corrections
        try:
            s_DataPath = f"/{self.s_SensorType.lower()}data"
            data_ref = db.reference(s_DataPath)
            data = data_ref.get()
            if self.s_SensorType == 'Energy' and (new_data < 0 or new_data > 50):
                raise_energy_sensor_value_error(new_data)
            elif self.s_SensorType == 'Water' and (new_data < 2 or new_data >  4):
                raise_water_sensor_value_error(new_data)
            if data_ref:
                for key in data:
                    if data[key]['id'] == self.s_SerialNumber:
                        if data[key]['timestamp'] == timestamp:
                            data_ref.child(key).update({'value': new_data})
        except FirebaseError as e:
            print(f"Firebase Error: {e}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def get_last_sampled_time(self): # depends on get_value()
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
  
    def get_current_historical_data(self):
        try:
            s_DataPath = f"/{(self.s_SensorType).lower()}data"
            data_ref = db.reference(s_DataPath)
            sensor_ref = db.reference(s_SensorPath)

            query_result = data_ref.order_by_child("id").equal_to(self.s_SerialNumber).get()
            if query_result:
                i = 0
                for item_key in query_result:
                    i = i + 1
                    print(f"{i}: {query_result[item_key]}")

            if not query_result:
                print(f"Sensor with serial number '{self.s_SerialNumber}' does not have data.") # Error Case: serial number doesn't exist.
        except FirebaseError as e:
            print(f"Firebase Error: {e}") # Error Case: issue with Firebase connection.
        except Exception as e:
            print(f"An error occurred: {str(e)}") # Error Case: not all sensors were deleted successfully, type error, etc.
  
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

if __name__ == "__main__":
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
    for i in range(0,3):
        ref = db.reference("/simulation")
        data = ref.get()
        num = 0
        for sensor in lst_Sensors2[0:3]:
            j = 0
            for key in data:
                if j == (i*5)+num:
                    t = data[key]['timestamp']
                    sensor.get_value(t)
                    sensor.get_last_sampled_time()
                j += 1
            num += 1
    sensor.set_value(3, t)
    print(sensor.get_current_historical_data())

    print("------------------------------")
    sensor = lst_Sensors2[0] # pulling one sensor for testing
    print("----------TEST CASES----------")
    print(f"sensor.get_state()\t{sensor.get_state()}")
    print(f"sensor.set_state()\t{sensor.set_state(s_SensorPath, 0)}")
    print(f"sensor.get_state()\t{sensor.get_state()}")
    print("------------------------------")
    print(f"sensor.get_sampling_rate()\t{sensor.get_sampling_rate()}")
    print(f"sensor.set_sampling_rate()\t{sensor.set_sampling_rate(i_newSamplingRate=3)}") # set new sampling rate to 3 seconds
    print(f"sensor.get_sampling_rate()\t{sensor.get_sampling_rate()}")
    print("------------------------------")