
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
import ast
# for testing
import unittest
############### END: BASIC IMPORTS ##################

s_ConfigFilePath = 'config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

s_User                    = config["User"]
s_Password                = config["Password"]
s_Host                    = config["Host"]
s_DatabasePath            = config["DatabasePath"]
lst_SerialNumbers         = config["lst_SerialNumbers"]
i_SamplingRate            = config["i_SamplingRate"]
s_TimeFormat              = config["s_TimeFormat"]
s_TimeZone                = config["s_TimeZone"]
f_RangeMin                = config["f_RangeMin"]
f_RangeMax                = config["f_RangeMax"]
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
            self.i_SamplingRate = i_SamplingRate
            if s_SerialNumber is None:
                self.s_SerialNumber = self.generate_serial_number()
            else:
                self.s_SerialNumber = s_SerialNumber
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
                        print(f"An unexpected error occurred: unable to set state for '{self.s_SerialNumber}'")

                if self.s_SensorType == 'Water':
                    if (value >= 2 and value <= 4):
                        print(f"Value of '{self.s_SerialNumber}' at '{s_Timestamp}' is: {value} L/hour")
                    else:
                        self.set_errorflag(1)
                        print(f"An unexpected error occurred: unable to set state for '{self.s_SerialNumber}'")
                return serial_number, value
            else:
                print(f"No data found for '{self.s_SerialNumber}' with timestamp: {s_Timestamp}")
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    # Function to set the value of the sensor at a specific timestamp in the historical data database
    def set_value(self, s_NewSensorType=None, s_NewLocation=None, i_NewSamplingRate=None):
        try:
            select_query = "SELECT type, location, samplingrate FROM sensor WHERE serialnumber = %s"
            cursor.execute(select_query, (self.s_SerialNumber, ))
            sensor_data = cursor.fetchone()
            if sensor_data:
                type, location, samplingrate = sensor_data

            if s_NewSensorType is not None:
                if (s_NewSensorType.lower() == "water" or s_NewSensorType.lower() == "energy"):
                    self.s_SensorType = s_NewSensorType
                    update_query = "UPDATE sensor SET type = %s WHERE serialnumber = %s"
                    cursor.execute(update_query, (s_NewSensorType.lower(), self.s_SerialNumber))
                    conn.commit()
                    print(f"Sensor '{self.s_SerialNumber}' type changed to '{s_NewSensorType.lower()}'")
                else:
                    print(f"Error! Incorrect new type recieved, must be 'Water' or 'Energy'")
            if s_NewLocation is not None:
                self.s_Location = s_NewLocation
                update_query = "UPDATE sensor SET location = %s WHERE serialnumber = %s"
                cursor.execute(update_query, (s_NewLocation, self.s_SerialNumber))
                conn.commit()
                print(f"Sensor '{self.s_SerialNumber}' location changed to {s_NewLocation}")
            if i_NewSamplingRate is not None:
                if i_NewSamplingRate >= 1:
                    self.i_SamplingRate = i_NewSamplingRate
                    update_query = "UPDATE sensor SET samplingrate = %s WHERE serialnumber = %s"
                    cursor.execute(update_query, (i_NewSamplingRate, self.s_SerialNumber))
                    conn.commit()
                    print(f"Sensor '{self.s_SerialNumber}' sampling rate changed to {i_NewSamplingRate}")
                else:
                    print(f"Error! Sampling rate must be a positive integer.")
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
                                self.set_errorflag(1)
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
        cursor.execute("SELECT  serialnumber, type, location, errorflag, status, samplingrate FROM sensor ORDER BY id DESC")
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
                sensors_info[serialnumber ] = sensor_info
            return sensors_info
        else:
            print("There are no sensors within the database.")
            return None
    except mysql.connector.Error as e:
        print(f"Error grabbing sensor data: {e}")
        return None

#Function to return a sensor's data
def get_sensor(s_SerialNumber):
    query = "SELECT  serialnumber, type, location, errorflag, status, samplingrate  FROM sensor where serialnumber= %s"
    cursor.execute(query, (s_SerialNumber,))
    sensor = cursor.fetchone()
    if sensor:
        sensors_info = {}
        sensor_info = {}
        serialnumber = sensor[0]
        sensor_info['serial_number'] = sensor[0]
        sensor_info['type'] = sensor[1]
        sensor_info['location'] = sensor[2]
        sensor_info['errorflag'] = sensor[3]
        sensor_info['status'] = sensor[4]
        sensor_info['samplingrate'] = sensor[5]
        sensor_info['historical_data'] = getCurrentHistoricalData(serialnumber)
        sensors_info[serialnumber] = sensor_info
        return {serialnumber: sensor_info}
    else: 
        print("None")
        return None

