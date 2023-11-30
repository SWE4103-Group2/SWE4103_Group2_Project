import { useContext } from 'react';
import { AuthContext } from './App';

const useAuthorization = (allowedAccounts) => {
  const { isAuthenticated, accountType } = useContext(AuthContext);

  if (!isAuthenticated) {
    // Redirect to the login page if not authenticated
    return '/login';
  }

  if (!allowedAccounts.includes(accountType)) {
    // Redirect or handle unauthorized access
    return '/unauthorized';
  }

  // Return null if authorized
  return null;
};

export default useAuthorization;