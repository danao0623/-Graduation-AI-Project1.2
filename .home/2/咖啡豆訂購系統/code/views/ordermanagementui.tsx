import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Order } from './Order'; // Assuming Order interface is defined elsewhere

interface OrderManagementUIProps {
  orderID: string;
}

const OrderManagementUI: React.FC<OrderManagementUIProps> = ({ orderID }) => {
  const [order, setOrder] = useState<Order | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await axios.get(`/api/orders/${orderID}`); // Adjust API endpoint as needed
        setOrder(response.data);
      } catch (error) {
        setMessage('Error fetching order information.');
      }
    };

    if (orderID) {
      fetchOrder();
    }
  }, [orderID]);

  const handleDisplayOrder = () => {
    if (order) {
      // Display order details using Material UI components
      console.log("Order details:", order);
    } else {
      setMessage('No order information available.');
    }
  };

  return (
    <div>
      <h1>Order Management UI</h1>
      <button onClick={handleDisplayOrder}>Display Order</button>
      {message && <p>{message}</p>}
      {order && (
        <div>
          {/* Display order details here using Material UI components */}
          <p>Order ID: {order.orderID}</p>
          {/* ... other order details ... */}
        </div>
      )}
    </div>
  );
};

export default OrderManagementUI;