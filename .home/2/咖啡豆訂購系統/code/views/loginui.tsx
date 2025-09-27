import React, { useState } from 'react';
import { TextField, Button, Typography } from '@mui/material';
import axios from 'axios';

interface LoginUIProps {
  onLoginSuccess: (token: string) => void;
}

const LoginUI: React.FC<LoginUIProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('/auth/login', { username, password });
      const token = response.data.token;
      onLoginSuccess(token);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Typography variant="h4" gutterBottom>Login</Typography>
      <TextField
        label="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        margin="normal"
        required
        fullWidth
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        margin="normal"
        required
        fullWidth
      />
      {error && <Typography color="error">{error}</Typography>}
      <Button type="submit" variant="contained" color="primary" fullWidth>Login</Button>
    </form>
  );
};

export default LoginUI;

import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import axios from 'axios';

interface LoginUIProps {
  onLoginSuccess: (token: string) => void;
}

const LoginUI: React.FC<LoginUIProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const getLoginInfo = async () => {
    try {
      const response = await axios.post('/api/auth/login', { username, password });
      const token = response.data.token;
      onLoginSuccess(token);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', width: 300, margin: 'auto', marginTop: '100px' }}>
      <TextField
        label="Username"
        variant="outlined"
        margin="normal"
        fullWidth
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <TextField
        label="Password"
        type="password"
        variant="outlined"
        margin="normal"
        fullWidth
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button variant="contained" onClick={getLoginInfo} fullWidth>Login</Button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </Box>
  );
};

export default LoginUI;

import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import axios from 'axios';

interface LoginUIProps {
  onLoginSuccess: (token: string) => void;
}

const LoginUI: React.FC<LoginUIProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const getLoginInfo = async () => {
    try {
      const response = await axios.post('/api/auth/login', { username, password });
      const token = response.data.token;
      onLoginSuccess(token);
    } catch (error: any) {
      setError(error.response?.data?.message || 'Login failed');
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <TextField
        label="Username"
        variant="outlined"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <TextField
        label="Password"
        type="password"
        variant="outlined"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button variant="contained" onClick={getLoginInfo}>Login</Button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </Box>
  );
};

export default LoginUI;