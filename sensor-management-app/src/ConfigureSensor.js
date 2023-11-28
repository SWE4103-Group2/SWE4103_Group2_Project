import React from 'react';
import { Link } from 'react-router-dom';
import DeleteSensor from './DeleteSensor';
import UpdateSensor from './UpdateSensor';

const ConfigureSensor = ({ sensorid }) => {
  const handleSensorUpdated = (updatedSensorId) => {
    console.log(updatedSensorId);
  };

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
        <div>
            <Link to='/sensors'>
              <button>Back</button>
            </Link>
        </div>
    </div>
  );
};

export default ConfigureSensor;