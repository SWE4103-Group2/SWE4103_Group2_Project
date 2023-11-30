import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const VirtualSensor = () => {
  const [sensorGroups, setSensorGroups] = useState({});
  const [selectedSensors, setSelectedSensors] = useState([]);
  const [creationMessage, setCreationMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch sensor IDs
    axios.get('https://127.0.0.1:5000/sensors', { withCredentials: true })
      .then(response => {
        // Organize sensor IDs into groups based on common prefix
        const groupedSensors = Object.keys(response.data).reduce((groups, sensorId) => {
          const prefix = sensorId.split('_').slice(0, -1).join('_'); // Extract common prefix
          if (!groups[prefix]) {
            groups[prefix] = [];
          }
          groups[prefix].push(sensorId);
          return groups;
        }, {});

        setSensorGroups(groupedSensors);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

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
    axios.post('https://127.0.0.1:5000/aggregate', { sensorIds: selectedSensors }, { withCredentials: true })
      .then(response => {
        // Handle success (if needed)
        setCreationMessage(response.data);
      })
      .catch(error => console.error('Error creating virtual sensor:', error));
  };

  const handleBack = () => navigate('/analytics');

  return (
    <div className="centered-content">
      <h2>Create Virtual Sensor</h2>
      <br/>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        {Object.entries(sensorGroups).map(([prefix, sensors]) => (
          <div key={prefix}>
            <h3>{prefix}</h3>
            <div>
              <input
                type="checkbox"
                id={`checkAll_${prefix}`}
                checked={sensors.every(sensorId => selectedSensors.includes(sensorId))}
                onChange={() => {
                  const newSelectedSensors = sensors.every(sensorId => selectedSensors.includes(sensorId))
                    ? selectedSensors.filter(id => !sensors.includes(id))
                    : [...selectedSensors, ...sensors];
                  setSelectedSensors(newSelectedSensors);
                }}
              />
              <label htmlFor={`checkAll_${prefix}`}>Check All</label>
            </div>
            <form>
              {sensors.slice(0, 5).map(sensorId => (
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
          </div>
        ))}
      </div>
      <br/>
      <button onClick={handleCreateVirtualSensor}>Create Virtual Sensor</button>
      <br />
      {creationMessage && (
        <div>
          <p>{creationMessage}</p>
        </div>
      )}
      <br />
      <button onClick={handleBack}>
        Back
      </button>
    </div>
  );
};

export default VirtualSensor;