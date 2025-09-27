import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import axios from 'axios';

interface LocationService {
  latitude: number;
  longitude: number;
  requestLocationAuthorization(): boolean;
  getLocation(): { latitude: number; longitude: number };
}


const useLocation = (): LocationService => {
  const [location, setLocation] = useState<{ latitude: number; longitude: number }>({ latitude: 0, longitude: 0 });
  const dispatch = useDispatch();


  const requestLocationAuthorization = (): boolean => {
    // Implement location authorization logic here.  This would likely involve browser APIs.
    //  For this example, we'll simulate success.
    return true;
  };

  const getLocation = async (): Promise<{ latitude: number; longitude: number }> => {
    if (navigator.geolocation) {
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setLocation({ latitude: position.coords.latitude, longitude: position.coords.longitude });
            resolve({ latitude: position.coords.latitude, longitude: position.coords.longitude });
          },
          (error) => {
            console.error("Error getting location:", error);
            reject(error);
          }
        );
      });
    } else {
      console.error("Geolocation is not supported by this browser.");
      return { latitude: 0, longitude: 0 };
    }
  };


  return {
    latitude: location.latitude,
    longitude: location.longitude,
    requestLocationAuthorization,
    getLocation,
  };
};

export default useLocation;