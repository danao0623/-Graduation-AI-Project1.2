import React, { useState } from 'react';
import { TextField, Button, Typography } from '@mui/material';
import axios from 'axios';

interface OrderQueryScreenProps {
}

const OrderQueryScreen: React.FC<OrderQueryScreenProps> = () => {
  const [orderNumber, setOrderNumber] = useState('');
  const [customerInfo, setCustomerInfo] = useState('');
  const [queryResult, setQueryResult] = useState('');

  const getOrderQueryInfo = async () => {
    try {
      const response = await axios.post('/api/order/query', { orderNumber, customerInfo });
      setQueryResult(response.data);
    } catch (error) {
      setQueryResult('Error fetching order information.');
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>Order Query</Typography>
      <TextField
        label="Order Number"
        value={orderNumber}
        onChange={(e) => setOrderNumber(e.target.value)}
      />
      <TextField
        label="Customer Info"
        value={customerInfo}
        onChange={(e) => setCustomerInfo(e.target.value)}
      />
      <Button variant="contained" onClick={getOrderQueryInfo}>Query</Button>
      <Typography variant="body1" gutterBottom>{queryResult}</Typography>
    </div>
  );
};

export default OrderQueryScreen;