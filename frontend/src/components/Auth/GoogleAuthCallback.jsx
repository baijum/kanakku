import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box, Typography, Alert } from '@mui/material';

function GoogleAuthCallback({ setIsLoggedIn }) {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('Google Auth Callback - Location:', location);
        // Parse the URL search params to get the token
        const params = new URLSearchParams(location.search);
        const token = params.get('token');
        
        console.log('Google Auth Callback - Token present:', !!token);

        if (!token) {
          setError('No authentication token received from Google');
          setLoading(false);
          return;
        }

        // Store the token
        console.log('Storing token in localStorage');
        localStorage.setItem('token', token);
        console.log('Token stored successfully:', !!localStorage.getItem('token'));
        
        // Update login state
        console.log('Setting isLoggedIn state to true');
        setIsLoggedIn(true);
        
        // Dispatch storage event for other tabs
        console.log('Dispatching storage event');
        window.dispatchEvent(new Event('storage'));
        
        // Redirect to the dashboard with a full page reload
        console.log('Navigating to dashboard with full reload');
        window.location.href = '/';
      } catch (err) {
        console.error('Error processing Google authentication:', err);
        setError('Failed to complete Google authentication');
        setLoading(false);
      }
    };

    handleCallback();
  }, [location, navigate, setIsLoggedIn]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Completing authentication...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          p: 3,
        }}
      >
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Typography>
          <a href="/login">Return to login</a>
        </Typography>
      </Box>
    );
  }

  return null;
}

export default GoogleAuthCallback; 