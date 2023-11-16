import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Reports = () => {
  const [totalEnergyConsumption, setTotalEnergyConsumption] = useState(0);
  const [totalWaterConsumption, setTotalWaterConsumption] = useState(0);
  const [offlineSensorCount, setOfflineSensorCount] = useState(0);
  const [outOfBoundsSensorCount, setOutOfBoundsSensorCount] = useState(0);

  useEffect(() => {
    // Fetch sensor data from the Flask backend
    axios.get('http://localhost:5000/')
      .then(response => {
        const allSensors = response.data;

        // Calculate total energy consumption and water consumption
        let energyConsumption = 0;
        let waterConsumption = 0;

        // Count offline and out-of-bounds sensors
        let offlineCount = 0;
        let outOfBoundsCount = 0;

        Object.values(allSensors).forEach(sensor => {
            let outOfBoundsValues = false;
            if (sensor.type === 'Energy') {
                energyConsumption += calculateEnergyConsumption(sensor);
                // Check if the sensor has out-of-bounds values
                outOfBoundsValues = sensor.historical_data
                    ? sensor.historical_data.some(row => row.value < 0 || row.value > 50)
                    : false;
            }
            else if (sensor.type === 'Water') {
                waterConsumption += calculateWaterConsumption(sensor);
                outOfBoundsValues = sensor.historical_data
                    ? sensor.historical_data.some(row => row.value < 0 || row.value > 4)
                    : false;
            }

            if (outOfBoundsValues) {
                outOfBoundsCount++;
            }

            // Check if the sensor is offline
            if (sensor.status === 'OFF') {
                offlineCount++;
            }
        });

        setTotalEnergyConsumption(energyConsumption.toFixed(4));
        setTotalWaterConsumption(waterConsumption.toFixed(4));
        setOfflineSensorCount(offlineCount);
        setOutOfBoundsSensorCount(outOfBoundsCount);
      })
      .catch(error => console.error('Error fetching sensors:', error));
  }, []);

  const calculateEnergyConsumption = (sensor) => {
    // sum up the values in historical_data
    var total = 0;
    if (sensor.historical_data !== null) {
        total = sensor.historical_data.reduce((sum, row) => sum + row.value, 0);
    }
    return total;
  };

  const calculateWaterConsumption = (sensor) => {
    // sum up the values in historical_data
    var total = 0;
    if (sensor.historical_data !== null) {
        total = sensor.historical_data.reduce((sum, row) => sum + row.value, 0);
    }
    return total;
  };

  return (
    <div>
      <h2>Reports</h2>
      <p>Total Energy Consumption: {totalEnergyConsumption} kWh</p>
      <p>Total Water Consumption: {totalWaterConsumption} l/min</p>
      <p>Offline Sensor Count: {offlineSensorCount}</p>
      <p>Out-of-Bounds Sensor Count: {outOfBoundsSensorCount}</p>
    </div>
  );
};

export default Reports;