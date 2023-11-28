import './App.css';
import React, { useState, createContext, useEffect, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import MainContent from './MainContent';
import Navigation from './Navigation';

// Create a context for managing authentication state
export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [isAuthenticated, setAuthenticated] = useState(false);
  const [accountType, setAccountType] = useState('');

  useEffect(() => {
    // Check local storage for authentication status on component mount
    const storedAuth = localStorage.getItem('isAuthenticated');
    const storedAcc = localStorage.getItem('accountType');
    if (storedAuth && storedAcc) {
      setAuthenticated(JSON.parse(storedAuth));
      setAccountType(JSON.parse(storedAcc));
    }
  }, []);

  const login = (account) => {
    // Authentication logic here (e.g., check user credentials)
    // For simplicity, let's assume successful authentication
    setAuthenticated(true);
    setAccountType(account);
    // Save authentication status to local storage
    localStorage.setItem('isAuthenticated', JSON.stringify(true));
    localStorage.setItem('accountType', JSON.stringify(account));
  };

  const logout = () => {
    // Log the user out (e.g., clear tokens or session data)
    setAuthenticated(false);
    // Save authentication status to local storage
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('accountType');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, accountType, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const PrivateRoute = ({ element, page }) => {
  const { isAuthenticated } = useContext(AuthContext);

  if (page) {
    return isAuthenticated ? element : <LoginPage />
  }
  return isAuthenticated ? element : <Navigate to="/login" />;
};

const App = () => {  
  return (
    <Router>
      <AuthProvider>
        {<PrivateRoute element={<Navigation />} />}
        <Routes>
          <Route
            path="/login"
            element={<PrivateRoute element={<MainContent />} page/>}
          />
          <Route
            path="/sensors/:sensorid?"
            element={<PrivateRoute element={<MainContent showSensors={true} />} />}
          />
          <Route path="/:show?" element={<PrivateRoute element={<MainContent />} />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
