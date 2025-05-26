import React, { useState } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link } from '@mui/material';
import axiosInstance from '../../api/axiosInstance';
import { Link as RouterLink } from 'react-router-dom';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!email) {
      setError('Email is required.');
      setLoading(false);
      return;
    }

    try {
      const response = await axiosInstance({
        method: 'post',
        url: '/api/v1/auth/forgot-password',
        data: { email },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Forgot password response:', response);
      setSuccess('If your email is registered, you will receive a password reset link.');
    } catch (err) {
      console.error('Error requesting password reset:', err);
      setError(err.response?.data?.error || 'Failed to process your request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: 400,
        mx: 'auto',
        p: 3,
        mt: 4,
        boxShadow: 3,
        borderRadius: 2,
        bgcolor: 'background.paper',
      }}
    >
      <Typography variant="h5" component="h1" gutterBottom align="center">
        Forgot Password
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Email"
          type="email"
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Send Reset Link'}
        </Button>
      </form>

      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Link component={RouterLink} to="/login" variant="body2">
          Back to Login
        </Link>
      </Box>
    </Box>
  );
}

export default ForgotPassword;
