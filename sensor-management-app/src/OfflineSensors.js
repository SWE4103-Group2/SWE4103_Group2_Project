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
      axios.get('https://127.0.0.1:5000/offline', { withCredentials: true })
        .then(response => {
          setOfflineSensors(response.data);
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
      <h2>Out of Bounds</h2>
      <br/>
      {loading && <p>Loading...</p>}
      {Object.values(offlineSensors).map(sensor => (
        <div key={sensor.serial_number}>
          <h3>{sensor.serial_number} Status: {sensor.status}</h3>
          <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                {sensor.historical_data.map((row, index) => (
                    <tr key={index}>
                      <td>{row.timestamp}</td>
                      <td>{row.value}</td>
                    </tr>
                ))}
              </tbody>
          </table>
          <br />
        </div>
      ))}
    </div>
  );
};

export default OfflineSensors;