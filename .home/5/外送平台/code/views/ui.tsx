import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { getOrder } from './orderSlice'; // Assuming you have a Redux slice for order management
import { Button } from '@mui/material';

interface Order {
  orderID: string;
  // ... other order properties
}

const UI: React.FC = () => {
  const [orderID, setOrderID] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const dispatch = useDispatch();

  useEffect(() => {
    const id = localStorage.getItem('orderID');
    if (id) {
      setOrderID(id);
      dispatch(getOrder(id));
    }
  }, [dispatch]);

  const displayOrderInformation = (order: Order) => {
    // Display order information using Material UI components
    console.log('Order Information:', order);
  };

  const displayErrorMessage = (message: string) => {
    setErrorMessage(message);
    // Display error message using Material UI components
    console.error('Error:', message);
  };

  const getOrderID = () => {
    return orderID;
  };

  const refreshPage = () => {
    window.location.reload();
  };

  const handleGetOrder = () => {
    const id = getOrderID();
    if (id) {
      dispatch(getOrder(id))
        .then((res) => {
          if (res.payload) {
            displayOrderInformation(res.payload);
          } else {
            displayErrorMessage('Failed to retrieve order information.');
          }
        })
        .catch((error) => {
          displayErrorMessage(`Error: ${error.message}`);
        });
    } else {
      displayErrorMessage('Please provide an order ID.');
    }
  };


  return (
    <div>
      <Button variant="contained" onClick={handleGetOrder}>Get Order</Button>
      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
      {/* Display order information here */}
    </div>
  );
};

export default UI;