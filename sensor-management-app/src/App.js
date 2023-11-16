import './App.css';
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './Navigation';
import MainContent from './MainContent';

function App() {
  return (
    <div className="App">
      <Router>
      <Navigation />
        <Routes>
          <Route path="/" element={<MainContent />} />
          <Route path="/historical" element={<MainContent showHistorical={true} />} />
          <Route path="/real-time" element={<MainContent showRT={true} />} />
          <Route path="/analytics" element={<MainContent showAnalytics={true} />} />
          <Route path="/reports" element={<MainContent showReports={true} />} />
          <Route path="/sensors" element={<MainContent showSensors={true} />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
