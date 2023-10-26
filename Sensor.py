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
  cred_obj = firebase_admin.credentials.Certificate('/Users/briannaorr/Documents/GitHub/SWE4103_Group2_Project/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json')
  default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://swe4103-db-default-rtdb.firebaseio.com/"
    })
  energySensorsRef = db.reference("/energydata")
  waterSensorsRef = db.reference("/waterdata")

  def __init__(self, s_SensorType, s_Location, i_SamplingRate):
    self.s_SensorType = s_SensorType
    self.s_Location = s_Location
    self.s_SerialNumber = self.generate_serial_number()
    self.f_Value = [-1,-1]
    self.i_SamplingRate = i_SamplingRate
    self.b_isOnline = False
    self.b_isOutOfBounds = False
    self.lst_States = [self.b_isOnline, self.b_isOutOfBounds] # should only be 2 values in order of isOnline? and isOutOfBounds?
  
  def generate_serial_number(self):
    ref = db.reference("/sensors")
    existing_sensors = ref.get()
    last_numbers = [int(key[-4:]) for key in existing_sensors if key.startswith(f"{self.s_SensorType}_{self.s_Location}_S")]
    if last_numbers:
        max_last_number = max(last_numbers)
    else:
        max_last_number = 0
    next_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{max_last_number + 1:04d}"
    return next_serial_number
  
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
          EnergySensorValueError.raise_energy_sensor_value_error(val)
      if self.s_SensorType == 'Water' and (val < 2 or val > 4):
          WaterSensorValueError.raise_water_sensor_value_error(val)
      self.f_Value = [t, val]
      self.set_historical_data([t, val]) # setting historical data
      return(self.f_Value)
    return "FILE READ ERROR: CANNOT OPEN FILE AT THIS PATH."
  
  def set_value(self, new_data, timestamp): # for scientist corrections
    if self.s_SensorType == 'Energy' and (new_data >= 0 or new_data <=  50):
      data = Sensor.energySensorsRef.get()
      if data: 
         for key in data:
            if data[key]['id'] == self.s_SerialNumber and data[key]['timestamp'] == timestamp:
              data[key]['value'] = new_data
              Sensor.energySensorsRef.child(key).set(data)
    elif self.s_SensorType == 'Energy' and (new_data < 0 or new_data > 50):
      EnergySensorValueError.raise_energy_sensor_value_error(new_data)
    elif self.s_SensorType == 'Water' and (new_data >= 2 or new_data <=  4):
      data = Sensor.waterSensorsRef.get()
      if data: 
         for key in data:
            print(data[key]['id']) 
            if data[key]['id'] == self.s_SerialNumber and data[key]['timestamp'] == timestamp:
              print(data[key]['value'])
              data[key]['value'] = new_data
              Sensor.waterSensorsRef.child(key).set(data)
    else:
      WaterSensorValueError.raise_water_sensor_value_error(new_data)
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
  def get_type(self):
     return self.s_SensorType
  def change_serial_number(self):
    i_LastNum = int(self.s_SerialNumber[-4:])
    if i_LastNum > 1:
      new_last_number = i_LastNum - 1
      new_serial_number = f"{self.s_SensorType}_{self.s_Location}_S{new_last_number:04d}"
      self.s_SerialNumber = new_serial_number
    else:
      print("Error: Couldn't adjust serial number.")
def createSensor(s_SensorType, s_Location, i_SamplingRate):
  sensor = Sensor(s_SensorType, s_Location, i_SamplingRate)
  serial_number = sensor.generate_serial_number()
  ref = db.reference('/sensors')
  ref.child(serial_number).set({
    'errorflag': 0, # assume no issues upon instantiation
    'id': serial_number,
    'type': sensor.get_type(),
    'samplingRate': i_SamplingRate
  })
  print("Ran create statement.")
  return sensor
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

def main():
  #sensor = createSensor("Water", 'LakeHuron','5')
  sensor = getSensor("Water_LakeHuron_S0001", "/sensors"); 
  sensor.set_value(3.0, '2023-10-26 00:11:02')

  

if __name__ == "__main__":
   main()
