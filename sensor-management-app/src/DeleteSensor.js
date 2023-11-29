import React from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const DeleteSensor = ({ sensorId }) => {
  const handleDeleteSensor = async () => {
    try {
      await axios.delete(`http://127.0.0.1:5000/Sensors/${sensorId}`, { withCredentials: true });
    } catch (error) {
      console.error('Error deleting sensor:', error);
    }
  };

  return (
    <div>
      <Link to='/sensors'>
          <button onClick={handleDeleteSensor}>
            Delete Sensor
          </button>
      </Link>
    </div>
  );
};

export default DeleteSensor;