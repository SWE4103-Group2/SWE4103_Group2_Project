from SensorApplication import (
    Sensor, get_sensors, get_sensor, getSensor, deleteSensor, createSensor,
    generate_sensor_data, update_database,
    get_latest_data,
    getCurrentHistoricalData,
    get_out_of_bounds,
    total_consumption, total_offline, total_out_of_bounds,
    aggregatesensors,
    update_aggregate, get_virtual_sensors,
    update_schedule_in_database,
    get_tickets,
    resolveTicket
)
from flask import Flask, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from threading import Thread, Lock
from time import sleep
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

s_ConfigFilePath = 'config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

serialNumbers = config["lst_SerialNumbers"]
i = 0

@app.route("/sensors")
def sensors():
    sensors = get_sensors()
    if sensors:
        return sensors, 200
    return sensors, 404

@app.route("/historical")
def historical():
    data = getCurrentHistoricalData()
    if data:
        return data, 200
    return data, 404

# Home page to display the list of sensors
@app.route("/real-time")
def simulation():
    global i
    for serialNum in serialNumbers:
        sensor = getSensor(serialNum)
        if sensor:
            samplingRate = sensor.get_sampling_rate()
            if samplingRate <= 5:
                data_value = generate_sensor_data(sensor.get_type())
                update_database(serialNum, data_value)
                print("Simulating real-time data... ", data_value)
            else:
                j = samplingRate // 5
                if i % j == 0:
                    data_value = generate_sensor_data()
                    update_database(serialNum, data_value)
                    print("Simulating real-time data... ", data_value)
    i += 1

    data = get_latest_data(serialNumbers)
    if data:
        return data, 200
    else:
        return "Sensor data not found.", 404

@app.route("/offline")
def offline():
    out_of_bounds = get_out_of_bounds()
    if out_of_bounds:
        return out_of_bounds, 200
    else:
        return out_of_bounds, 404

@app.route("/aggregate", methods=['POST'])
def aggregate():
    data = request.get_json()
    sensorIds = data['sensorIds']
    aggregate = aggregatesensors(sensorIds)
    if aggregate:
        return f"Virtual sensor {aggregate['vsid']} was created successfully!", 200
    return f"Virtual sensor creation was unsuccessful!", 404

@app.route("/analytics")
def analytics():
    water, energy = total_consumption()
    offline = total_offline()
    out = total_out_of_bounds()
    update_aggregate()
    virtualsensors = get_virtual_sensors()
    return {"water": water, "energy": energy, "offline": offline, "out": out, "virtualsensors": virtualsensors}, 200

@app.route("/upload", methods=['POST'])
def upload():
    try:
        excel_file = request.files['file']
        technician_id = request.form['technician_id']
        update_schedule_in_database(excel_file, technician_id)
        return "File uploaded successfully", 200
    except Exception as e:
        print(str(e))
        return f"Error processing the file: {str(e)}", 500

@app.route("/tickets")
def tickets():
    tickets = get_tickets()
    if tickets:
        return tickets, 200
    return tickets, 404
    
@app.route("/resolve", methods=['PATCH'])
def ticket():
    try:
        data = request.get_json()
        ticket_id = data['ticketId']
        resolveTicket(ticket_id)
        return f"Status of ticket {ticket_id} was updated to RESOLVED.", 200
    except Exception as e:
        print(str(e))
        return f"Error updating {ticket_id}", 404
    
@app.route("/Sensors/<s_SerialNumber>", methods= ['GET', 'DELETE', 'PATCH'])
def sensor(s_SerialNumber):
    if request.method == 'GET':
        if isinstance(getSensor(s_SerialNumber), Sensor):
            return get_sensor(s_SerialNumber), 200
        else:
            return f"{s_SerialNumber} not found.", 404
    
    if request.method == 'DELETE':
        if isinstance(getSensor(s_SerialNumber), Sensor):
            if deleteSensor(s_SerialNumber):
                return  f"{s_SerialNumber} was deleted.", 200
            else:
                return f"{s_SerialNumber} was not deleted an error occured." , 422   
        else:
            return f"{s_SerialNumber} does not exist, the delete operation was not done.", 404
       
    if request.method == 'PATCH':
        if isinstance(getSensor(s_SerialNumber), Sensor):
            #assumming data is received in json format
            data = request.get_json()
            s_SensorType = data['type']
            s_Location = data['location']
            i_SamplingRate = data['samplingrate']
            if getSensor(s_SerialNumber).set_value(s_SensorType, s_Location, i_SamplingRate): 
                return f"{s_SerialNumber} parameters were updated.", 200
            else:
                return f"{s_SerialNumber} parameters were not updated.", 304
        else:
            return s_SerialNumber + " not found, the update operation was not done.", 404
    

@app.route("/Sensors", methods= ['POST'])
def create_sensor():
    if request.method == 'POST':
        data = request.get_json()

        # Validate input data
        if 's_SensorType' not in data or 's_Location' not in data or 'i_SamplingRate' not in data:
            return f"Missing required fields", 400

        try:
            sensor = createSensor(data['s_SensorType'], data['s_Location'], data['i_SamplingRate'])
            return get_sensor(sensor.s_SerialNumber), 201
        except Exception as e:
            return str(e), 500

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)