#Function to get the sum of energy sensor values at a specfic timestamp or for historical data
def total_consumption(s_Timestamp=None):
    if s_Timestamp: 
        #returns total water consumption at the timestamp specified
        try:
            select_query = """
                SELECT v.serialnum, v.val, s.type
                FROM value v
                JOIN sensor s ON v.serialnum = s.serialnumber
                WHERE v.timestamp = ?;
            """
            cursor.execute(select_query, (s_Timestamp,))
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalWaterConsumption = 0
                totalEnergyConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    val = sensor_data[i][1]
                    sensorType = sensor_data[i][2]
                    if sensorType == 'Water':
                        totalWaterConsumption = totalWaterConsumption + val
                    elif sensorType == 'Energy':
                        totalEnergyConsumption = totalEnergyConsumption + val
                print("Total Consumption: ", totalWaterConsumption, totalEnergyConsumption )
                return [totalWaterConsumption, totalEnergyConsumption]
            else:
                print(f"Timestamp'{s_Timestamp}' does not have values associated with it.")
                return None
        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")
    else: 
        #returns total water consumption for historical data
        try:
            select_query = """
                SELECT v.serialnum, v.timestamp, v.val, s.type
                FROM value v
                JOIN sensor s ON v.serialnum = s.serialnumber;
            """
            cursor.execute(select_query)
            sensor_data = cursor.fetchall()
            if sensor_data:
                totalWaterConsumption = 0
                totalEnergyConsumption = 0
                for i in range (len(sensor_data)):
                    serialNum = sensor_data[i][0]
                    timestamp = sensor_data[i][1]
                    val = sensor_data[i][2]
                    sensorType = sensor_data[i][3]
                    if sensorType == 'Water':
                        totalWaterConsumption = totalWaterConsumption + val
                    elif sensorType == 'Energy':
                        totalEnergyConsumption = totalEnergyConsumption + val
                print("Total Consumption: ", totalWaterConsumption, totalEnergyConsumption)
                return [totalWaterConsumption, totalEnergyConsumption]
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
                if error_flag == 1: 
                    num_out_of_bounds = num_out_of_bounds +  1
            print("Total Out of bounds : ", num_out_of_bounds)
            return  num_out_of_bounds
        else:
            print(f"There are no sensors.")
            return None
    except mysql.connector.Error as e:
        print(f"Error getting sensor data: {e}")

def get_out_of_bounds(): 
    try:
        select_query = """
                SELECT v.serialnum, v.timestamp, v.val, s.type, s.status
                FROM value v
                JOIN sensor s ON v.serialnum = s.serialnumber
                WHERE s.errorflag = 1;
            """
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()
        if sensor_data:
            sensors_info = {}
            for row in sensor_data:
                serialnum = row[0]
                timestamp = row[1]
                val = row[2]
                sensortype = row[3]
                if val < 0 or (val > 4 and sensortype == 'Water') or (val > 50 and sensortype == 'Energy'):
                    if serialnum not in sensors_info:
                        sensors_info[serialnum] = {'serial_number': serialnum, 'historical_data': [], 'status': row[4]}
                    sensors_info[serialnum]['historical_data'].append({ 'timestamp': str(timestamp), 'value': val })
            print("Offline Sensors: ", sensors_info)
            return sensors_info
        else:
            print(f"There are no offline sensors. ")
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

    if len(schedule_data) == 0:
        update_insert = 1
    print(update_insert)
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
        sat = record["Saturday"]
        sun = record["Sunday"]
        
        print(hour, mon, tues, wed, thurs, fri)
        try:
            if update_insert == 0:
                select_query_id = "SELECT id FROM schedule WHERE technicianID = %s and timeInHours = %s"
                cursor.execute(select_query_id, (technician_id,hour,))
                user_data = cursor.fetchall()
                id = user_data[0][0] 
                print(id)
                update_query = "UPDATE schedule SET availabilityMonday = %s, availabilityTuesday = %s, availabilityWednesday = %s, availabilityThursday = %s, availabilityFriday = %s, availabilitySaturday = %s, availabilitySunday = %s WHERE id = %s"
                cursor.execute(update_query, (mon,tues,wed,thurs,fri,id,))
                conn.commit
            else:
                insert_query = "INSERT INTO schedule (technicianID, timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday, availabilitySaturday, availabilitySunday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (technician_id, hour, mon, tues, wed, thurs, fri, sat, sun,))
                conn.commit()

        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")


