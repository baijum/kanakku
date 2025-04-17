import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import axiosInstance from '../../api/axiosInstance'; // Import the configured instance

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function EditAccount() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [accountName, setAccountName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  // Fetch account details when component mounts
  useEffect(() => {
    const fetchAccountDetails = async () => {
      setLoading(true);
      setError('');
      
      try {
        const token = getToken();
        if (!token) {
          setError('Authentication required. Please log in.');
          setLoading(false);
          return;
        }
        const config = { headers: { 'Authorization': `Bearer ${token}` } };

        // Try getting account details first from standard endpoint
        try {
          // Directly fetch account information using the specific account endpoint
          const response = await axiosInstance.get(`/api/v1/accounts/${id}`, config);
          
          console.log('Account API Response:', response.data);
          
          if (response.data) {
            setAccountName(response.data.name || '');
            setDescription(response.data.description || '');
            setLoading(false);
            return;
          }
        } catch (detailError) {
          console.error('Error fetching account details:', detailError);
          // Continue with fallback
        }
        
        // Fallback: try to get all accounts and find the one matching the ID
        try {
          // Get detailed account info
          const detailsResponse = await axiosInstance.get('/api/v1/accounts/details', config);
          
          console.log('Accounts details response:', detailsResponse.data);
          
          if (detailsResponse.data && Array.isArray(detailsResponse.data)) {
            const accountInfo = detailsResponse.data.find(a => a.id === parseInt(id));
            if (accountInfo) {
              setAccountName(accountInfo.name || '');
              setDescription(accountInfo.description || '');
              setLoading(false);
              return;
            }
          }
        } catch (detailsError) {
          console.error('Error fetching accounts details:', detailsError);
          // Continue with next fallback
        }
        
        // Final fallback: Get just account names
        const accountsResponse = await axiosInstance.get('/api/v1/accounts', config);
        
        console.log('Accounts list response:', accountsResponse.data);
        
        if (accountsResponse.data && accountsResponse.data.accounts) {
          const accountIndex = parseInt(id) - 1;
          if (accountIndex >= 0 && accountIndex < accountsResponse.data.accounts.length) {
            const accountInfo = {
              id: id,
              name: accountsResponse.data.accounts[accountIndex],
              description: ''
            };
            setAccountName(accountInfo.name);
            setDescription('');
          } else {
            throw new Error('Account not found');
          }
        } else {
          throw new Error('No accounts data available');
        }
      } catch (err) {
        console.error('Error fetching account details:', err);
        setError('Error loading account details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchAccountDetails();
    } else {
      setLoading(false);
      setError('Account ID is missing');
    }
  }, [id]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!accountName) {
      setError('Account Name is required.');
      return;
    }

    const updatedAccount = {
      name: accountName,
      description: description,
    };

    console.log('Submitting updated account:', updatedAccount);

    try {
      const token = getToken();
      if (!token) {
        setError('Authentication required. Please log in.');
        return;
      }
      const config = { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } };

      const response = await axiosInstance.put(`/api/v1/accounts/${id}`, updatedAccount, config);

      console.log('Update response:', response.data);

      if (response.status === 200) {
        setSuccess(`Account '${accountName}' updated successfully!`);
        // Navigate back to accounts list after a delay
        setTimeout(() => navigate('/accounts'), 1500);
      } else {
        setError('Failed to update account. Status: ' + response.status);
      }
    } catch (err) {
      console.error("Account update error:", err);
      setError(err.response?.data?.message || err.response?.data?.error || 'An error occurred during account update.');
    }
  };

  const handleCancel = () => {
    navigate('/accounts');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Edit Account
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Box 
          component="form" 
          onSubmit={handleSubmit} 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: 2,
            maxWidth: '500px',
            margin: 'auto'
          }}
        >
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button 
              variant="outlined" 
              onClick={handleCancel}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              color="primary"
            >
              Update Account
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default EditAccount; 