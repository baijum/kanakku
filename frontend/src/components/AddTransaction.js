import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function AddTransaction() {
  const [date, setDate] = useState(new Date());
  const [status, setStatus] = useState('');
  const [payee, setPayee] = useState('');
  const [postings, setPostings] = useState([
    { account: '', amount: '', currency: '$' },
    { account: '', amount: '', currency: '$' },
  ]);
  const [accounts, setAccounts] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getToken(); // Get token
    // Fetch list of accounts
    axios.get('/api/accounts', { 
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Ensure response.data exists and response.data.accounts is an array
        if (response.data && Array.isArray(response.data.accounts)) {
          setAccounts(response.data.accounts);
        } else {
          console.error('Unexpected response structure for accounts:', response.data);
          setAccounts([]);
        }
      })
      .catch(error => {
        console.error('Error fetching accounts:', error);
        setAccounts([]); // Set to empty array on error
      });
  }, []);

  const handleAddPosting = () => {
    setPostings([...postings, { account: '', amount: '', currency: '$' }]);
  };

  const handleRemovePosting = (index) => {
    const newPostings = [...postings];
    newPostings.splice(index, 1);
    setPostings(newPostings);
  };

  const handlePostingChange = (index, field, value) => {
    const newPostings = [...postings];
    newPostings[index][field] = value;
    setPostings(newPostings);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Validate postings
    const total = postings.reduce((sum, posting) => {
      return sum + (parseFloat(posting.amount) || 0);
    }, 0);

    if (Math.abs(total) > 0.01) {
      setError('Transaction does not balance');
      return;
    }

    // Format date
    const formattedDate = date.toISOString().split('T')[0];

    // Prepare transaction data
    const transactionData = {
      date: formattedDate,
      status: status,
      payee: payee,
      postings: postings.map(posting => ({
        account: posting.account,
        amount: posting.amount,
        currency: posting.currency,
      })),
    };

    const token = getToken(); // Get token
    // Send to backend
    axios.post('/api/transactions', transactionData, {
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Reset form
        setDate(new Date());
        setStatus('');
        setPayee('');
        setPostings([
          { account: '', amount: '', currency: '$' },
          { account: '', amount: '', currency: '$' },
        ]);
        alert('Transaction added successfully!');
      })
      .catch(error => {
        console.error('Error adding transaction:', error);
        setError(error.response?.data?.error || 'Failed to add transaction');
      });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Add Transaction
      </Typography>
      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Date"
                  value={date}
                  onChange={setDate}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">None</MenuItem>
                  <MenuItem value="*">Cleared</MenuItem>
                  <MenuItem value="!">Pending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Payee"
                value={payee}
                onChange={(e) => setPayee(e.target.value)}
                required
              />
            </Grid>
            {postings.map((posting, index) => (
              <React.Fragment key={index}>
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                </Grid>
                <Grid item xs={12} sm={5}>
                  <FormControl fullWidth>
                    <InputLabel>Account</InputLabel>
                    <Select
                      value={posting.account}
                      onChange={(e) => handlePostingChange(index, 'account', e.target.value)}
                      label="Account"
                      required
                    >
                      {accounts.map((account) => (
                        <MenuItem key={account} value={account}>
                          {account}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={5}>
                  <TextField
                    fullWidth
                    label="Amount"
                    type="number"
                    value={posting.amount}
                    onChange={(e) => handlePostingChange(index, 'amount', e.target.value)}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                    <IconButton
                      onClick={() => handleRemovePosting(index)}
                      disabled={postings.length <= 2}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Grid>
              </React.Fragment>
            ))}
            <Grid item xs={12}>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddPosting}
                variant="outlined"
              >
                Add Posting
              </Button>
            </Grid>
            {error && (
              <Grid item xs={12}>
                <Typography color="error">{error}</Typography>
              </Grid>
            )}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
              >
                Add Transaction
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}

export default AddTransaction; 