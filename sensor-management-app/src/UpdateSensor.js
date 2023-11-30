import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

const UpdateSensor = ({ sensorId, onSensorUpdated }) => {
  const [sensorData, setSensorData] = useState({ type: '', location: '', samplingrate: '' });
  const [error, setError] = useState('');

  // Function to fetch sensor data from the server
  const fetchSensorData = useCallback(async () => {
    try {
      const response = await axios.get(`https://127.0.0.1:5000/Sensors/${sensorId}`, { withCredentials: true });
      setSensorData(Object.values(response.data)[0]); // Set the fetched sensor data in the state
    } catch (error) {
      console.error('Error fetching sensor data:', error);
    }
  }, [sensorId]);

  // useEffect hook to fetch sensor data when the component mounts
  useEffect(() => {
    fetchSensorData();
  }, [fetchSensorData]); // Trigger the fetch when sensorId changes

  const handleUpdateSensor = async () => {
    if (!sensorData.type || !sensorData.location || sensorData.samplingrate <= 0) {
      setError('Please provide valid input for all fields.');
      return;
    }

    try {
      const response = await axios.patch(`https://127.0.0.1:5000/Sensors/${sensorId}`, sensorData, { withCredentials: true });
      onSensorUpdated(response.data); // Notify parent component about the updated sensor
      setError('');
    } catch (error) {
      console.error('Error updating sensor:', error);
    }
  };

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
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