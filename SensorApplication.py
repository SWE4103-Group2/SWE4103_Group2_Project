
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

s_ConfigFilePath = '/Users/briannaorr/Documents/Github/SWE4103_Group2_Project/config.json'

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

#technician's schedule 
schedule = 'Technician_Schedule_Form.xlsx'
# Sensor Object Class
class Sensor:

    i_NumObjects = {} # number of existing sensors

    def __init__(self, s_SensorType, s_Location, i_SamplingRate, s_SerialNumber=None):
        self.s_SensorType = s_SensorType
        self.s_Location = s_Location
        self.i_SamplingRate = i_SamplingRate
        self.i_ErrorFlag = 0
        self.s_Status = "ON"
        if s_SerialNumber is None:
            self.s_SerialNumber = self.generate_serial_number()
        else:
            self.s_SerialNumber = s_SerialNumber
            

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
            return True
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return False

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
            schedule_technician()
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
            return True
        else:
            print(f"Sensor with serial number '{s_SerialNumber}' not found in the database, delete query was not executed.")
            return False
        
    except mysql.connector.Error as e:
        print(f"Error deleting record: {e}")
        return False

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
                    #print(record)
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
                    #print(record)
                return data
            else:
                print(f"Sensor with serial number '{s_SerialNumber}' does not have historical data")
    except mysql.connector.Error as e:
        print(f"Error grabbing historical data: {e}")
        return None
    
#Function to return all sensors and its info if a serial number is not specified 
def get_sensors(s_SerialNumber=None):
    sensors_info = {}
    try:
        cursor.execute("SELECT  serialnumber, type, location, errorflag, status, samplingrate  FROM sensor ORDER BY id DESC")
        sensors = cursor.fetchall()

        if sensors:
            for sensor in sensors: 
                sensor_info = {}
                serialnumber = sensor[0]
                sensor_info['serial_number'] = sensor[0]
                sensor_info['type'] = sensor[1]
                sensor_info['location'] = sensor[2]
                sensor_info['errorflag'] = sensor[3]
                sensor_info['status'] = sensor[4]
                sensor_info['samplingrate'] = sensor[5]
                sensor_info['historical_data'] = getCurrentHistoricalData(serialnumber)
                sensors_info[serialnumber ] = sensor_info
            
            if s_SerialNumber is None:
                #print(sensors_info)
                return sensors_info
            else:
                print(sensor_info)
                return sensor_info
        else:
            print("There are no sensors within the database.")
            return None
    except mysql.connector.Error as e:
        print(f"Error grabbing sensor data: {e}")
        return None

#Function to return a sensor's data
def get_sensor(s_SerialNumber):
    sensors = get_sensors()
    if s_SerialNumber in sensors:
        print(get_sensors(s_SerialNumber))
        return get_sensors(s_SerialNumber)
    else: 
        print("None")
        return None

#Function to get the sum of energy sensor values at a specfic timestamp or for historical data
def total_energy_consumption(s_Timestamp=None):
    if s_Timestamp: 
        #returns total energy consumption at the timestamp specified
        try:
            select_query = "SELECT serialnum, val FROM value WHERE timestamp = %s"
            cursor.execute(select_query, (s_Timestamp,))
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalEnergyConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    sensor = getSensor(serialNum)
                    if sensor.get_type() == 'Energy':
                        val = sensor.get_value(s_Timestamp)[1]
                        #print("val:", val)
                        totalEnergyConsumption = totalEnergyConsumption + val
                print("Total Energy Consumption: ", totalEnergyConsumption )
                return  totalEnergyConsumption
            else:
                print(f"Timestamp'{s_Timestamp}' does not have sensor values associated with it.")
                return None
        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")
    else: 
        #returns total energy consumption for historical data
        try:
            select_query = "SELECT serialnum, val, timestamp FROM value"
            cursor.execute(select_query)
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalEnergyConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    timestamp = sensor_data[i][2]
                    sensor = getSensor(serialNum)
                    if sensor.get_type() == 'Energy':
                        val = sensor.get_value(timestamp)[1]
                        #print("val:", val)
                        totalEnergyConsumption = totalEnergyConsumption + val
                print("Total Energy Consumption: ", totalEnergyConsumption )
                return  totalEnergyConsumption
            else:
                print(f"There's no historical data.")
                return None
        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")

#Function to get the sum of energy sensor values at a specfic timestamp or for historical data
def total_water_consumption(s_Timestamp=None):
    if s_Timestamp: 
        #returns total water consumption at the timestamp specified
        try:
            select_query = "SELECT serialnum, val FROM value WHERE timestamp = %s"
            cursor.execute(select_query, (s_Timestamp,))
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalWaterConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    sensor = getSensor(serialNum)
                    if sensor.get_type() == 'Water':
                        val = sensor.get_value(s_Timestamp)[1]
                        #print("val:", val)
                        totalWaterConsumption = totalWaterConsumption + val
                print("Total Water Consumption: ", totalWaterConsumption )
                return  totalWaterConsumption
            else:
                print(f"Timestamp'{s_Timestamp}' does not have values associated with it.")
                return None
        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")
    else: 
        #returns total water consumption for historical data
        try:
            select_query = "SELECT serialnum, val, timestamp FROM value"
            cursor.execute(select_query)
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalWaterConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    timestamp = sensor_data[i][2]
                    sensor = getSensor(serialNum)
                    if sensor.get_type() == 'Water':
                        val = sensor.get_value(timestamp)[1]
                        #print("val:", val)
                        totalWaterConsumption = totalWaterConsumption + val
                print("Total Water Consumption: ", totalWaterConsumption )
                return  totalWaterConsumption
            else:
                print(f"There's no historical data.")
                return None
        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")

