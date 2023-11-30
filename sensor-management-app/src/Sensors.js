import React, { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import AddSensor from './AddSensor';
import useAuthorization from './useAuthorization';

const Sensors = () => {
  const [sensors, setSensors] = useState({});
  const [sortOrder, setSortOrder] = useState('asc');

  // Specify the allowed account types for this route
  const allowedAccounts = ['scientist', 'technician'];

  // Use the hook to check authorization
  const redirectPath = useAuthorization(allowedAccounts);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('https://127.0.0.1:5000/sensors', { withCredentials: true });
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

  const handleSort = () => {
    setSortOrder((prevSortOrder) => (prevSortOrder === 'asc' ? 'desc' : 'asc'));
  };

  // If redirectPath is not null, redirect the user
  if (redirectPath) {
    return <Navigate to={redirectPath} />;
  }

  // Convert sensors object to array for sorting
  const sortedSensors = Object.values(sensors).sort((a, b) => {
    if (sortOrder === 'asc') {
      return a.serial_number.localeCompare(b.serial_number);
    } else {
      return b.serial_number.localeCompare(a.serial_number);
    }
  });

  return (
    <div>
        <h2>Sensors</h2>
        <br />
        <h3>Add Sensor</h3>
        <AddSensor onSensorAdded={handleSensorAdded} />
        <br/>
        <button onClick={handleSort}>
          Sort {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
        </button>
        <table>
            <tbody>
                {sortedSensors.map((sensor) => (
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