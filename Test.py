import datetime
import time
import random
# pip install firebase_admin
import firebase_admin
from firebase_admin import db
from random import randint

i_SamplingRate = 1
s_TimeFormat = "%Y-%m-%d %H:%M:%S"
s_TimeZone = "Atlantic"
i_DataRetentionMonths = 3
i_NumFiles = 5
f_RangeMin = 0.0
f_RangeMax = 50.0
serial_number = "abc123"

# firebase
ref = ""
cred_obj = firebase_admin.credentials.Certificate('C:/Users/olivi/Downloads/swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':"https://swe4103-db-default-rtdb.firebaseio.com/"
    })
###

# Function to generate simulated sensor data
def generate_sensor_data():
    # Simulate data or generate an error
    if randint(0, 100) < 90:  # 99.9% chance of valid data
        return random.uniform(f_RangeMin, f_RangeMax) # return a value in a set range (can be made configurable) assumed float
    else:
        return -1 # equivalent to null
    
# Function to update the data file
def update_data_file(s_SerialNumber, i_DataValue):
    now = datetime.datetime.now() # get current time
    timestamp = now.strftime(s_TimeFormat) # make current time into timestamp
    serial_number = s_SerialNumber
    lst_toAdd = []

    data_row = {
        "timestamp": timestamp,
        "id": serial_number,
        "value": i_DataValue
        }

    lst_toAdd.append(data_row)
    
    ref = db.reference("/waterdata") # re-directs
    for key in lst_toAdd:
        ref.push().set(key)

def main():
    lst_serial_numbers = ["Water_HydroElectricDam_S0005"]
    last_seen = None
    #while True:
    for i in range(0,16): # print 16 values for 3 sensors
        for serialNum in lst_serial_numbers: # to get name of file
            data_value = generate_sensor_data() # Simulate sensor data generation
            update_data_file(serialNum, data_value)
        time.sleep(i_SamplingRate) # Wait for the next sampling interval

def create_sensor():
    temp = []
    ref = db.reference('/sensors')
    new = {'error flag': 0, 'id': 'Water_HydroElectricDam_S0004', 'type': "Water"}
    temp.append(new)

    for key in temp:
        ref.push().set(key)

if __name__ == "__main__":
    #create_sensor()
    main()