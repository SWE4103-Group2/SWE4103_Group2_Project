import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTable, useFilters, useSortBy } from 'react-table';
import Select from 'react-select';
import './Historical.css'

const Historical = () => {
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStart, setFilterStart] = useState(null);
  const [filterEnd, setFilterEnd] = useState(null);
  const [selectedSensors, setSelectedSensors] = useState([]);
  const [data, setData] = useState([]);

  useEffect(() => {
      // Fetch sensor data from Flask backend
      axios.get('https://127.0.0.1:5000/historical', { withCredentials: true })
        .then(response => {
          setHistoricalData(Object.values(response.data));
          setData(Object.values(response.data));
          setLoading(false);
        })
        .catch(error => {
          console.error('Error fetching sensors:', error);
          setLoading(false);
        });
  }, []);

  const handleFilter = () => {
    setLoading(true);
  
    // Filter the data based on the start and end dates
    const filteredData = historicalData.filter(entry => {
      const entryDate = new Date(entry.timestamp);
      entryDate.setHours(0,0,0,0);
      const startFilterDate = filterStart ? new Date(filterStart + 'T00:00:00') : null;
      const endFilterDate = filterEnd ? new Date(filterEnd + 'T00:00:00') : null;
  
      if ((startFilterDate && entryDate < startFilterDate) || (endFilterDate && entryDate > endFilterDate)) {
        return false;
      }

      // Check selected sensors
      if (selectedSensors.length > 0 && !selectedSensors.includes(entry.serialnum)) {
        return false;
      }
  
      return true;
    });
  
    setData(filteredData);
    setLoading(false);
  };

  const handleDownloadCSV = () => {
    // Convert the data to CSV format
    const csvData = [
      ['ID', 'Timestamp', 'Value'],
      ...data.map(entry => [entry.serialnum, entry.timestamp, entry.value]),
    ];

    // Create a CSV file
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'historical_data.csv';
    link.click();
  };

  const columns = React.useMemo(
    () => [
      {
        Header: 'ID',
        accessor: 'serialnum',
      },
      {
        Header: 'Timestamp',
        accessor: 'timestamp',
      },
      {
        Header: 'Value',
        accessor: 'value',
      },
    ],
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state: { filters, sortBy },
  } = useTable(
    {
      columns,
      data,
    },
    useFilters, // Use the useFilters plugin
    useSortBy
  );

  const sensorOptions = Array.from(new Set(historicalData.map(entry => entry.serialnum))).map(sensorId => ({
    value: sensorId,
    label: sensorId,
  }));

  return (
    <div>
      <h2>Historical Data</h2>
      <br/>
      <label style={{ marginRight: '10px' }}>
        Start Date:
        <input
          type="date"
          value={filterStart || ''}
          onChange={(e) => setFilterStart(e.target.value)}
        />
      </label>
      <label>
        End Date:
        <input
          type="date"
          value={filterEnd || ''}
          onChange={(e) => setFilterEnd(e.target.value)}
        />
      </label>
      <br/>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <label>
          Sensors:
        </label>
        <Select
          isMulti
          options={sensorOptions}
          value={selectedSensors.map(sensorId => ({ value: sensorId, label: sensorId }))}
          onChange={selectedOptions => setSelectedSensors(selectedOptions.map(option => option.value))}
          placeholder="Select..."
          styles={{
            control: (styles) => ({ ...styles, minWidth: '650px' }),
          }}
        />
      </div>
      <button onClick={handleFilter}>Apply Filter</button>

      {loading && <p>Loading...</p>}
      {!loading && (
        <div>
          <br/>
          <button onClick={handleDownloadCSV}>Download CSV</button>
          <table {...getTableProps()}>
            <thead>
              {headerGroups.map(headerGroup => (
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map(column => (
                    <th
                      {...column.getHeaderProps(column.getSortByToggleProps())}
                      className={column.isSorted ? (column.isSortedDesc ? 'sort-desc' : 'sort-asc') : ''}
                    >
                      {column.render('Header')}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody {...getTableBodyProps()}>
              {rows.map(row => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()} key={row.id}>
                    {row.cells.map(cell => (
                      <td {...cell.getCellProps()} key={cell.column.id}>
                        {cell.render('Cell')}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Historical;