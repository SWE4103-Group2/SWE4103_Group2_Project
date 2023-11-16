import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AddSensor from './AddSensor';
import DeleteSensor from './DeleteSensor';
import OfflineSensors from './OfflineSensors';
import RealTime from './RealTime';
import Reports from './Reports';
import SensorList from './SensorList';

const MainContent = ({ showSensors=false, showRT=false, showHistorical=false, showAnalytics=false, showReports=false }) => {
  const [sensors, setSensors] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/');
        setSensors(response.data);
      } catch (error) {
        console.error('Error fetching sensors:', error);
      }
    };

    fetchData();
  }, []);

  const handleSensorAdded = (newSensor) => {
    setSensors((prevSensors) => {
      // Extract the sensor ID and the sensor object from newSensor
      const [newSensorId, newSensorData] = Object.entries(newSensor)[0];
      console.log('Previous Sensors:', prevSensors);
      return {...prevSensors, [newSensorId]: newSensorData};
    });
  };

  const handleSensorDeleted = (deletedSensorId) => {
    setSensors((prevSensors) => Object.values(prevSensors).filter((sensor) => sensor.serial_number !== deletedSensorId));
  };
  
  return (
    <div>
        <div className="main">
            <div className="topbar">
                <div className="toggle">
                    <ion-icon name="menu-outline"></ion-icon>
                </div>

                <div className="search">
                    <label>
                        <input type="text" placeholder="Search here"/>
                        <ion-icon name="search-outline"></ion-icon>
                    </label>
                </div>

                <div className="user">
                    <img src="assets/imgs/sensor1.jpg" alt=""/>
                </div>
            </div>

            {/* ======================= Cards ================== */}
            <div className="cardBox">
                <div className="card">
                    <div>
                        <div className="cardName">Sensor Alerts</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="eye-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Ticket Management System</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="cart-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Analysis</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="chatbubbles-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Reports</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="cash-outline"></ion-icon>
                    </div>
                </div>
            </div>

            {/* ================ Order Details List ================= */}
            <div className="details">
                <div className="Documentation">
                    {showRT && (
                        <RealTime />
                    )}
                    {showHistorical && (
                        <SensorList />
                    )}
                    {showAnalytics && (
                        <OfflineSensors />
                    )}
                    {showReports && (
                        <Reports />
                    )}
                    {showSensors && (
                        <div>
                            <AddSensor onSensorAdded={handleSensorAdded} />
                            <table>
                                <tbody>
                                    {Object.values(sensors).map((sensor) => (
                                        <tr key={sensor.serial_number}>
                                            <td>{sensor.serial_number}</td>
                                            <td>
                                                <DeleteSensor
                                                    sensorId={sensor.serial_number}
                                                    onSensorDeleted={handleSensorDeleted}
                                                />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* ================= New Customers ================ */}
                <div className="recentCustomers">
                    <div className="cardHeader">
                        <h2>Contact Lids</h2>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default MainContent;