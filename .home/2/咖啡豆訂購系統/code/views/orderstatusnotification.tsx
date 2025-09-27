import React from 'react';
import { useDispatch } from 'react-redux';
import { AxiosResponse } from 'axios';

interface OrderStatusNotification {
  message: string;
  customerEmail: string;
}

const useOrderStatusNotification = () => {
  const dispatch = useDispatch();

  const sendOrderStatusNotification = async (notification: OrderStatusNotification): Promise<AxiosResponse<any>> => {
    try {
      const response = await axios.post('/api/notifications', notification);
      return response;
    } catch (error) {
      console.error("Error sending notification:", error);
      throw error;
    }
  };

  return { sendOrderStatusNotification };
};

export default useOrderStatusNotification;

//This is a placeholder,  actual implementation requires backend API and axios setup.  Replace '/api/notifications' with your actual API endpoint.
const axios = {
  post: async (url: string, data: any) => {
    return {data: {status: 'success'}};
  }
};