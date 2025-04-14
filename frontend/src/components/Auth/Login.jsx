import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link, Divider } from '@mui/material';
import axios from 'axios'; // Assuming axios is used
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom'; // To redirect after login
import GoogleIcon from '@mui/icons-material/Google';

function Login({ setIsLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
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

    if (!email || !password) {
      setError('Email and Password are required.');
      setLoading(false);
      return;
    }

    try {
      // Use relative URL path to leverage the proxy
      const response = await axios({
        method: 'post',
        url: '/api/auth/login',
        data: {
          email,
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

  const handleGoogleLogin = async () => {
    setError('');
    setGoogleLoading(true);
    
    try {
      const response = await axios.get('/api/auth/google');
      
      if (response.data && response.data.auth_url) {
        // Redirect to Google's authentication page
        window.location.href = response.data.auth_url;
      } else {
        setError('Failed to start Google authentication');
        setGoogleLoading(false);
      }
    } catch (err) {
      console.error("Google login error:", err);
      setError(err.response?.data?.error || err.message || 'Failed to start Google authentication');
      setGoogleLoading(false);
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
          id="email"
          label="Email"
          name="email"
          autoComplete="email"
          autoFocus
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          color="primary"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Log In'}
        </Button>
        
        <Divider sx={{ my: 2 }}>or</Divider>
        
        <Button
          fullWidth
          variant="outlined"
          startIcon={<GoogleIcon />}
          onClick={handleGoogleLogin}
          disabled={loading || googleLoading}
          sx={{ mb: 2 }}
        >
          {googleLoading ? <CircularProgress size={24} /> : 'Sign in with Google'}
        </Button>
        
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Box sx={{ mb: 1 }}>
            <Link component={RouterLink} to="/forgot-password" variant="body2">
              Forgot Password?
            </Link>
          </Box>
          <Box>
            Don't have an account?{' '}
            <Link component={RouterLink} to="/register" variant="body2">
              Sign Up
            </Link>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default Login; 