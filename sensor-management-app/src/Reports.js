import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Reports = () => {
  const [data, setData] = useState({ energy: 0, water: 0, offline: 0, out: 0 });

  useEffect(() => {
    // Fetch sensor data from the Flask backend
    axios.get('http://127.0.0.1:5000/reports')
      .then(response => {
        setData(response.data);
      })
      .catch(error => console.error('Error fetching sensors:', error));
  }, []);

  return (
    <div>
      <h2>Reports</h2>
      <p>Total Energy Consumption: {data.energy} kWh</p>
      <p>Total Water Consumption: {data.water} l/min</p>
      <p>Offline Sensor Count: {data.offline}</p>
      <p>Out-of-Bounds Sensor Count: {data.out}</p>
    </div>
  );
};

export default Reports;