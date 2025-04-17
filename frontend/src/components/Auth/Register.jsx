import React, { useState } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link, Divider } from '@mui/material';
import axiosInstance from '../../api/axiosInstance';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import GoogleIcon from '@mui/icons-material/Google';

function Register({ setIsLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!email || !password || !confirmPassword) {
      setError('All fields are required.');
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    try {
      const response = await axiosInstance({
        method: 'post',
        url: '/api/v1/auth/register',
        data: {
          email,
          password,
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Registration response:', response);

      if (response.data && response.data.token) {
        try {
          // Store the token
          localStorage.setItem('token', response.data.token);
          
          // Set login state directly
          setIsLoggedIn(true);
          
          // Also dispatch storage event for other tabs
          window.dispatchEvent(new Event('storage'));
          
          // Use React Router navigation
          navigate('/');
        } catch (storageError) {
          console.error('Error storing token:', storageError);
          setError('Error completing registration. Please try again.');
        }
      } else if (response.data && response.data.message) {
        // New flow: Registration succeeded but user needs activation
        setError('');
        // Navigate to login with success message
        navigate('/login', { 
          state: { 
            notification: {
              type: 'success',
              message: response.data.message
            }
          }
        });
      } else {
        console.error('Invalid response format:', response.data);
        setError('Registration failed. Invalid response from server.');
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError(err.response?.data?.error || err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError('');
    setGoogleLoading(true);
    
    try {
      const response = await axiosInstance.get('/api/v1/auth/google');
      
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
        Register
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1, width: '100%', maxWidth: '400px' }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="email"
          label="Email Address"
          name="email"
          autoComplete="email"
          type="email"
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
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
        />
        <TextField
          margin="normal"
          required
          fullWidth
          name="confirmPassword"
          label="Confirm Password"
          type="password"
          id="confirmPassword"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          disabled={loading}
        />
        {error && (
          <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
            {error}
          </Alert>
        )}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading || googleLoading}
        >
          {loading ? <CircularProgress size={24} /> : 'Register'}
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
          {googleLoading ? <CircularProgress size={24} /> : 'Sign up with Google'}
        </Button>
        
        <Box textAlign="center">
          <Link component={RouterLink} to="/login" variant="body2">
            Already have an account? Sign in
          </Link>
        </Box>
      </Box>
    </Box>
  );
}

export default Register; 