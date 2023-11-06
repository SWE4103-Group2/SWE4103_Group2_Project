import requests

base_URL = "http://127.0.0.1:5000/"
test_sensor_1 = "Sensors/Water_Field_2_S0001"
test_sensor_2 = "Sensors/Water_LakeHuron_S0001"

data = {
        "timestamp": "2023-10-26 21:38:38" , 
        "value": "2.5" 
    }

def get_sensors_test(): 
    try: 
        response = requests.get(base_URL + "Sensors")
        if response.status_code == 200: 
            print("Response:")
            print(response.text)
        else:
            print(f"GET Request failed with status code {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"GET Request failed with an exception: {e}")

def delete_sensor_test(): 
    try: 
        response = requests.delete(base_URL + test_sensor_2)
        if response.status_code == 200: 
            print("Response:")
            print(response.text)
        else:
            print(f"DELETE Request failed with status code {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"DELETE Request failed with an exception: {e}")


def get_sensor_data_test():
    try: 
        response = requests.get(base_URL + test_sensor_1)
        if response.status_code == 200: 
            print("Response:")
            print(response.text)
        else:
            print(f"GET Request failed with status code {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"GET Request failed with an exception: {e}")


def patch_sensor_data_test():
    try:
        response = requests.patch(base_URL + test_sensor_1, json=data)
        
        if response.status_code == 200:
            print("PATCH Request was successful.")
            print("Response:")
            print(response.text)
        else:
            print(f"PATCH Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"PATCH Request failed with an exception: {e}")



def main():
    #get_sensors_test()
    #delete_sensor_test()
    #get_sensor_data_test()
    #Patch fails 
    patch_sensor_data_test()

if __name__ == '__main__':
   main()