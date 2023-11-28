import React, { useEffect, useState } from 'react';
import axios from 'axios';
import firebase from './firebase';

const RealTime = () => {
  const [realTimeData, setRealTimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch real-time data from Flask backend
        const response = await axios.get('http://127.0.0.1:5000/real-time');
        console.log(response.data);

        // Sign in anonymously
        const userCredential = await firebase.auth().signInAnonymously();
        const user = userCredential.user;

        // Listen for changes in real-time data
        const ref = firebase.database().ref('/energydata');
        ref.on('value', (snapshot) => {
          const data = snapshot.val();
          if (data) {
            const keys = Object.keys(data);
            const lastKey = keys[keys.length - 1];
            const lastValue = data[lastKey];
            setRealTimeData(lastValue);
          }
          else {
            setRealTimeData([]);
          }
          setLoading(false);
        }, (error) => {
          console.error(error);
          setError('Error fetching real-time data from Firebase');
          setLoading(false);
        });
      } catch (error) {
        console.error('Error fetching sensors:', error);
        setError('Error fetching sensors');
        setLoading(false);
      }
    };

    fetchData();

    // Cleanup: Unsubscribe from Firebase updates when the component unmounts
    return () => {
      const ref = firebase.database().ref('/energydata');
      ref.off('value');
    };
  }, []);

  return (
    <div>
      <h1>Real-time Data</h1>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {!loading && (
        <div id="data">
          Timestamp: {realTimeData.timestamp}, Value: {realTimeData.value}
        </div>
      )}
    </div>
  );
};

export default RealTime;