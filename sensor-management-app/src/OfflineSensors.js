import React, { useState, useEffect } from 'react';
import axios from 'axios';

const OfflineSensors = () => {
    const [offlineSensors, setOfflineSensors] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch sensor data from Flask backend
        axios.get('http://localhost:5000/')
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
    }, []);

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