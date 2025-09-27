import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, TextField, Typography } from '@mui/material';

interface OrderQueryUIProps {
  orderID: string;
  customerID: string;
}

const OrderQueryUI: React.FC<OrderQueryUIProps> = ({ orderID, customerID }) => {
  const [orderStatus, setOrderStatus] = useState('');

  useEffect(() => {
    const fetchOrderStatus = async () => {
      try {
        const response = await axios.get(`/api/orders/${orderID}/status`);
        setOrderStatus(response.data.orderStatus);
      } catch (error) {
        console.error('Error fetching order status:', error);
        setOrderStatus('Error fetching status');
      }
    };

    if (orderID) {
      fetchOrderStatus();
    }
  }, [orderID]);

  const getOrderID = (): string => orderID;
  const getCustomerID = (): string => customerID;
  const displayOrderStatus = (status: string): void => setOrderStatus(status);


  return (
    <div>
      <Typography variant="h6">Order Details</Typography>
      <TextField label="Order ID" value={getOrderID()} disabled />
      <TextField label="Customer ID" value={getCustomerID()} disabled />
      <Typography variant="body1">Order Status: {orderStatus}</Typography>
      {/* Add more UI elements as needed */}
    </div>
  );
};

export default OrderQueryUI;