# Function to retrieve user's schedule from the database
def getSchedule():
    try:
        # query everything in a schedule
        select_query = "SELECT timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday, availabilitySaturday, availabilitySunday, technicianID FROM schedule"
        cursor.execute(select_query)
        schedule_data = cursor.fetchall()

        if schedule_data:  # if there is an entry
            lst_Identifiers = [] 
            for row in schedule_data: # save each row of schedule data
                timeInHours, arr_Monday, arr_Tuesday, arr_Wednesday, arr_Thursday, arr_Friday, arr_Saturday, arr_Sunday, technicianID = row
                if technicianID not in lst_Identifiers: # check that the id does not already exist
                    lst_Identifiers.append(technicianID) # save unique ids
            
            lst_df = [] # list of all dataframes (schedules)
            lst_IdentifiersInOrder = []
            for idNum in lst_Identifiers: # for each id get the corresponding schedule
                query = "SELECT timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday, availabilitySaturday, availabilitySunday FROM schedule WHERE technicianID = %s"
            
                cursor.execute(query, (idNum,))
                userInfoData = cursor.fetchall()

                if userInfoData:  # if there is an entry
                    rows = []
                    for i in userInfoData:
                        timeInHours, arr_Monday, arr_Tuesday, arr_Wednesday, arr_Thursday, arr_Friday, arr_Saturday, arr_Sunday = i
                        new_row = {
                            "Hours": timeInHours,
                            "Monday": str(arr_Monday),
                            "Tuesday": str(arr_Tuesday),
                            "Wednesday": str(arr_Wednesday),
                            "Thursday": str(arr_Thursday),
                            "Friday": str(arr_Friday),
                            "Saturday": str(arr_Saturday),
                            "Sunday": str(arr_Sunday)
                        }

                        rows.append(new_row)

                    df = pd.concat([pd.DataFrame(rows)], ignore_index=True)
                    df = df.replace({'Y': 1, 'N': 0})
                    lst_df.append(df) # list of schedule matrices in binary format
                    lst_IdentifiersInOrder.append(idNum)
            return lst_df, lst_IdentifiersInOrder
        else:
            print(f"No data found in schedule table")
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def getEarliestAvailability(arr_OfDataFrames, lst_IdentifiersInOrder):
    try:
        lst_result = []
        lst_DateObjects = []
        for df in arr_OfDataFrames:
            current_time = datetime.now()  # get the current time

            year = current_time.year
            month = current_time.month
            day = current_time.day
            hour = current_time.hour

            current_time = datetime(year, month, day, hour, 0, 0)  # setting time manually to avoid error
    
            current_day = current_time.strftime('%A')

            while True:
                filtered_df = df[df["Hours"] == (f"0 days {(current_time.hour+1) % 24:02d}:00:00")]
                
                if current_time.hour == 0:
                    current_day = (current_time + timedelta(hours=1)).strftime('%A')
                    if current_day == "Saturday" or current_day == "Sunday":
                        # skip to Monday
                        current_time += timedelta(days=(7 - current_time.weekday()))
                        current_day = "Monday"
                        
                # Check if filtered_df is empty
                if not filtered_df.empty:
                    i_AvailabilityForNextHour = filtered_df[current_day].iat[0]
                # print("HERE")
                    if i_AvailabilityForNextHour == 1:
                        available_day = current_day
                        i_AvailableHour = current_time.hour
                        current_time += timedelta(hours=1)  # increment hour after finding an available hour
                        current_day = current_time.strftime('%A')  # update the day
                        break

                current_time += timedelta(hours=1)  # Increment hour

                if current_time.weekday() == 0 and current_time.hour == 0:
                    break # break out of the loop if we've gone through a full week

            # Include date information
            year = current_time.year
            month = current_time.month
            day = current_time.day
            hour = current_time.hour
            dateObject = datetime(year, month, day, hour, 0, 0)
            
            s_DateString = current_time.strftime('%A, %B %d, %Y at %I:%M %p')
            
            lst_DateObjects.append(dateObject)
        
        closest_date, userID = min(zip(lst_DateObjects, lst_IdentifiersInOrder), key=lambda item: abs(item[0] - current_time))
        return closest_date, userID
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def Book(i_UserID, DateObject):
    try:
        month = DateObject.strftime("%B")
        day = DateObject.day
        year = DateObject.year
        week_day = DateObject.strftime("%A")
        hour = DateObject.hour
        update_query = f"UPDATE schedule SET availability{week_day} = %s WHERE timeInHours = %s AND technicianID = %s"
        time = f"{hour}:00:00"
        cursor.execute(update_query, ('N', time, i_UserID))
        conn.commit()

        print(f"Success! Technician with ID '{i_UserID}' is booked for {week_day} {month} {day}, {year} at {time}")
    
    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return (i_UserID, f"{day} {month} {day}, {year} at {time}")

