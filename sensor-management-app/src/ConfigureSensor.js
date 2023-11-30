import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DeleteSensor from './DeleteSensor';
import UpdateSensor from './UpdateSensor';

const ConfigureSensor = ({ sensorid }) => {
  const navigate = useNavigate();
  
  const [updateMessage, setUpdateMessage] = useState('')
  const handleSensorUpdated = (updatedSensorId) => {
    setUpdateMessage(updatedSensorId);
  };

  const handleBack = () => navigate('/sensors');

  return (
    <div>
        <h2>{sensorid}</h2>
        <UpdateSensor
            sensorId={sensorid}
            onSensorUpdated={handleSensorUpdated}
        />
        <DeleteSensor
            sensorId={sensorid}
        />
        <br/>
        {updateMessage && (
          <div>
            <p>{updateMessage}</p>
          </div>
        )}
        <br/>
        <button onClick={handleBack}>
          Back
        </button>
    </div>
  );
};

export default ConfigureSensor;