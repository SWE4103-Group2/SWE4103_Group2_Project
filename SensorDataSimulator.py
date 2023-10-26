import os
import datetime
import time
import random
from random import randint
i_SamplingRate = 1
s_DataDirectory = "/Users/briannaorr/Documents/GitHub/SWE4103_Group2_Project/Files"
s_TimeFormat = "%Y-%m-%d %H:%M:%S"
s_TimeZone = "Atlantic"
i_DataRetentionMonths = 3
i_NumFiles = 5
f_RangeMin = 0.0
f_RangeMax = 50.0

def generate_sensor_data():
    if randint(0, 100) < 99.9:  # 99.9% chance of valid data
        return random.uniform(f_RangeMin, f_RangeMax) # return a value in a set range (can be made configurable) assumed float
    else:
        return None # equivalent to null
def update_data_file(s_SerialNumber, i_DataValue, time_LastSeen):
    now = datetime.datetime.now() # get current time
    timestamp = now.strftime(s_TimeFormat) # make current time into timestamp
    last_seen = timestamp  # Initial value, will be updated later
    serial_number = s_SerialNumber
    data_row = f"{timestamp},{serial_number},{time_LastSeen},{i_DataValue}\n" # Create the row of data
    data_file_path = os.path.join(s_DataDirectory, f"{s_SerialNumber}.csv")
    with open(data_file_path, "a") as file: # Open the data file in append mode
        file.write(data_row) # Write the data row
def purge_old_data():
    now = datetime.datetime.now() # get current time
    three_months_ago = now - datetime.timedelta(days=i_DataRetentionMonths * 30) # get the date
    three_months_ago_timestamp = three_months_ago.strftime(s_TimeFormat)
    data_files = os.listdir(s_DataDirectory)
    for file_name in data_files:
        file_path = os.path.join(s_DataDirectory, file_name)
        with open(file_path, "r") as file:
            lines = file.readlines()
            lines = [line for line in lines if line.strip().split(",")[0] >= three_months_ago_timestamp]
        with open(file_path, "w") as file:
            file.writelines(lines)

last_seen = None
for i in range(0,16):
    for i in range(1, i_NumFiles+1):
        data_value = generate_sensor_data()
        if isinstance(data_value, float): 
            last_seen = datetime.datetime.now().strftime(s_TimeFormat)
        update_data_file("S000"+str(i), data_value, last_seen)
    purge_old_data()
    time.sleep(i_SamplingRate)
