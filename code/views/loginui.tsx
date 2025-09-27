```tsx
import React, { useState } from 'react';

interface LoginUIProps {
  onLoginSuccess: () => void;
  onLoginFailure: () => void;
}

const LoginUI: React.FC<LoginUIProps> = ({ onLoginSuccess, onLoginFailure }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const getUsername = (): string => username;
  const getPassword = (): string => password;
  const displayLoginSuccess = (): void => onLoginSuccess();
  const displayLoginFailure = (): void => onLoginFailure();


  const handleLogin = async () => {
    try {
      //  Replace with actual login logic.  This is a placeholder.
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        displayLoginSuccess();
      } else {
        displayLoginFailure();
      }
    } catch (error) {
      displayLoginFailure();
      console.error("Login failed:", error);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default LoginUI;

```tsx
import React, { useState } from 'react';

interface LoginUIProps {
  onLoginSuccess: () => void;
  onLoginFailure: (message: string) => void;
}

const LoginUI: React.FC<LoginUIProps> = ({ onLoginSuccess, onLoginFailure }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const getUsername = () => username;
  const getPassword = () => password;

  const handleLogin = async () => {
    try {
      //  Replace with actual login API call
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        onLoginFailure(errorData.message || 'Login failed');
      } else {
        onLoginSuccess();
      }
    } catch (error) {
      onLoginFailure('An unexpected error occurred');
    }
  };

  const displayLoginSuccess = () => {
    //Implement success display logic here.
    alert("Login Successful!");
  };

  const displayLoginFailure = (message: string) => {
    //Implement failure display logic here.
    alert(`Login Failed: ${message}`);
  };


  return (
    <div>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default LoginUI;