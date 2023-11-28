import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Historical.css';

const Historical = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      // Fetch sensor data from Flask backend
      axios.get('http://127.0.0.1:5000/tickets')
        .then(response => {
          setTickets(response.data);
          console.log(response.data);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching sensors:', error);
          setLoading(false);
        });
  }, []);

  return (
    <div>
    </div>
  );
};

export default Historical;