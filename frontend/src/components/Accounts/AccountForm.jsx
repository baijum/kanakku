import React, { useState } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
// import axios from 'axios'; // Assuming axios is used for API calls
import axiosInstance from '../../api/axiosInstance'; // Import the configured instance

function AccountForm() {
  const [accountName, setAccountName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!accountName) {
      setError('Account Name is required.');
      return;
    }

    const newAccount = {
      name: accountName,
      description: description,
    };

    try {
      const token = localStorage.getItem('token');

      // Use axiosInstance and add Authorization header
      const response = await axiosInstance.post('/api/v1/accounts', newAccount, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json' // Axios usually sets this, but good to be explicit
        }
      });

      if (response.status === 201) {
        setSuccess(`Account '${accountName}' created successfully!`);
        // Clear the form
        setAccountName('');
        setDescription('');
        // Optionally: trigger a refresh of an account list or navigate
      } else {
        setError('Failed to create account. Status: ' + response.status);
      }
    } catch (err) {
      console.error("Account creation error:", err);
      // Log more details about the error
      console.error("Error response:", err.response?.data);
      console.error("Error status:", err.response?.status);
      console.error("Error headers:", err.response?.headers);
      
      setError(err.response?.data?.message || err.response?.data?.msg || err.response?.data?.error || 'An error occurred during account creation.');
    }
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit} 
      sx={{ 
        mt: 3, 
        p: 3, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 2, // Spacing between elements
        maxWidth: '500px', // Limit form width
        margin: 'auto' // Center the form
      }}
    >
      <Typography variant="h5" component="h2" gutterBottom>
        Create New Account
      </Typography>
      <TextField
        required
        fullWidth
        id="account-name"
        label="Account Name"
        name="accountName"
        value={accountName}
        onChange={(e) => setAccountName(e.target.value)}
        autoFocus
      />
      <TextField
        fullWidth
        id="description"
        label="Description (Optional)"
        name="description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        multiline
        rows={3}
      />
      {error && (
        <Typography color="error" variant="body2">
          {error}
        </Typography>
      )}
      {success && (
        <Typography color="success.main" variant="body2">
          {success}
        </Typography>
      )}
      <Button
        type="submit"
        fullWidth
        variant="contained"
        color="primary"
        sx={{ mt: 2 }}
      >
        Create Account
      </Button>
    </Box>
  );
}

export default AccountForm; 