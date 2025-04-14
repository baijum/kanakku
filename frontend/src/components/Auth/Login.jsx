import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link } from '@mui/material';
import axios from 'axios'; // Assuming axios is used
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom'; // To redirect after login

function Login({ setIsLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Check for success notification from registration
  useEffect(() => {
    if (location.state?.notification) {
      const { type, message } = location.state.notification;
      if (type === 'success') {
        setSuccess(message);
      }
      // Clear the location state after using it
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location, navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    if (!username || !password) {
      setError('Username and Password are required.');
      setLoading(false);
      return;
    }

    try {
      // Use relative URL path to leverage the proxy
      const response = await axios({
        method: 'post',
        url: '/api/auth/login',
        data: {
          username,
          password,
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Login response:', response);

      // Assuming the backend returns a token upon successful login
      if (response.data && response.data.token) {
        try {
          // Log the token format for debugging
          console.log('Token received:', response.data.token);
          
          // Store the token
          localStorage.setItem('token', response.data.token);
          console.log('Token stored in localStorage:', localStorage.getItem('token'));
          
          // Set login state directly
          setIsLoggedIn(true);
          
          // Also dispatch storage event for other tabs
          window.dispatchEvent(new Event('storage'));
          console.log('Storage event dispatched');
          
          console.log('Navigating to dashboard...');
          // Use React Router navigation instead of window.location
          navigate('/');
        } catch (storageError) {
          console.error('Error storing token:', storageError);
          setError('Error completing login. Please try again.');
        }
      } else {
        console.error('Invalid response format:', response.data);
        setError('Login failed. Invalid response from server.');
      }
    } catch (err) {
      console.error("Login error:", err);
      console.error("Error response:", err.response);
      console.error("Error request:", err.request);
      setError(err.response?.data?.error || err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        marginTop: 8,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        p: 3,
      }}
    >
      <Typography component="h1" variant="h5">
        Sign in
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1, width: '100%', maxWidth: '400px' }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="username"
          label="Username"
          name="username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={loading}
        />
        <TextField
          margin="normal"
          required
          fullWidth
          name="password"
          label="Password"
          type="password"
          id="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
        />
        {error && (
          <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mt: 2, width: '100%' }}>
            {success}
          </Alert>
        )}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Sign In'}
        </Button>
        <Box textAlign="center">
          <Link component={RouterLink} to="/register" variant="body2">
            Don't have an account? Register
          </Link>
        </Box>
      </Box>
    </Box>
  );
}

export default Login; 