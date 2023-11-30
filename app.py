from SensorApplication import Sensor, get_sensors,get_sensor,  getSensor,deleteSensor, createSensor
from flask import Flask, request


app = Flask(__name__)

@app.route("/Sensors")
def sensors():
    if get_sensors():
        return get_sensors(), 200
    return get_sensors(), 404
    
@app.route("/Sensors/<s_SerialNumber>", methods= ['GET', 'DELETE', 'PATCH', 'POST'])
def sensor(s_SerialNumber):
    if request.method == 'GET':
        if get_sensor(s_SerialNumber) is not None:
            return get_sensor(s_SerialNumber), 200
        else:
            return f"{s_SerialNumber} not found.", 404
    
    if request.method == 'DELETE':
        if get_sensor(s_SerialNumber) is not None:
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
            s_Timestamp = data['timestamp']
            f_NewValue = data['value']
            if getSensor(s_SerialNumber).set_value(s_Timestamp, f_NewValue): 
                return f"The value of sensor {s_SerialNumber} at timestamp {s_Timestamp} was updated to {f_NewValue}.", 200
            else:
                return f"The value of sensor {s_SerialNumber} at timestamp {s_Timestamp} was not updated.", 304
        else:
            return s_SerialNumber + " not found, the update operation was not done.", 404
    

@app.route("/Sensors/Create", methods= ['POST'])
def create_sensor():
    if request.method == 'POST':
        data = request.get_json()

        # Validate input data
        if 's_SensorType' not in data or 's_Location' not in data or 'i_SamplingRate' not in data:
            return f"Missing required fields", 400

        try:
            sensor = createSensor(data['s_SensorType'], data['s_Location'], data['i_SamplingRate'])
            return f"Sensor created with Serial Number: {sensor.s_SerialNumber}", 201
        except Exception as e:
            return str(e), 500

if __name__ == '__main__':
    app.run(debug = True)