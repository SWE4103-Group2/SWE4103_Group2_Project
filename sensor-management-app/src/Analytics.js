import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Analytics = () => {
  const [data, setData] = useState({ energy: 0, water: 0, offline: 0, out: 0, virtualsensors: [] });

  useEffect(() => {
    // Fetch sensor data analytics
    axios.get('http://127.0.0.1:5000/analytics', { withCredentials: true })
      .then(response => {
        setData(response.data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  return (
    <div>
      <h2>Analytics</h2>
      <table>
        <thead>
          <tr>
            <th>Total Energy Consumption</th>
            <th>Total Water Consumption</th>
            <th>Offline Sensor Count</th>
            <th>Out-of-Bounds Sensor Count</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{data.energy}</td>
            <td>{data.water}</td>
            <td>{data.offline}</td>
            <td>{data.out}</td>
          </tr>
        </tbody>
      </table>
      <br/>
      <h3>Virtual Sensors</h3>
      <table>
        <thead>
          <tr>
            <th>Virtual Sensor ID</th>
            <th>Value</th>
            <th>Sensors</th>
          </tr>
        </thead>
        <tbody>
          {data.virtualsensors.map(virtualSensor => (
            <tr key={virtualSensor.vsid}>
              <td>{virtualSensor.vsid}</td>
              <td>{virtualSensor.value}</td>
              <td>{virtualSensor.sensors}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Analytics;