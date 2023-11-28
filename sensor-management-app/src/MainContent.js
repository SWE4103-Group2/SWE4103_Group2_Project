import React from 'react';
import { useParams } from 'react-router-dom';
import ConfigureSensor from './ConfigureSensor';
import Historical from './Historical';
import OfflineSensors from './OfflineSensors';
import RealTime from './RealTime';
import Reports from './Reports';
import Sensors from './Sensors';
import Tickets from './Tickets';

const MainContent = ({ showSensors=false}) => {
  const { show, sensorid } = useParams();
  
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
                    {show==='real-time' && (
                        <RealTime />
                    )}
                    {show==='historical' && (
                        <Historical />
                    )}
                    {show==='analytics' && (
                        <OfflineSensors />
                    )}
                    {show==='reports' && (
                        <Reports />
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
                        <h2>Contact Lids</h2>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default MainContent;