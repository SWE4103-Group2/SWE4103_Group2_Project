import unittest
from SensorApplication4 import *
from SensorApplication4 import Sensor 
from contextlib import redirect_stdout
from io import StringIO

#Constants
sensor = getSensor("Water_LakeHuron_S0003")
s_Timestamp = "2023-11-08 14:07:28"
s_Timestamp2 = "2023-11-15 16:41:23"
schedule = "Technician_Schedule_Form.xlsx"
technician_id = 1

class UnitTests(unittest.TestCase):
    
    def print_test_result(self):
        test_name = self.id().split('.')[-1]  # Get the name of the current test
        if self._outcome.success:
            print(f"'{test_name}' passed.")
        else:
            print(f"'{test_name}' failed.")

    
    #Function to test get_type
    def test_get_type(self):
        with redirect_stdout(StringIO()):
            result = sensor.get_type()
        expected_type = sensor.s_SensorType
        self.assertEqual(result, expected_type)
        self.print_test_result()

    #Function to test get_value
    def test_get_value(self):
        with redirect_stdout(StringIO()):
            result = sensor.get_value(s_Timestamp)[1]
        select_query = "SELECT val FROM value WHERE timestamp = %s AND serialnum = %s"
        cursor.execute(select_query, (s_Timestamp, sensor.s_SerialNumber, ))
        sensor_data = cursor.fetchone()
        self.assertIsNotNone(sensor_data, "Data was not found for the given timestamp and serial number")
        expected_value = sensor_data[0]
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test set_value
    def test_set_value(self):
        expected_value = 1.14
        with redirect_stdout(StringIO()):
            sensor.set_value(s_Timestamp, expected_value)
        select_query = "SELECT val FROM value WHERE timestamp = %s AND serialnum = %s"
        cursor.execute(select_query, (s_Timestamp, sensor.s_SerialNumber, ))
        sensor_data = cursor.fetchone()
        self.assertIsNotNone(sensor_data, "Data was not found for the given timestamp and serial number")
        result = sensor_data[0]
        self.assertEqual(result, expected_value)
        self.print_test_result()

    
    
    #Function to test get_errorflag
    def test_get_errorflag(self):
        with redirect_stdout(StringIO()):
            result = sensor.get_errorflag()
        expected_value = sensor.i_ErrorFlag
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test set_errorflag
    def test_set_errorflag(self):
        expected_value = 0
        with redirect_stdout(StringIO()):
            sensor.set_errorflag(expected_value)
        result = sensor.i_ErrorFlag
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test get_status
    def test_get_status(self):
        with redirect_stdout(StringIO()):
            result = sensor.get_status()
        expected_value = sensor.s_Status
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test set_status
    def test_set_status(self):
        expected_value = "OFF"
        with redirect_stdout(StringIO()):
            sensor.set_status(expected_value)
        result = sensor.s_Status
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test get_sampling_rate
    def test_get_sampling_rate(self):
        with redirect_stdout(StringIO()):
            result = sensor.get_sampling_rate()
            expected_value = sensor.i_SamplingRate
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test set_sampling_rate
    def test_set_sampling_rate(self):
        expected_value = "5"
        with redirect_stdout(StringIO()):
            sensor.set_sampling_rate(expected_value)
        result = sensor.i_SamplingRate
        self.assertEqual(result, expected_value)
        self.print_test_result()
    
                
    #Function to test createSensor
    def test_createSensor(self): 
        s_SensorType = 'Water'
        s_Location = 'Bathurst'
        i_SamplingRate = 1
        sensor = createSensor(s_SensorType, s_Location, i_SamplingRate)

        self.assertIsInstance(sensor, Sensor)  
        self.assertEqual(sensor.s_SensorType, s_SensorType)  
        self.assertEqual(sensor.s_Location, s_Location) 
        self.assertEqual(sensor.i_SamplingRate, i_SamplingRate)  
    

    #Function to test getSensor
    def test_getSensor(self): 
        serial_num = "Water_LakeHuron_S0003"
        sensor = getSensor(serial_num)
        self.assertIsInstance(sensor, Sensor)  
        self.print_test_result()
    

    #Function to test deleteSensor 
    def test_delete_sensor(self):
        serial_num = "Water_LakeHuron_S0035"
        result = deleteSensor(serial_num)
        select_query = "SELECT * FROM sensor WHERE serialnumber = %s"
        cursor.execute(select_query, (serial_num, ))
        sensor_data = cursor.fetchone()
        if sensor_data != None: 
            self.assertTrue(result)  
        else: 
            self.assertFalse(result)
        self.print_test_result()
    

    #Function to test getCurrentHistoricalData 
    def test_getCurrentHistoricalData(self):
        serial_num = "Water_LakeHuron_S0003"
        select_query = "SELECT * FROM value"
        cursor.execute(select_query)
        sensor_data = cursor.fetchall()

        #pulling all historical data
        with redirect_stdout(StringIO()):
            result = getCurrentHistoricalData()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        

        #pulling historical data for specific sensor
        result = getCurrentHistoricalData(serial_num)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        self.print_test_result()
        
    
    #Function to test total_energy_consumption 
    def test_total_energy_consumption(self):
        result = total_energy_consumption()
        type = "Energy%"
        sum_query = "SELECT SUM(val) FROM value WHERE serialnum LIKE  %s"
        cursor.execute(sum_query,(type,))
        data = cursor.fetchone()
        self.assertIsNotNone(data, "Data was not found for the given sensor")
        expected_value= data[0]
        self.assertEqual(round(result), round(expected_value))
        self.print_test_result()
    
    
    #Function to test total_energy_consumption at a specific timestamp
    def test_total_energy_consumption(self):
        with redirect_stdout(StringIO()):
            result = total_energy_consumption(s_Timestamp2)
        type = "Energy%"
        sum_query = "SELECT SUM(val) FROM value WHERE timestamp = %s AND serialnum LIKE  %s"
        cursor.execute(sum_query,(s_Timestamp2,type,))
        data = cursor.fetchone()
        self.assertIsNotNone(data, "Data was not found for the given sensor")
        expected_value= data[0]
        self.assertEqual(round(result), round(expected_value))
        self.print_test_result()
    
    #Function to test total_water_consumption 
    def test_total_water_consumption(self):
        with redirect_stdout(StringIO()):
            result = total_water_consumption()
        type = "Water%"
        sum_query = "SELECT SUM(val) FROM value WHERE serialnum LIKE %s"
        cursor.execute(sum_query,(type,))
        expected_value= cursor.fetchone()[0]
        self.assertEqual(round(result), round(expected_value))
        self.print_test_result()

    #Function to test total_water_consumption at a specific timestamp
    def test_total_water_consumption(self):
        with redirect_stdout(StringIO()):
            result = total_water_consumption(s_Timestamp)
        type = "Water%"
        sum_query = "SELECT SUM(val) FROM value WHERE timestamp = %s AND serialnum LIKE  %s"
        cursor.execute(sum_query,(s_Timestamp,type,))
        expected_value= cursor.fetchone()[0]
        self.assertEqual(round(result), round(expected_value))
        self.print_test_result()
    
    #Function to test total_offline
    def test_total_offline(self):
        with redirect_stdout(StringIO()):
            result = total_offline()
        status = "OFF"
        sum_query = "SELECT COUNT(status) FROM sensor WHERE status =  %s"
        cursor.execute(sum_query,(status,))
        expected_value= cursor.fetchone()[0]
        self.assertEqual(result, expected_value)
        self.print_test_result()

    #Function to test total_out_of_bounds
    def test_total_out_of_bounds(self):
        errorflag = 1
        with redirect_stdout(StringIO()):
            result = total_out_of_bounds()
        
        sum_query = "SELECT COUNT(errorflag) FROM sensor WHERE errorflag =  %s"
        cursor.execute(sum_query,(errorflag,))
        expected_value= cursor.fetchone()[0]
        self.assertEqual(result, expected_value)
        self.print_test_result()
        


    #Function to test create_ticket
    def test_create_ticket(self):
        serial_num = "Water_Pond_S0006"
        with redirect_stdout(StringIO()):
            create_ticket(serial_num)
        #retrieve last ticket
        select_query = "SELECT * FROM ticket ORDER BY id DESC LIMIT 1"
        cursor.execute(select_query)
        record = cursor.fetchone()
        result = record[3]
        id = record[0]
        self.assertEqual(result, serial_num)
        self.print_test_result()

        #clean up- delete test ticket
        delete_query = "DELETE FROM ticket where id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()
    
    #Function to test update_ticket
    def test_update_ticket(self):
        expected = "UNRESOLVED"
        
        #retrieve last ticket and update it
        select_query = "SELECT * FROM ticket ORDER BY id DESC LIMIT 1"
        cursor.execute(select_query)
        last_ticket = cursor.fetchone()
        id = last_ticket[0]
        update_ticket(expected, id)

        #retrieve updated ticket 
        retrieve_updated_ticket = "SELECT * FROM ticket WHERE id = %s"
        cursor.execute(retrieve_updated_ticket, (id,))
        retrieved_ticket = cursor.fetchone()
        result = retrieved_ticket[2]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
