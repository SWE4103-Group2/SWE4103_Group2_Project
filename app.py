from Sensor import getSensor,sensor_to_dict,sensors_to_dict,deleteSensor, Sensor
from flask import Flask, request, json, jsonify


s_ConfigFilePath = '/Users/briannaorr/Documents/Github/SWE4103_Group2_Project/config.json'

################### CONFIGURATION ###################
with open(s_ConfigFilePath, 'r') as config_file:
    config = json.load(config_file)

s_ServiceAccountKeyPath   = config["s_ServiceAccountKeyPath"]
s_DatabaseURL             = config["s_DatabaseURL"]
s_SensorPath              = config["s_SensorPath"]
s_SerialNumber            = config["s_SerialNumber"]
i_SamplingRate            = config["i_SamplingRate"]
############## END: CONFIGURATION ###################

#serial number of sensor to be deleted 
s_SerialNumber_delete = 'Water_LakeHuron_S0001'

app = Flask(__name__)


@app.route("/Sensors")
def sensors():
    if sensors_to_dict(s_SensorPath):
        return sensors_to_dict(s_SensorPath), 200
    return "Sensors not found.", 404
    
@app.route("/Sensors/<s_SerialNumber>", methods= ['GET', 'DELETE', 'PATCH'])
def sensor(s_SerialNumber):
    if request.method == 'GET':
        if isinstance(getSensor(s_SerialNumber,s_SensorPath), Sensor):
            return sensor_to_dict(getSensor(s_SerialNumber, s_SensorPath)), 200
        else:
            return s_SerialNumber + " not found.", 404
    
    if request.method == 'DELETE':
        if isinstance(getSensor(s_SerialNumber,s_SensorPath), Sensor):
            deleteSensor(s_ServiceAccountKeyPath, s_DatabaseURL, s_SensorPath, s_SerialNumber_delete)
            return  s_SerialNumber + " deleted.", 200
        else:
            return s_SerialNumber + " not found.", 404
       
    if request.method == 'PATCH':
        if isinstance(getSensor(s_SerialNumber,s_SensorPath), Sensor):
            #assumming data is received in json format
            data = request.get_json()
            s_Timestamp = data['timestamp']
            f_NewValue = data['value']
            getSensor(s_SerialNumber,s_SensorPath).set_value(s_Timestamp, f_NewValue)
        else:
            return s_SerialNumber + " not found.", 404



if __name__ == '__main__':
    app.run(debug = True)