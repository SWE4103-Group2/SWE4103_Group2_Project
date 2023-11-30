import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js';

Chart.register(LineElement, PointElement, LinearScale, CategoryScale);

const RealTime = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: {},
  });

  const chartRefs = useRef({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('https://127.0.1:5000/real-time', { withCredentials: true });
        const newData = response.data.slice(0, 4);

        // Update chart data
        setChartData((prevData) => {
          const updatedDatasets = { ...prevData.datasets };

          newData.forEach((data) => {
            if (!updatedDatasets[data.serialnum]) {
              updatedDatasets[data.serialnum] = {
                label: `Real-time Data ${data.serialnum}`,
                fill: false,
                lineTension: 0.1,
                backgroundColor: `rgba(75,192,192,0.4)`,
                borderColor: `rgba(75,192,192,1)`,
                data: [],
              };
            }

            updatedDatasets[data.serialnum].data.push(data.value);
          });

          return {
            labels: [...prevData.labels, newData[0]?.timestamp],
            datasets: updatedDatasets,
          };
        });
      } catch (error) {
        console.error('Error fetching data from server:', error);
      }
    };

    // Fetch data initially
    fetchData();

    // Set up a timer to fetch data every 5 seconds (adjust as needed)
    const intervalId = setInterval(fetchData, 5000);

    // Clean up the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    // Create or update the charts when chartData changes
    if (chartRefs.current && chartData.labels.length > 0) {
      Object.keys(chartData.datasets).forEach((serialnum) => {
        if (!chartRefs.current[serialnum]) {
          chartRefs.current[serialnum] = React.createRef();
        }
        
        if (chartRefs.current[serialnum].current) {
          chartRefs.current[serialnum].current.data = {
            labels: chartData.labels,
            datasets: [chartData.datasets[serialnum]],
          };
          chartRefs.current[serialnum].current.update();
        }
      });
    }
  }, [chartData]);

  return (
    <div>
      <h1>Real-time Data</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
        {Object.keys(chartData.datasets).map((serialnum) => (
          <div key={serialnum}>
            <h2>{serialnum}</h2>
            <Line
              ref={chartRefs.current[serialnum]}
              data={{ labels: chartData.labels, datasets: [chartData.datasets[serialnum]] }}
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
              height={100}
              width={200}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default RealTime;