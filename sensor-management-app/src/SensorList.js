import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SensorList = () => {
  const [sensors, setSensors] = useState({});
  const [updateFormData, setUpdateFormData] = useState({ sensorId: '', timestamp: '', value: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      // Fetch sensor data from Flask backend
      axios.get('http://localhost:5000/')
        .then(response => {
          setSensors(response.data);
          setLoading(false);
        })
        .catch(error => console.error('Error fetching sensors:', error));
  }, []);

  const handleUpdate = (sensorId, timestamp, value) => {
    // Set initial values for the update form
    setUpdateFormData({ sensorId, timestamp, value });
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setUpdateFormData({ ...updateFormData, [name]: value });
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    
    const { sensorId, timestamp, value } = updateFormData;
    
    // Make a PATCH request to the Flask backend using Axios
    axios.patch(`http://localhost:5000/Sensors/${sensorId}`, { timestamp: timestamp, value: value })
    .then(response => {
      console.log('Patch request successful:', response.data);
    })
    .catch(error => {
      console.error('Error in patch request:', error);
    });

    // After submitting, clear the form data
    setUpdateFormData({ sensorId: '', timestamp: '', value: '' });
  };

  return (
    <div>
      <h2>Historical Data</h2>
      {loading && <p>Loading...</p>}
      <table>
        {!loading && (
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Value</th>
              <th>Action</th>
            </tr>
          </thead>
        )}
        <tbody>
          {Object.keys(sensors).map(sensorId => {
            const sensor = sensors[sensorId];
            return (
              <React.Fragment key={sensorId}>
                {sensor.historical_data !== null && (
                  sensor.historical_data.map(row => (
                    <tr key={row.serialnum}>
                      <td>{row.serialnum}</td>
                      <td>{row.timestamp}</td>
                      <td>{row.value}</td>
                      <td>
                        {(updateFormData.sensorId !== sensorId || updateFormData.timestamp !== row.timestamp) && (
                          <button onClick={() => handleUpdate(sensorId, row.timestamp, row.value)}>Update</button>
                        )}
                        {/* Update Form */}
                        {updateFormData.sensorId === sensorId && updateFormData.timestamp === row.timestamp && (
                          <form onSubmit={handleFormSubmit}>
                            <input type="number" step="0.1" name="value" value={updateFormData.value} onChange={handleFormChange}/>
                            <button type="submit">Submit</button>
                          </form>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default SensorList;