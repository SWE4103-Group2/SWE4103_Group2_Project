#####################################################
'''
   (TechnicianSchedule.py)   OGR

env: Windows

'''
################### BASIC IMPORTS ###################
import json
import pandas as pd
from datetime import datetime, timedelta, time
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


## TEST ##
arr_df, lst_IdentifiersInOrder = getSchedule()
s_DayOfWeek, s_Month, s_Day, s_Year, s_Hour, s_AvailabilityString, time_EarliestDate, i_UserID = getEarliestAvailability(arr_df, lst_IdentifiersInOrder)
Book(i_UserID=i_UserID, s_DayOfWeek=s_DayOfWeek, s_Hour=s_Hour, s_AvailabilityString=s_AvailabilityString)
