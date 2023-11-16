from SensorApplication import Sensor, get_sensors, get_sensor, getSensor, deleteSensor, createSensor
from flask import Flask, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from threading import Thread, Lock
from time import sleep

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin
cred = credentials.Certificate("swe4103-db-firebase-adminsdk-jq4dv-e4128ec05e.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://swe4103-db-default-rtdb.firebaseio.com'
})

data_ref = db.reference("/energydata")
ref = db.reference("/simulation")
data = ref.get()

class RealTimeThread(Thread):
    def __init__(self, lock):
        super().__init__()
        self._stop_flag = False
        self.lock = lock

    def run(self):
        global data, data_ref
        while not self._stop_flag:
            result = data_ref.get()
            if result is not None:
                last = list(result.values())[-1]
            else:
                last = {"id": "", "timestamp": "", "value": -1}
            
            # Real-time data simulation
            prev = {"id": "", "timestamp": "", "value": -1}
            for val in data.values():
                with self.lock:
                    if prev["id"] == last["id"] and prev["timestamp"] == last["timestamp"]:
                        break
                    prev = val
            
            with self.lock:
                data_ref.push().set(val)
                print("Simulating real-time data... ", val)
            
            sleep(5)

    def stop(self):
        self._stop_flag = True

real_time_thread = None

@app.route("/")
def sensors():
    global real_time_thread

    if real_time_thread and real_time_thread.is_alive():
        real_time_thread.stop()
        real_time_thread.join()
    
    sensors = get_sensors()
    if sensors:
        return sensors, 200
    return sensors, 404

# Home page to display the list of sensors
@app.route("/real-time")
def simulation():
    global real_time_thread

    if real_time_thread and real_time_thread.is_alive():
        return "Real-time simulation is already running", 200

    # Create a lock
    data_lock = Lock()

    # Start a new thread
    real_time_thread = RealTimeThread(data_lock)
    real_time_thread.start()

    return "Real-time simulation started", 200
    
@app.route("/Sensors/<s_SerialNumber>", methods= ['GET', 'DELETE', 'PATCH', 'POST'])
def sensor(s_SerialNumber):
    global real_time_thread

    if real_time_thread and real_time_thread.is_alive():
        real_time_thread.stop()
        real_time_thread.join()
    
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
    

@app.route("/Sensors", methods= ['POST'])
def create_sensor():
    global real_time_thread

    if real_time_thread and real_time_thread.is_alive():
        real_time_thread.stop()
        real_time_thread.join()
    
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
    app.run(debug = True)