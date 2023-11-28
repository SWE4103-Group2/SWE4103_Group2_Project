import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import axios from 'axios';
import useAuthorization from './useAuthorization';

const OfflineSensors = () => {
  const [offlineSensors, setOfflineSensors] = useState({});
  const [loading, setLoading] = useState(true);

  // Specify the allowed account types for this route
  const allowedAccounts = ['scientist', 'technician'];

  // Use the hook to check authorization
  const redirectPath = useAuthorization(allowedAccounts);

  useEffect(() => {
    // Fetch sensor data from Flask backend
    if (!redirectPath) {
      axios.get('http://127.0.0.1:5000/')
        .then(response => {
          const allSensors = response.data;
          const offlineSensors = Object.values(allSensors).map(sensor => {
            let filteredHistoricalData = [];
            if (sensor.type === 'Energy') {
              filteredHistoricalData = sensor.historical_data
                ? sensor.historical_data.filter(row => row.value < 0 || row.value > 50)
                : [];
            }
            else if (sensor.type === 'Water') {
              filteredHistoricalData = sensor.historical_data
                ? sensor.historical_data.filter(row => row.value < 0 || row.value > 4)
                : [];
            }
          
            return {
              ...sensor,
              historical_data: filteredHistoricalData,
            };
          });
          setOfflineSensors(offlineSensors);
          setLoading(false);
        })
        .catch(error => console.error('Error fetching sensors:', error));
    }
  }, [redirectPath]);

  // If redirectPath is not null, redirect the user
  if (redirectPath) {
    return <Navigate to={redirectPath} />;
  }

  return (
    <div>
      <h2>Offline Sensors</h2>
      {loading && <p>Loading...</p>}
      {Object.values(offlineSensors).map(sensor => (
          sensor.historical_data.length > 0 && (
              <div key={sensor.serial_number}>
                  <div>Serial Number: {sensor.serial_number}</div>
                  <div>Status: {sensor.status}</div>
                  {sensor.historical_data.map((row, index) => (
                      <div key={index}>
                        Timestamp: {row.timestamp}, Value: {row.value}
                      </div>
                  ))}
                  <br />
              </div>
          )
      ))}
    </div>
  );
};

export default OfflineSensors;