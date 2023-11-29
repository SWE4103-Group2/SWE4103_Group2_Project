import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ConfigureSensor from './ConfigureSensor';
import Historical from './Historical';
import OfflineSensors from './OfflineSensors';
import RealTime from './RealTime';
import Analytics from './Analytics';
import Sensors from './Sensors';
import Tickets from './Tickets';
import VirtualSensor from './VirtualSensor';
import customer from './assets/imgs/customer.png'

const MainContent = ({ showSensors=false}) => {
  const { show, sensorid } = useParams();
  const [sensorIds, setSensorIds] = useState([]);

  useEffect(() => {
    // Fetch sensor IDs
    axios.get('http://127.0.0.1:5000/sensors', { withCredentials: true })
      .then(response => {
        setSensorIds(Object.keys(response.data));
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);
  
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
                    <img src={customer} alt=""/>
                </div>
            </div>

            {/* ======================= Cards ================== */}
            <div className="cardBox">
                <div className="card">
                    <div>
                        <div className="cardName">Sensor Alerts</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="alert-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Ticket Management System</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="construct-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Analysis</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="bar-chart-outline"></ion-icon>
                    </div>
                </div>

                <div className="card">
                    <div>
                        <div className="cardName">Reports</div>
                    </div>

                    <div className="iconBx">
                        <ion-icon name="document-outline"></ion-icon>
                    </div>
                </div>
            </div>

            {/* ================ Order Details List ================= */}
            <div className="details">
                <div className="centered-content">
                    {show==='real-time' && (
                        <RealTime />
                    )}
                    {show==='historical' && (
                        <Historical />
                    )}
                    {show==='analytics' && (
                        <Analytics />
                    )}
                    {show==='reports' && (
                        <OfflineSensors />
                    )}
                    {showSensors && !sensorid && (
                        <Sensors />
                    )}
                    {sensorid && (
                        <ConfigureSensor sensorid={sensorid} />
                    )}
                    {show==='tickets' && (
                        <Tickets />
                    )}
                </div>

                {/* ================= New Customers ================ */}
                <div className="recentCustomers">
                    <div className="cardHeader">
                        {show==='analytics' && (
                            <VirtualSensor sensorIds={sensorIds} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default MainContent;