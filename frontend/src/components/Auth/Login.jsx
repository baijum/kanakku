import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link, Divider } from '@mui/material';
import axiosInstance from '../../api/axiosInstance';
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
    
    // Check for account_inactive error in URL parameters
    const params = new URLSearchParams(location.search);
    const errorParam = params.get('error');
    
    if (errorParam === 'account_inactive') {
      setError('Your account is inactive. Please use the Account Status tab in Profile Settings to reactivate it.');
      // Remove the error parameter from URL to prevent showing the error after page refresh
      navigate(location.pathname, { replace: true });
    }
  }, [location, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Use axiosInstance for regular login
      const response = await axiosInstance({
        method: 'post',
        url: '/api/v1/auth/login',
        data: {
          email,
          password,
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Store the token and set login state
      localStorage.setItem('token', response.data.token);
      setIsLoggedIn(true);
      navigate('/');
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
      // Use the proxy configuration instead of direct backend URL
      console.log('Sending Google auth request via proxy...');
      
      // Using axiosInstance instead of direct axios
      const response = await axiosInstance.get('/api/v1/auth/google');
      
      if (response.data && response.data.auth_url) {
        // Redirect to Google's authentication page
        console.log(`Redirecting to Google auth URL: ${response.data.auth_url}`);
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
      <Box component="form" onSubmit={handleLogin} noValidate sx={{ mt: 1, width: '100%', maxWidth: '400px' }}>
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