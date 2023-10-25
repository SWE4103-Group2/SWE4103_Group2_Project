import pandas as pd
import numpy as np
import time
import random
from random import randint
import unittest
import os
import datetime
from json import loads, dumps
import firebase_admin
from firebase_admin import db


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
  
  #replaced with db
  #df_HistoricalData = pd.DataFrame() # 2D array holding historical data OR get_historical_data()

  cred_obj = firebase_admin.credentials.Certificate('/Users/briannaorr/Documents/GitHub/SWE4103_Group2_Project/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json')
  default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://swe4103-db-default-rtdb.firebaseio.com/"
    })
  
  def __init__(self, s_SensorType, s_Location, i_SamplingRate):
        self.s_SensorType = s_SensorType
        self.s_Location = s_Location
        self.f_SerialNumber = self.generate_serial_number()
        self.f_Value = [-1,-1]
        self.i_SamplingRate = i_SamplingRate
        self.b_isOnline = False
        self.b_isOutOfBounds = False
        self.lst_States = [self.b_isOnline, self.b_isOutOfBounds] # should only be 2 values in order of isOnline? and isOutOfBounds?
        self.energySensorsRef = db.reference("/energydata")
        self.waterSensorsRef = db.reference("/waterdata")
  
  def generate_serial_number(self):
    Sensor.i_NumObjects += 1 # Increment the last number of objects
    return f"{self.s_SensorType}_{self.s_Location}_{Sensor.i_NumObjects:04d}" # formatted as: Water/Energy_Location_0000
  def get_serial_number(self):
    return self.f_SerialNumber
  def get_value(self, t0=""):
    file_path = "C:/Users/olivi/Desktop/Fall_2023/SWE4103/Project/S" + self.f_SerialNumber[-4:] + ".csv" # read file at this location (simulated data)
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
  
  '''
  def set_value(self, new_data, row, col): # for scientist corrections
    if self.s_SensorType == 'Energy' and (new_data < 0 or new_data > 50):
        raise_energy_sensor_value_error(new_data)
    if self.s_SensorType == 'Water' and (new_data < 2 or new_data > 4):
        raise_water_sensor_value_error(new_data)
    Sensor.df_HistoricalData.at[row, col] = float(new_data)
    return Sensor.df_HistoricalData.at[row, col]
  '''
  def set_value(self, new_data, timestamp): # for scientist corrections
    
    if self.s_SensorType == 'Energy' and (new_data >= 0 or new_data <=  50):
      data = self.energySensorsRef.get()
      if data: 
         for key in data: 
            if data[key][timestamp] == timestamp:
              data['value'] = new_data
              self.energySensorsRef.child(key).set(data)
    elif self.s_SensorType == 'Energy' and (new_data < 0 or new_data > 50):
      raise_energy_sensor_value_error(new_data)
    elif self.s_SensorType == 'Water' and (new_data >= 2 or new_data <=  4):
      data = self.waterSensorsRef.get()
      if data: 
         for key in data: 
            if data[key][timestamp] == timestamp:
              data['value'] = new_data
              self.waterSensorsRef.child(key).set(data)
    else:
      raise_water_sensor_value_error(new_data)
         
  
  def get_last_sampled_time(self): # depends on get_value()
    return Sensor.df_HistoricalData.loc[Sensor.df_HistoricalData.index[-1], 't']
  def get_current_historical_data(self):
    return Sensor.df_HistoricalData
  def set_historical_data(self, val):
    if len(Sensor.df_HistoricalData) > 0 and val[0] in Sensor.df_HistoricalData['t'].values:
      Sensor.df_HistoricalData.loc[Sensor.df_HistoricalData['t'] == val[0], 'S'+self.f_SerialNumber[-4:]] = val[1]
    else:
      df = pd.DataFrame({'t':[val[0]], ('S'+self.f_SerialNumber[-4:]):[val[1]]})
      Sensor.df_HistoricalData = pd.concat([Sensor.df_HistoricalData, df], ignore_index=True)
    return Sensor.df_HistoricalData # output to verify
  def get_state(self):
    return self.lst_States # returns current states for online/offline and out/in-bounds
  def set_state(self, lst_States, b_isOnline=None, b_isOutOfBounds=None):
    if len(lst_States) != 2: # if more/less than 2 arguments given: throw error
      return f"ARGUMENT ERROR: Expected 2 Arguments, Received {len(lst_States)}"
    else: # proceed
      for state in lst_States: # checking arguments
        if not isinstance(state, bool): # check that type is boolean
          return f"TYPE ERROR: Expected Boolean for Current State Types, Received {type(state)}"
    if b_isOnline is not None:
      if not isinstance(b_isOnline, bool):
          return f"TYPE ERROR: Expected Boolean for b_isOnline, Received {type(b_isOnline)}"
      else:
          self.lst_States[0] = b_isOnline
    if b_isOutOfBounds is not None:
        if not isinstance(b_isOutOfBounds, bool):
            return f"TYPE ERROR: Expected Boolean for b_isOutOfBounds, Received {type(b_isOutOfBounds)}"
        else:
            self.lst_States[1] = b_isOutOfBounds
    return self.lst_States
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
    for i in range(0,15):
      file_path = "C:/Users/olivi/Desktop/Fall_2023/SWE4103/Project/S0001.csv"
      with open(file_path, "r") as file:
        t, sn, d, val = file.readlines()[i].split(',')
        t = t.split()[1]
      for sensor in lst_Sensors2:
        sensor.get_value(t)
        sensor.get_last_sampled_time()
    sensor.set_value(3, 0, 'S'+sensor.f_SerialNumber[-4:])

    #print(Sensor.df_HistoricalData)
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
    