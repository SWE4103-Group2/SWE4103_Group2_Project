
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

s_ConfigFilePath = 'config.json'

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
                SELECT v.serialnum, v.val, v.timestamp, s.type
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
                    val = sensor_data[i][1]
                    timestamp = sensor_data[i][2]
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
        
        print(hour, mon, tues, wed, thurs, fri)
        try:
            if update_insert == 0:
                select_query_id = "SELECT id FROM schedule WHERE technicianID = %s and timeInHours = %s"
                cursor.execute(select_query_id, (technician_id,hour,))
                user_data = cursor.fetchall() 
                id = user_data[0][0] 
                print(id)
                update_query = "UPDATE schedule SET availabilityMonday = %s, availabilityTuesday = %s, availabilityWednesday = %s, availabilityThursday = %s, availabilityFriday = %s WHERE id = %s"
                cursor.execute(update_query, (mon,tues,wed,thurs,fri,id,))
                conn.commit
            else:
                insert_query = "INSERT INTO schedule (technicianID, timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (technician_id, hour, mon, tues, wed, thurs, fri,))
                conn.commit()

        except mysql.connector.Error as e:
            print(f"Error getting sensor data: {e}")


# Function to retrieve user's schedule from the database
def getSchedule():
    try:
        select_query = "SELECT timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday, technicianID FROM schedule"

        #cursor.execute(select_query, (i_UserID,))
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()

        if sensor_data:  # if there is an entry
            lst_Identifiers = []
            for row in sensor_data: 
                timeInHours, arr_Monday, arr_Tuesday, arr_Wednesday, arr_Thursday, arr_Friday, technicianID = row
                if technicianID not in lst_Identifiers: # check for ids
                    lst_Identifiers.append(technicianID) # save unique ids
            
            lst_df = [] # list of all dataframes
            lst_IdentifiersInOrder = []
            for idNum in lst_Identifiers: # for each id get their schedule
                query = "SELECT timeInHours, availabilityMonday, availabilityTuesday, availabilityWednesday, availabilityThursday, availabilityFriday FROM schedule WHERE technicianID = %s"
            
                cursor.execute(query, (idNum,))
                userInfoData = cursor.fetchall()

                if userInfoData:  # if there is an entry
                    rows = []
                    for i in userInfoData:
                        timeInHours, arr_Monday, arr_Tuesday, arr_Wednesday, arr_Thursday, arr_Friday = i
                        new_row = {
                            "Hours": timeInHours,
                            "Monday": str(arr_Monday),
                            "Tuesday": str(arr_Tuesday),
                            "Wednesday": str(arr_Wednesday),
                            "Thursday": str(arr_Thursday),
                            "Friday": str(arr_Friday)
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

def find_next_day_of_week(current_day):
    # Define a mapping from day names to corresponding integers
    days_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    # Convert the input day to lowercase and get its corresponding integer value
    current_day = current_day.lower()
    current_day_index = days_mapping.get(current_day)

    if current_day_index is not None:
        # Get the current date and day of the week
        today = datetime.now()
        current_day_of_week = today.weekday()

        # Calculate the number of days until the next occurrence of the input day
        days_until_next = (current_day_index - current_day_of_week + 7) % 7

        # Calculate the next date
        next_date = today + timedelta(days=days_until_next)

        return next_date.year, next_date.strftime('%B'), next_date.day
    else:
        return "Invalid day name"

def getEarliestAvailability(arr_OfDataFrames, lst_IdentifiersInOrder):
    lst_result = []
    for df in arr_OfDataFrames:

        current_time = datetime.now()
        current_day = current_time.weekday()
        day_of_week = current_time.strftime('%A')
        current_hour = current_time.hour
        next_hour = current_hour + 1
        if next_hour == 24:
            next_hour = 0
        
        next_day = None
        next_day_of_week = None
        next_hour = None
        
        if (day_of_week != "Saturday" and day_of_week != "Sunday"):
            filtered_df = df[df['Hours'] == (f"0 days {next_hour}:00:00")]
            hour_and_day = filtered_df[f"{day_of_week}"]
            
            if (hour_and_day.iat[0] == 1):
                next_day = current_day
                next_day_of_week = day_of_week
                next_hour = current_hour + 1 
                next_hour = (f"0 days {next_hour}:00:00")
            else: # keep searching
                tomorrow = current_time + timedelta(days=1)
                day_of_week_tomorrow = tomorrow.strftime('%A')

                if day_of_week_tomorrow == "Saturday":
                    next_day = current_time + timedelta(days=3)
                elif day_of_week_tomorrow == "Sunday":
                    next_day = current_time + timedelta(days=2)
                else:
                    next_day = current_time + timedelta(days=1)

                next_day_of_week = next_day.strftime('%A')
                
                for index, row in df.iterrows():
                    entry = row[next_day_of_week]
                    if entry == 1:
                        next_hour = row['Hours']
                        break
        else: # keep searching
            tomorrow = current_time + timedelta(days=1)
            day_of_week_tomorrow = tomorrow.strftime('%A')

            if day_of_week_tomorrow == "Saturday":
                next_day = current_time + timedelta(days=3)
            elif day_of_week_tomorrow == "Sunday":
                next_day = current_time + timedelta(days=2)
            else:
                next_day = current_time + timedelta(days=1)

            next_day_of_week = next_day.strftime('%A')
            
            for index, row in df.iterrows():
                entry = row[next_day_of_week]
                if entry == 1:
                    next_hour = row['Hours']
                    break
            
        s_Year, s_Month, s_Day = find_next_day_of_week(next_day_of_week)
        s_AvailabilityString = f"{s_Year}-{s_Month}-{s_Day}  {str(next_hour)[7:]}"
        lst_result.append([s_Year, s_Month, s_Day, str(next_hour)[7:]])
        print(f"Next Time: {next_day_of_week} {s_Month} {s_Day}, {s_Year} at {str(next_hour)[7:]}")
    
    lst_DateObjects = []
    for val in lst_result:
        date_object = datetime(val[0], datetime.strptime(val[1], '%B').month, val[2], *map(int, val[3].split(':')))
        lst_DateObjects.append(date_object)
    
    #closest_date = min(lst_DateObjects, key=lambda date_obj: abs(date_obj - current_time))
    closest_date, userID = min(zip(lst_DateObjects, lst_IdentifiersInOrder), key=lambda item: abs(item[0] - current_time))

    #print("Date:", closest_date)
    #print("UserID:", userID)
    return next_day_of_week, s_Month, s_Day, s_Year, str(next_hour)[7:], s_AvailabilityString, closest_date, userID
    
def Book(i_UserID, s_DayOfWeek, s_Hour, s_AvailabilityString):
    try:       
        update_query = f"UPDATE schedule SET availability{s_DayOfWeek} = %s WHERE timeInHours = %s AND technicianID = %s"
        s_Time = timedelta(days=0, hours=int(s_Hour[0:2]), minutes=0)
        print(s_Time)
        cursor.execute(update_query, ('N', s_Time, i_UserID))
        conn.commit()
        print(f"Success! Technician with ID '{i_UserID}' is booked for {s_AvailabilityString}")
    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


#Function to create tickets, should be called when a sensor's value is out of bounds or off 
def create_ticket(serialNum):
    state = "UNRESOLVED"
    insert_query = "INSERT INTO ticket (State, sensor) VALUES (%s, %s)"
    cursor.execute(insert_query, (state, serialNum,))
    conn.commit()


#Function to update tickets
#States: RESOLVED, UNRESOLVED
def update_ticket(state, ticket_id):
    update_query = "UPDATE ticket SET State = %s WHERE id = %s"
    cursor.execute(update_query, (state,ticket_id,))
    conn.commit()


#Function to handle alerting subsystem 
def alert(serialnumber):
    select_query = "SELECT sensor,state FROM ticket"
    cursor.execute(select_query)
    tickets = cursor.fetchall()
    ticket_exists = False
    for ticket in tickets:
        sensor, state = ticket
        if serialnumber == sensor and state == "RESOLVED": #ticket for sensor exists but it was resolved so creating another is required
            create_ticket(serialnumber)
        if serialnumber == sensor and state == "UNRESOLVED": #creating a new ticket is not required
            ticket_exists = True
    if not(ticket_exists):  
        create_ticket(serialnumber)
    
    arr_df, lst_IdentifiersInOrder = getSchedule()
    s_DayOfWeek, s_Month, s_Day, s_Year, s_Hour, s_AvailabilityString, time_EarliestDate, i_UserID = getEarliestAvailability(arr_df, lst_IdentifiersInOrder)
    Book(i_UserID=i_UserID, s_DayOfWeek=s_DayOfWeek, s_Hour=s_Hour, s_AvailabilityString=s_AvailabilityString)
    
    #add updating booking time in table 


#Function to continuously check the db 
def pollingDB():
    check_db = True  #make this a global variable, assuming db is not checked after working hours, this variable will only be set to true during working hours
    if check_db:
        select_query = "SELECT serialnumber,errorflag, status FROM sensor"
        cursor.execute(select_query)
        sensors = cursor.fetchall()
        for sensor in sensors:
            serialnumber,errorflag, status = sensor
            if errorflag == 1 or status == 'OFF':
                alert(serialnumber)

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
    total_consumption()
    total_offline()
    total_out_of_bounds()

if __name__ == "__main__":
    main()