import React, { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import AddSensor from './AddSensor';
import useAuthorization from './useAuthorization';

const Sensors = () => {
  const [sensors, setSensors] = useState({});

  // Specify the allowed account types for this route
  const allowedAccounts = ['scientist', 'technician'];

  // Use the hook to check authorization
  const redirectPath = useAuthorization(allowedAccounts);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/sensors', { withCredentials: true });
        setSensors(response.data);
      } catch (error) {
        console.error('Error fetching sensors:', error);
      }
    };

    if (!redirectPath) {
      fetchData();
    }
  }, [redirectPath]);

  const handleSensorAdded = (newSensor) => {
    setSensors((prevSensors) => {
      // Extract the sensor ID and the sensor object from newSensor
      const [newSensorId, newSensorData] = Object.entries(newSensor)[0];
      
      return {...prevSensors, [newSensorId]: newSensorData};
    });
  };

  // If redirectPath is not null, redirect the user
  if (redirectPath) {
    return <Navigate to={redirectPath} />;
  }

  return (
    <div>
        <h2>Sensors</h2>
        <br />
        <h3>Add Sensor</h3>
        <AddSensor onSensorAdded={handleSensorAdded} />
        <table>
            <tbody>
                {Object.values(sensors).map((sensor) => (
                    <tr key={sensor.serial_number}>
                        <td>{sensor.serial_number}</td>
                        <td>
                            <Link to={`/sensors/${sensor.serial_number}`}>
                                <button>
                                    Configure Sensor
                                </button>
                            </Link>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
  );
};

export default Sensors;