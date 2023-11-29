import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTable, useFilters, useSortBy } from 'react-table';
import './Historical.css'

const Historical = () => {
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStart, setFilterStart] = useState(null);
  const [filterEnd, setFilterEnd] = useState(null);
  const [data, setData] = useState([]);

  useEffect(() => {
      // Fetch sensor data from Flask backend
      axios.get('http://127.0.0.1:5000/historical', { withCredentials: true })
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
  
      if (startFilterDate && entryDate < startFilterDate) {
        return false;
      }
  
      if (endFilterDate && entryDate > endFilterDate) {
        return false;
      }
  
      return true;
    });
  
    setData(filteredData);
    setLoading(false);
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

  return (
    <div>
      <h2>Historical Data</h2>
      <label>
        Filter Start Date:
        <input
          type="date"
          value={filterStart || ''}
          onChange={(e) => setFilterStart(e.target.value)}
        />
      </label>
      <label>
        Filter End Date:
        <input
          type="date"
          value={filterEnd || ''}
          onChange={(e) => setFilterEnd(e.target.value)}
        />
      </label>
      <button onClick={handleFilter}>Apply Filter</button>

      {loading && <p>Loading...</p>}
      {!loading && (
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
                <tr {...row.getRowProps()}>
                  {row.cells.map(cell => (
                    <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Historical;