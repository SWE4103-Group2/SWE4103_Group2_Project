import mysql.connector
import matplotlib.pyplot as plt

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

# Function to retrieve sensor data from the database
def fetch_sensor_data(conn):
    cursor.execute("SELECT serialnumber, status FROM value")
    rows = cursor.fetchall()
    return rows

# Function to generate sample sensor data and insert into the database
def generate_sensor_data(conn, num_sensors):
    for sensor_id in range(1, num_sensors + 1):
        # Simulating sensor values (replace this with actual sensor data acquisition)
        sensor_value = random.uniform(0, 100)

        # Check for bad data values and set error_flag to 1
        if sensor_value < 10:  # Assuming threshold for bad data is 10
            error_flag = 1
        else:
            error_flag = 0

        # Randomly assign sensor status (online/offline)
        sensor_status = random.choice(['ON', 'OFF'])

        # Insert data into the database
        cursor.execute('''INSERT INTO sensors (sensor_id, status, value, error_flag)
                          VALUES (?, ?, ?, ?)''', (sensor_id, sensor_status, sensor_value, error_flag))
    
    conn.commit()
    
# Function to create a graph for online and offline sensors
def create_sensor_graph(sensor_data):
    online_sensors = sum(1 for sensor in sensor_data if sensor[1] == 'online')
    offline_sensors = sum(1 for sensor in sensor_data if sensor[1] == 'offline')

    labels = ['Online', 'Offline']
    values = [online_sensors, offline_sensors]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['green', 'red'])
    plt.xlabel('Sensor Status')
    plt.ylabel('Number of Sensors')
    plt.title('Online vs Offline Sensors')

    plt.show()

# Main function to execute the code
def main():
    database_name = 'your_database_name.db'  # Replace with your database name
    conn = connect_to_database(database_name)
    sensor_data = fetch_sensor_data(conn)
    conn.close()

    create_sensor_graph(sensor_data)

if __name__ == "__main__":
    main()