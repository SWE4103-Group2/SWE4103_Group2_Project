import React, { useEffect, useState } from 'react';
import axios from 'axios';

const UpdateSensor = ({ sensorId, onSensorUpdated }) => {
  const [sensorData, setSensorData] = useState({ type: '', location: '', samplingrate: '' });

  // Function to fetch sensor data from the server
  const fetchSensorData = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/Sensors/${sensorId}`, { withCredentials: true });
      setSensorData(Object.values(response.data)[0]); // Set the fetched sensor data in the state
    } catch (error) {
      console.error('Error fetching sensor data:', error);
    }
  };

  // useEffect hook to fetch sensor data when the component mounts
  useEffect(() => {
    fetchSensorData();
  }, [sensorId]); // Trigger the fetch when sensorId changes

  const handleUpdateSensor = async () => {
    try {
      const response = await axios.patch(`http://127.0.0.1:5000/Sensors/${sensorId}`, sensorData, { withCredentials: true });
      onSensorUpdated(response.data); // Notify parent component about the updated sensor
    } catch (error) {
      console.error('Error updating sensor:', error);
    }
  };

  return (
    <div>
      <label>
        Sensor Type:
        <input
          type="text"
          value={sensorData.type}
          onChange={(e) => setSensorData({ ...sensorData, type: e.target.value })}
        />
      </label>
      <br />
      <label>
        Location:
        <input
          type="text"
          value={sensorData.location}
          onChange={(e) => setSensorData({ ...sensorData, location: e.target.value })}
        />
      </label>
      <br />
      <label>
        Sampling Rate:
        <input
          type="number"
          value={sensorData.samplingrate}
          onChange={(e) => setSensorData({ ...sensorData, samplingrate: parseInt(e.target.value) })}
        />
      </label>
      <br />
      <button onClick={handleUpdateSensor}>Update Sensor</button>
    </div>
  );
};

export default UpdateSensor;