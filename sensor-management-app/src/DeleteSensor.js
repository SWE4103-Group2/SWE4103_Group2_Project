import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const DeleteSensor = ({ sensorId }) => {
  const navigate = useNavigate();

  const handleDeleteSensor = async () => {
    try {
      await axios.delete(`https://127.0.0.1:5000/Sensors/${sensorId}`, { withCredentials: true });
      navigate('/sensors');
    } catch (error) {
      console.error('Error deleting sensor:', error);
    }
  };

  return (
    <div>
      <button onClick={handleDeleteSensor}>
        Delete Sensor
      </button>
    </div>
  );
};

export default DeleteSensor;