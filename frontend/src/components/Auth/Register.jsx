import React, { useState } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link } from '@mui/material';
import axios from 'axios';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

function Register({ setIsLoggedIn }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!username || !email || !password || !confirmPassword) {
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
      const response = await axios({
        method: 'post',
        url: '/api/auth/register',
        data: {
          username,
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
          
          // Navigate to dashboard
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
          id="email"
          label="Email Address"
          name="email"
          autoComplete="email"
          type="email"
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
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Register'}
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