#Function to create tickets, should be called when a sensor's value is out of bounds or off 
def create_ticket(serialNum):
    state = "UNRESOLVED"
    insert_query = "INSERT INTO ticket (State, sensor) VALUES (%s, %s)"
    cursor.execute(insert_query, (state, serialNum,))
    conn.commit()
    print(f"Success! Ticket for sensor : {serialNum} created!")

#Function to update tickets
#States: RESOLVED, UNRESOLVED
def update_ticket(state, ticket_id):
    update_query = "UPDATE ticket SET State = %s WHERE id = %s"
    cursor.execute(update_query, (state,ticket_id,))
    conn.commit()
    print(f"Ticket {ticket_id} was updated to {state}.")

def alert(serialnumber):
    # Check if there are any existing unresolved tickets for the given sensor
    try:
        select_query = "SELECT id FROM ticket WHERE sensor = %s AND state = 'UNRESOLVED'"
        cursor.execute(select_query, (serialnumber,))
        existing_unresolved_tickets = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    if not existing_unresolved_tickets:
        # No unresolved ticket found, create a new one
        create_ticket(serialnumber)
        try:
            select_query = "SELECT id FROM ticket WHERE sensor = %s ORDER BY id DESC LIMIT 1"
            cursor.execute(select_query, (serialnumber,))
            id = cursor.fetchone()[0]
            update_booking(serialnumber, id)
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    else:
        return  # Exit the function
    
#Function to update booking time in db  
def update_booking(serialnumber, id): 
    arr_df, lst_IdentifiersInOrder = getSchedule()
    time_EarliestDate, i_UserID = getEarliestAvailability(arr_df, lst_IdentifiersInOrder)
    i_UserID, s_AvailabilityString = Book(i_UserID=i_UserID, DateObject = time_EarliestDate)
    print(i_UserID)
    update_query = "UPDATE ticket SET BookingTime = %s, technicianID = %s, sensor = %s WHERE id = %s"
    cursor.execute(update_query, ((s_AvailabilityString), i_UserID, serialnumber, id,))
    conn.commit()

check_db = True
def pollingDB():
    count = 0
    while check_db:
        print("Polling Count: ", count)
        try:
            select_query = "SELECT serialnumber, errorflag, status FROM sensor"
            cursor.execute(select_query)
            sensors = cursor.fetchall()
            for sensor in sensors:
                serialnumber, errorflag, status = sensor
                if errorflag == 1 or status == 'OFF':
                    alert(serialnumber)
                    print("Alert")
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        # Sleep for a duration before refreshing data
        time.sleep(10) 
        count = count + 1
    cursor.close()
    conn.close()

