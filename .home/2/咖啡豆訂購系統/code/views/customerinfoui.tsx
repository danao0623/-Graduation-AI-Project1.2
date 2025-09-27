import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface CustomerInfo {
  customerID: string;
  customerInfo: string;
}

const CustomerInfoUI: React.FC = () => {
  const [customerID, setCustomerID] = useState('');
  const [customerInfo, setCustomerInfo] = useState('');
  const [error, setError] = useState('');

  const getCustomerInfo = async () => {
    try {
      const response = await axios.get(`/api/customers/${customerID}`);
      setCustomerInfo(response.data.customerInfo);
      setError('');
    } catch (error: any) {
      setError(error.response ? error.response.data.message : 'Failed to fetch customer info');
    }
  };

  const handleCustomerIDChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCustomerID(event.target.value);
  };

  useEffect(() => {
    if (customerID) {
      getCustomerInfo();
    }
  }, [customerID]);


  return (
    <div>
      <input type="text" value={customerID} onChange={handleCustomerIDChange} placeholder="Enter Customer ID" />
      <button onClick={getCustomerInfo}>Get Customer Info</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <div>{customerInfo}</div>
    </div>
  );
};

export default CustomerInfoUI;