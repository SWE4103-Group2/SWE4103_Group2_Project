import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from './App';
import sensor from './assets/imgs/sensor.png';
import './Navigation.css';

const Navigation = () => {
    const { logout } = useContext(AuthContext);

    return (
        <div className="navigation">
            <ul>
                <li>
                    <a href="#">
                        <div className="item-container">
                            <div className="image-container">
                                <img
                                    src={sensor}
                                    alt=""
                                    style={{ width: '60px', height: 'auto' }}
                                />
                            </div>
                            <div className="text-container">
                                <span className="title">Sensor Mgt. System</span>
                            </div>
                        </div>
                    </a>
                </li>

                <li>
                    <Link to="/real-time">
                        <span className="icon">
                            <ion-icon name="refresh-circle-outline"></ion-icon>
                        </span>
                        <span className="title">Real-Time Data</span>
                    </Link>
                </li>

                <li>
                    <Link to="/historical">
                        <span className="icon">
                            <ion-icon name="time-outline"></ion-icon>
                        </span>
                        <span className="title">Historical Data</span>
                    </Link>
                </li>

                <li>
                    <Link to="/analytics">
                        <span className="icon">
                            <ion-icon name="bar-chart-outline"></ion-icon>
                        </span>
                        <span className="title">Analytics</span>
                    </Link>
                </li>

                <li>
                    <Link to="/reports">
                        <span className="icon">
                            <ion-icon name="document-text-outline"></ion-icon>
                        </span>
                        <span className="title">Reports</span>
                    </Link>
                </li>

                <li>
                    <Link to="/sensors">
                        <span className="icon">
                            <ion-icon name="settings-outline"></ion-icon>
                        </span>
                        <span className="title">Configure Sensor</span>
                    </Link>
                </li>

                <li>
                    <Link to="/tickets">
                        <span className="icon">
                            <ion-icon name="construct-outline"></ion-icon>
                        </span>
                        <span className="title">Tickets</span>
                    </Link>
                </li>

                <li>
                    <a href="#">
                        <span className="icon">
                            <ion-icon name="lock-closed-outline"></ion-icon>
                        </span>
                        <span className="title">Password</span>
                    </a>
                </li>

                <li>
                    <a href="/login" onClick={logout}>
                        <span className="icon">
                            <ion-icon name="log-out-outline"></ion-icon>
                        </span>
                        <span className="title">Sign Out</span>
                    </a>
                </li>
            </ul>
        </div>
    );
};

export default Navigation;