def resolveTicket(ticketID):
    try:
        select_query = "SELECT * FROM ticket WHERE id = %s"
        cursor.execute(select_query, (ticketID,))
        tickets = cursor.fetchall()

        for ticket in tickets:
            tid, BookingTime, State, sensor, technicianID = ticket

            if BookingTime is not None:
                parts = BookingTime.split(" ")
                s_DayOfWeek = parts[0]
                s_Date = f"{parts[3]}-{parts[1]}-{parts[2].replace(',', '')} {parts[5]}"
                print(s_Date)
                datetime_object = datetime.strptime(s_Date, '%Y-%B-%d %H:%M:%S')

                if State == "RESOLVED":
                    print(f"Ticket #{tid}: Already resolved.")

                if State == "UNRESOLVED":
                    # errorflag == 0 in sensor table
                    # status == ON in sensor table
                    update_query = "UPDATE sensor SET errorflag = %s, status = %s WHERE serialnumber = %s"
                    cursor.execute(update_query, (0, "ON", sensor))  # reset status and error flag
                    conn.commit()

                    # schedule set to Y in schedule table
                    update_query = f"UPDATE schedule SET availability{s_DayOfWeek} = %s WHERE timeInHours = %s AND technicianID = %s"
                    cursor.execute(update_query, ('Y', datetime_object, technicianID))  # re-open availability
                    conn.commit()

                    # ticket table = "resolved"
                    update_ticket(state="RESOLVED", ticket_id=tid)
            else:
                print(f"Error Creating Date Object from Booking Time.")

    except ValueError as e:
        print(f"Error converting Booking Time to datetime: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

def get_tickets():
    select_query = "SELECT * from ticket"
    cursor.execute(select_query)
    tickets = cursor.fetchall()
    data = []
    for row in tickets:
        ticketId, bookingTime, state, sensor, technicianId = row
        record = {"ticketId": ticketId, "bookingTime": bookingTime, "state": state, "sensor": sensor, "technicianId": technicianId}
        data.append(record)
        
    return data

#function to aggregate sensors by adding values
def aggregatesensors(serial_numbers):
    # initialize the val variable
    value = 0
    
    # Get the sensor data from the database.
    try:
        # parameterized query
        placeholders = ', '.join(['%s' for _ in serial_numbers])
        query = f"SELECT id FROM sensor WHERE serialnumber IN ({placeholders})"
        cursor.execute(query, serial_numbers)
        results = cursor.fetchall()
        
        int_list = [item[0] for item in results]
        
        b = "insert into virtualsensor (sensors) values (%s); "
        cursor.execute(b,(str(int_list),))
        conn.commit()

        # Get the last inserted ID
        cursor.execute("SELECT LAST_INSERT_ID();")
        vsid = cursor.fetchone()[0]

        cursor.execute("SELECT JSON_OBJECT('sensorid', sensorid, 'value', val) FROM value;")
        result = cursor.fetchall()
        
        for row in result:
            json_string = row[0]
            data_dict = json.loads(json_string)
            sensor_id = data_dict.get('sensorid')
            if sensor_id in int_list:
                value += data_dict.get('value')
        print(value)

        stmt = "INSERT INTO virtualvalue (virtualsensorid, val) values (%s, %s);"
        cursor.execute(stmt, (vsid, value,))
        conn.commit()

        return {'vsid': vsid, 'value': value}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def update_aggregate():
    try:
        query = "SELECT id, sensors FROM virtualsensor;"
        cursor.execute(query)
        virtualsensors = cursor.fetchall()
        for sensor in virtualsensors:
            vsid = sensor[0]
            int_list = ast.literal_eval(sensor[1])
        
            cursor.execute("SELECT JSON_OBJECT('sensorid', sensorid, 'value', val) FROM value;")
            result = cursor.fetchall()
            
            value = 0
            for row in result:
                json_string = row[0]
                data_dict = json.loads(json_string)
                sensor_id = data_dict.get('sensorid')
                if sensor_id in int_list:
                    value += data_dict.get('value')
            print(value)

            stmt = "UPDATE virtualvalue SET val = %s where virtualsensorid = %s;"
            cursor.execute(stmt, (vsid, value,))
            conn.commit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_virtual_sensors():
    try:
        query = """
                    SELECT v.val, s.id, s.sensors
                    FROM virtualvalue v
                    JOIN virtualsensor s ON v.virtualsensorid = s.id;
                """
        cursor.execute(query)
        results = cursor.fetchall()
        sensors_info = []
        if results:
            for row in results:
                value = row[0]
                vsid = row[1]
                sensors = row[2]
                sensors_info.append({'vsid': vsid, 'value': value, 'sensors': sensors})
            return sensors_info
        else:
            print("There are no virtual sensors within the database.")
            return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Function to generate simulated sensor data
def generate_sensor_data(sensorType=''):
    # Simulate data or generate an error
    rangeMin = f_RangeMin
    rangeMax = f_RangeMax
    if sensorType == 'Energy':
        rangeMin = 0
        rangeMax = 50
    if randint(0, 100) < 90:  # 99.9% chance of valid data
        return random.uniform(rangeMax, rangeMin) # return a value in a set range (can be made configurable) assumed float
    else:
        return -1 # equivalent to null
    
# Function to update the database
def update_database(s_SerialNumber, i_DataValue):
    now = datetime.now() # get current time
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

def get_latest_data(serial_numbers):
    try:
        placeholders = ', '.join(['%s' for _ in serial_numbers])
        query = f"""
                WITH RankedData AS (
                    SELECT
                        serialnum,
                        timestamp,
                        val,
                        ROW_NUMBER() OVER (PARTITION BY serialnum ORDER BY timestamp DESC) AS RowRank
                    FROM
                        value v
                    WHERE
                        serialnum IN ({placeholders})
                )
                SELECT
                    serialnum,
                    timestamp,
                    val
                FROM
                    RankedData
                WHERE
                    RowRank = 1;
            """
        cursor.execute(query, serial_numbers)
        results = cursor.fetchall()
        data = []
        for row in results:
            data.append({'serialnum': row[0], 'timestamp': str(row[1]), 'value': row[2]})
        return data
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
 
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

    #get_sensor('Water_LakeHuron_S0003')
    #total_consumption()
    #total_offline()
    total_out_of_bounds()
    #aggregatesensors(['Water_LakeHuron_S0005', 'Water_LakeHuron_S0003', 'Water_Pond_S0007']


if __name__ == "__main__":
    main()