def total_offline(): 
    try:
        select_query = "SELECT serialnumber, status FROM sensor"
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()
        if sensor_data:
            num_offline = 0
            for i in range (len(sensor_data)):
                serialNum = sensor_data[i][0]
                status = sensor_data[i][1]
                #status = getSensor(serialNum).get_status()
                if status == 'OFF': 
                    num_offline = num_offline + 1
            print("Total Offline : ", num_offline)
            return  num_offline
        else:
            print(f"There are no sensors. ")
            return None
    except mysql.connector.Error as e:
        print(f"Error getting sensor data: {e}")
    

def total_out_of_bounds():
    try:
        select_query = "SELECT serialnumber, errorflag FROM sensor"
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()
        if sensor_data:
            num_out_of_bounds = 0
            for i in range (len(sensor_data)):
                serialNum = sensor_data[i][0]
                error_flag = sensor_data[i][1]
                #issue with set_errorFlag
                #error_flag = getSensor(serialNum).get_errorflag()
                print(error_flag)
                if error_flag == 1: 
                    num_out_of_bounds = num_out_of_bounds +  1
            print("Total Out of bounds : ", num_out_of_bounds)
            return  num_out_of_bounds
        else:
            print(f"There are no sensors.")
            return None
    except mysql.connector.Error as e:
        print(f"Error getting sensor data: {e}")

#Function to return the serial number of sensors that are out of bounds 
def get_Out_Of_Bounds_Sensors():
    try:
        select_query = "SELECT serialnumber, errorflag FROM sensor"
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()
        if sensor_data:
            sensors = []
            for i in range (len(sensor_data)):
                serialNum = sensor_data[i][0]
                error_flag = sensor_data[i][1]
                if error_flag == 1: 
                    sensors.append(serialNum)
            print("Sensors : ", sensors)
            return  sensors
        else:
            print( f"There are no sensors.")
            return None
    except mysql.connector.Error as e:
        print(f"Error getting sensor data: {e}")

#Function to update or insert the availability of a technician
def update_schedule_in_database(excel_file, technician_id):
    #boolean to determine if the schedule is being updated or inserted, 0 - updates schedule , 1 - inserts schedule
    update_insert = 0
    
    select_query = "SELECT * FROM schedule WHERE technicianID = %s"
    cursor.execute(select_query, (technician_id,))
    schedule_data = cursor.fetchall() 
    print(schedule_data)

    if len(schedule_data) == 0:
        update_insert = 1

    #convert schedule to json object 
    df = pd.read_excel(excel_file)
    data = df.to_json(orient='records')
    schedule_data = json.loads(data)
   
    for record in schedule_data:
        hour = record["Hour"]
        mon = record["Monday"]
        tues = record["Tuesday"]
        wed = record["Wednesday"]
        thurs = record["Thursday"]
        fri = record["Friday"]
        #print(hour, mon, tues, wed, thurs, fri)
        try:
            if update_insert == 0: 
                update_query = "UPDATE schedule SET availabilityMonday = %s, availabilityTuesday = %s, availabilityWednesday = %s, availabilityThursday = %s, availabilityFriday = %s WHERE technicianID = %s AND timeInHours = %s"
                cursor.execute(update_query, (mon,tues,wed,thurs,fri,technician_id, hour,))
                conn.commit
            else:
                insert_query = "INSERT INTO schedule (technicianID, timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (technician_id, hour, mon, tues, wed, thurs, fri,))
                conn.commit()

        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")


############### END: FUNCTIONS ###################

def main():

    #sensor = createSensor(s_SensorType="Water", s_Location="LakeHuron", i_SamplingRate=1)
    #sensor = getSensor(s_SerialNumber="Water_LakeHuron_S0003")
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
    
    #sensor.get_last_sampled_time()
    #get_sensors('Water_LakeHuron_S0003')
    
    #total_energy_consumption()
    #total_energy_consumption('2023-11-15 16:47:47')
    #total_water_consumption()
    #total_water_consumption("2023-11-08 14:07:33")
    #total_offline()
    #total_out_of_bounds()
    #get_Out_Of_Bounds_Sensors()
    #retrieve_earliest_opentime()
    #schedule_technician()
    update_schedule_in_database(schedule, 1)

    '''
    technician_ids = []
    select_query = "SELECT id FROM user WHERE userType = %s"
    cursor.execute(select_query, ("Technician",))
    user_data = cursor.fetchall() 
    for i in len(user_data): #check if schedule is already in the database 
        technician_ids.append(user_data[i][0])
    '''
    
    
if __name__ == "__main__":
    main()
