#import pytest
import requests

BASE_URL = 'http://127.0.0.1:5000'  

existing_sensor = 'Water_River_S0017'
nonexistent_sensor = 'Water_Sea_S0002'
sensor_to_create = 'Water_Sea_S0001'

def test_get_sensors():
    response = requests.get(f'{BASE_URL}/Sensors')
    print(response)
    if response.status_code != 404:
        print(response.json())
    #assert response.status_code == 200

def test_get_sensor():
    response = requests.get(f'{BASE_URL}/Sensors/{existing_sensor}')
    print(response)
    if response.status_code != 404:
        print(response.json())
    #assert response.status_code == 200

def test_get_sensor_not_found():
    response = requests.get(f'{BASE_URL}/Sensors/{nonexistent_sensor}')
    print(response)
    #assert response.status_code == 404


def test_create_sensor():
    sensor_data = {
        's_SensorType': 'Energy',
        's_Location': 'Moncton',
        'i_SamplingRate': 1
    }
    response = requests.post(f'{BASE_URL}/Sensors/Create', json=sensor_data)
    print(response)
    #assert response.status_code == 200


def test_delete_sensor():
    response = requests.delete(f'{BASE_URL}/Sensors/{existing_sensor}')
    print(response, response.text)
    #assert response.status_code == 200


def test_set_sensor_value():
    sensorId = 'Water_LakeHuron_S0003'
    sensor_data = {
        'timestamp': '2023-11-08 14:07:28',
        'value': 3.7
    }
    response = requests.patch(f'{BASE_URL}/Sensors/{sensorId}', json=sensor_data)
    print(response, response.text)
    

def main(): 
    #test_get_sensors()
    #test_get_sensor()
    #test_get_sensor_not_found()
    #test_delete_sensor()
    #test_create_sensor()
    test_set_sensor_value()

if __name__ == '__main__':
    #pytest.main()
    main()