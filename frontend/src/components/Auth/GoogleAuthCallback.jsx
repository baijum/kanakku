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
        // Parse the URL search params to get the token
        const params = new URLSearchParams(location.search);
        const token = params.get('token');

        if (!token) {
          setError('No authentication token received from Google');
          setLoading(false);
          return;
        }

        // Store the token
        localStorage.setItem('token', token);
        
        // Update login state
        setIsLoggedIn(true);
        
        // Dispatch storage event for other tabs
        window.dispatchEvent(new Event('storage'));
        
        // Redirect to the dashboard
        navigate('/');
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