import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, CircularProgress, Alert, Link } from '@mui/material';
import axiosInstance from '../../api/axiosInstance';
import { Link as RouterLink, useParams, useNavigate, useLocation } from 'react-router-dom';

function ResetPassword() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');

  useEffect(() => {
    // Extract email from query parameters
    const params = new URLSearchParams(location.search);
    const emailParam = params.get('email');
    if (emailParam) {
      setEmail(emailParam);
    }
  }, [location.search]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!newPassword || !confirmPassword) {
      setError('Both fields are required.');
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      setLoading(false);
      return;
    }

    try {
      const response = await axiosInstance({
        method: 'post',
        url: '/api/v1/auth/reset-password',
        data: {
          email,
          token,
          new_password: newPassword,
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Reset password response:', response);
      setSuccess('Your password has been reset successfully.');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login', { 
          state: { 
            notification: { 
              type: 'success', 
              message: 'Password reset successful. You can now log in with your new password.' 
            } 
          } 
        });
      }, 3000);
    } catch (err) {
      console.error('Error resetting password:', err);
      setError(err.response?.data?.error || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  if (!token || !email) {
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
          Invalid Reset Link
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          The password reset link is invalid or has expired.
        </Alert>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Link component={RouterLink} to="/forgot-password" variant="body2">
            Request a new password reset
          </Link>
        </Box>
      </Box>
    );
  }

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
        Reset Password
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
          label="New Password"
          type="password"
          margin="normal"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <TextField
          fullWidth
          label="Confirm New Password"
          type="password"
          margin="normal"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
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
          {loading ? <CircularProgress size={24} /> : 'Reset Password'}
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

export default ResetPassword; 