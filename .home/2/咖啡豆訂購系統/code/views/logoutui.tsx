import React from 'react';
import { useDispatch } from 'react-redux';
import { logout } from '../store/authSlice'; // Assuming you have a Redux slice for authentication

interface LogoutUIProps {}

const LogoutUI: React.FC<LogoutUIProps> = () => {
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <button onClick={handleLogout}>Logout</button>
  );
};

export default LogoutUI;