import React from 'react';
import axios from 'axios';

const DeleteSensor = ({ sensorId, onSensorDeleted }) => {
  const handleDeleteSensor = async () => {
    try {
      await axios.delete(`http://localhost:5000/Sensors/${sensorId}`);
      onSensorDeleted(sensorId); // Notify parent component about the deleted sensor
    } catch (error) {
      console.error('Error deleting sensor:', error);
    }
  };

  return (
    <div>
      <button onClick={handleDeleteSensor}>Delete Sensor</button>
    </div>
  );
};

export default DeleteSensor;