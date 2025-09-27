import React, { useState } from 'react';
import { Button, TextField } from '@mui/material';
import axios from 'axios';

interface OrderOperationScreenProps {
  orderId: number;
}

const OrderOperationScreen: React.FC<OrderOperationScreenProps> = ({ orderId }) => {
  const [operationType, setOperationType] = useState('');
  const [updatedInfo, setUpdatedInfo] = useState('');
  const [operationResult, setOperationResult] = useState('');

  const handleOperationTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setOperationType(event.target.value);
  };

  const handleUpdatedInfoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUpdatedInfo(event.target.value);
  };

  const handleGetOperationInfo = async () => {
    try {
      const response = await axios.get(`/api/orders/${orderId}/operationInfo`, {
        params: {
          operationType,
          updatedInfo
        }
      });
      setOperationResult(response.data);
    } catch (error) {
      setOperationResult('Error fetching operation info');
      console.error(error);
    }
  };

  return (
    <div>
      <TextField
        label="Operation Type"
        value={operationType}
        onChange={handleOperationTypeChange}
      />
      <TextField
        label="Updated Info"
        value={updatedInfo}
        onChange={handleUpdatedInfoChange}
      />
      <Button variant="contained" onClick={handleGetOperationInfo}>
        Get Operation Info
      </Button>
      <div>{operationResult}</div>
    </div>
  );
};

export default OrderOperationScreen;