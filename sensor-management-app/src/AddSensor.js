import React, { useState } from 'react';
import axios from 'axios';

const AddSensor = ({ onSensorAdded }) => {
  const [sensorData, setSensorData] = useState({ s_SensorType: '', s_Location: '', i_SamplingRate: '' });

  const handleAddSensor = async () => {
    try {
      const response = await axios.post('http://localhost:5000/Sensors', sensorData);
      onSensorAdded(response.data); // Notify parent component about the added sensor
      setSensorData({ s_SensorType: '', s_Location: '', i_SamplingRate: '' }); // Clear input field
    } catch (error) {
      console.error('Error adding sensor:', error);
    }
  };

  return (
    <div>
      <h2>Add Sensor</h2>
      <label>
        Sensor Type:
        <input
          type="text"
          value={sensorData.s_SensorType}
          onChange={(e) => setSensorData({ ...sensorData, s_SensorType: e.target.value })}
        />
      </label>
      <br />
      <label>
        Location:
        <input
          type="text"
          value={sensorData.s_Location}
          onChange={(e) => setSensorData({ ...sensorData, s_Location: e.target.value })}
        />
      </label>
      <br />
      <label>
        Sampling Rate:
        <input
          type="number"
          value={sensorData.i_SamplingRate}
          onChange={(e) => setSensorData({ ...sensorData, i_SamplingRate: e.target.value })}
        />
      </label>
      <br />
      <button onClick={handleAddSensor}>Add Sensor</button>
    </div>
  );
};

export default AddSensor;