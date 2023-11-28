import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import firebase from './firebase';
import { Line } from 'react-chartjs-2';
import { Chart, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js';

Chart.register(LineElement, PointElement, LinearScale, CategoryScale);

const RealTime = () => {
  const [realTimeData, setRealTimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Real-time Data',
        fill: false,
        lineTension: 0.1,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
        // ... other dataset configurations
        data: [],
      },
    ],
  });

  const chartRef = useRef(null);

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
            console.log(lastValue);
            // Update chart data
            if (lastValue.value !== undefined) {
              setChartData((prevData) => ({
                labels: [...prevData.labels, lastValue.timestamp],
                datasets: [
                  {
                    ...prevData.datasets[0],
                    data: [...prevData.datasets[0].data, lastValue.value],
                  },
                ],
              }));
            }

            setRealTimeData(lastValue);
          } else {
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

    return () => {
      // Cleanup: Unsubscribe from Firebase updates when the component unmounts
      const ref = firebase.database().ref('/energydata');
      ref.off('value');
    };
  }, []);

  useEffect(() => {
    // Create or update the chart when chartData changes
    if (chartRef.current && chartData.datasets[0].data.length > 0) {
      chartRef.current.data = chartData;
      chartRef.current.update();
    }
  }, [chartData]);

  return (
    <div>
      <h1>Real-time Data</h1>
      {error && <p>Error: {error}</p>}
      {true && (<div>
        <Line
          ref={chartRef}
          data={chartData}
          options={{
            scales: {
              x: {
                type: 'category',
                labels: chartData.labels,
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Value',
                },
              },
            },
          }}
        />
      </div>)}
    </div>
  );
};

export default RealTime;