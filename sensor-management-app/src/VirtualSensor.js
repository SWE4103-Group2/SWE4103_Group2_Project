
import React, { useState } from 'react';
import axios from 'axios';

const VirtualSensor = ({ sensorIds }) => {
  const [selectedSensors, setSelectedSensors] = useState([]);
  const [creationMessage, setCreationMessage] = useState('');

  const handleCheckboxChange = (sensorId) => {
    // Toggle the selection of the sensor ID
    if (selectedSensors.includes(sensorId)) {
      setSelectedSensors(selectedSensors.filter(id => id !== sensorId));
    } else {
      setSelectedSensors([...selectedSensors, sensorId]);
    }
  };

  const handleCreateVirtualSensor = () => {
    // Make a request to create a virtual sensor using selected sensor IDs
    axios.post('http://127.0.0.1:5000/aggregate', { sensorIds: selectedSensors }, { withCredentials: true })
      .then(response => {
        // Handle success (if needed)        
        setCreationMessage(response.data);
      })
      .catch(error => console.error('Error creating virtual sensor:', error));
  };

  return (
    <div>
      <h2>Create Virtual Sensor</h2>
      <form>
        {sensorIds.map(sensorId => (
          <div key={sensorId}>
            <input
              type="checkbox"
              id={sensorId}
              checked={selectedSensors.includes(sensorId)}
              onChange={() => handleCheckboxChange(sensorId)}
            />
            <label htmlFor={sensorId}>{sensorId}</label>
          </div>
        ))}
      </form>
      <button onClick={handleCreateVirtualSensor}>Create Virtual Sensor</button>

      {creationMessage && (
        <div>
          <p>{creationMessage}</p>
        </div>
      )}
    </div>
  );
};

export default VirtualSensor;