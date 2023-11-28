import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from './App';

const Navigation = () => {
    const { logout } = useContext(AuthContext);

    function doClickTicketsR(e) {
        e.preventDefault();  // Prevent the default behavior of the anchor tag
        window.location.href = "accessdeniedR.html";
    };

    return (
        <div className="navigation">
            <ul>
                <li>
                    <a href="#">
                        <table>
                            <tbody>
                                <tr>
                                    <td width="60px">
                                        <div className="imgBx">
                                            <img src="assets/imgs/sensor2.jpg" alt="" />
                                        </div>
                                    </td>
                                    <td>
                                        <span className="title">Sensor Mgt. System</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </a>
                </li>

                <li>
                    <Link to="/real-time">
                        <span className="icon">
                            <ion-icon name="home-outline"></ion-icon>
                        </span>
                        <span className="title">Real-Time Data</span>
                    </Link>
                </li>

                <li>
                    <Link to="/historical">
                        <span className="icon">
                            <ion-icon name="home-outline"></ion-icon>
                        </span>
                        <span className="title">Historical Data</span>
                    </Link>
                </li>

                <li>
                    <Link to="/analytics">
                        <span className="icon">
                            <ion-icon name="people-outline"></ion-icon>
                        </span>
                        <span className="title">Analytics</span>
                    </Link>
                </li>

                <li>
                    <Link to="/reports">
                        <span className="icon">
                            <ion-icon name="chatbubble-outline"></ion-icon>
                        </span>
                        <span className="title">Reports</span>
                    </Link>
                </li>

                <li>
                    <Link to="/sensors">
                        <span className="icon">
                            <ion-icon name="help-outline"></ion-icon>
                        </span>
                        <span className="title">Configure Sensor</span>
                    </Link>
                </li>

                <li>
                    <Link to="/tickets">
                        <span className="icon">
                            <ion-icon name="settings-outline"></ion-icon>
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