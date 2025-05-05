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
        console.log('Google Auth Callback - Full URL:', window.location.href);
        
        // Parse the URL search params to get the token
        const params = new URLSearchParams(location.search);
        const token = params.get('token');
        const errorParam = params.get('error');
        
        // Check for error parameter 
        if (errorParam) {
          console.log('Google Auth Callback - Error received:', errorParam);
          // Redirect to login page with the error parameter
          navigate(`/login?error=${errorParam}`);
          return;
        }
        
        console.log('Google Auth Callback - Token present:', !!token);
        console.log('Google Auth Callback - Token length:', token ? token.length : 0);

        if (!token) {
          setError('No authentication token received from Google');
          setLoading(false);
          return;
        }

        // Store the token first
        console.log('Storing token in localStorage');
        localStorage.removeItem('token'); // Clear any existing token
        localStorage.setItem('token', token);
        
        // Verify token was properly stored
        const storedToken = localStorage.getItem('token');
        console.log('Token stored successfully:', !!storedToken);
        console.log('Stored token matches original:', storedToken === token);
        
        // Update login state
        console.log('Setting isLoggedIn state to true');
        setIsLoggedIn(true);
        
        // Dispatch storage event for other tabs
        console.log('Dispatching storage event');
        window.dispatchEvent(new Event('storage'));
        
        // Small delay to ensure state is updated before redirect
        console.log('Preparing for redirect to dashboard...');
        setTimeout(() => {
          // Redirect to the dashboard with a full page reload
          console.log('Navigating to dashboard with full reload');
          window.location.href = '/';
        }, 300);
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