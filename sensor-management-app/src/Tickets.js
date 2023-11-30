import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useAuthorization from './useAuthorization';
import './Historical.css';

const Tickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  // Specify the allowed account types for this route
  const allowedAccounts = ['technician'];

  // Use the hook to check authorization
  const redirectPath = useAuthorization(allowedAccounts);

  useEffect(() => {
      if (!redirectPath) {
        // Fetch sensor data from Flask backend
        axios.get('https://127.0.0.1:5000/tickets', { withCredentials: true })
          .then(response => {
            setTickets(response.data);
            setLoading(false);
          })
          .catch(error => {
            console.error('Error fetching sensors:', error);
            setLoading(false);
          });
      }
  }, [redirectPath]);
  
const handleResolveTicket = (ticketId) => {
    axios.patch('https://127.0.0.1:5000/resolve', { ticketId })
    .then(response => {
      console.log(response.data);
    })
    .catch(error => {
      console.error('Error updating ticket status: ', error);
    });
  };
  
  return (
    <div>
      <h2>Tickets</h2>
      {loading ? (
        <p>Loading tickets...</p>
      ) : (
        <div>
          <table className="historical-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Booking Time</th>
                <th>State</th>
                <th>Sensor</th>
                <th>Technician ID</th>
                <th>Resolve</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map(ticket => (
                <tr key={ticket.ticketId}>
                  <td>{ticket.ticketId}</td>
                  <td>{ticket.bookingTime}</td>
                  <td>{ticket.state}</td>
                  <td>{ticket.sensor}</td>
                  <td>{ticket.technicianId}</td>
                  <td>
                    {ticket.state==="UNRESOLVED" && (
                      <button onClick={() => handleResolveTicket(ticket.ticketId)}>Resolve</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <br/>
        </div>
       )}
    </div>
   );
};
export default Tickets;