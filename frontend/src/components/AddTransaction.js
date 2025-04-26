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
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import axiosInstance from '../api/axiosInstance';

/**
 * AddTransaction Component
 * 
 * This component provides a form interface for users to add new financial transactions.
 * It supports double-entry accounting by allowing users to add multiple postings
 * that must balance to zero. The component fetches available accounts from the API
 * and provides validation before submission.
 */
function AddTransaction() {
  // State for transaction form fields
  const [date, setDate] = useState(new Date());
  const [status, setStatus] = useState('');
  const [payee, setPayee] = useState('');
  const [postings, setPostings] = useState([
    { account: '', amount: '', currency: '₹' },
    { account: '', amount: '', currency: '₹' },
  ]);
  const [accounts, setAccounts] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  /**
   * Effect hook to fetch available accounts when component mounts
   */
  useEffect(() => {
    // Fetch list of accounts using axiosInstance instead of direct axios
    axiosInstance.get('/api/v1/accounts')
      .then(response => {
        // Ensure response.data exists and response.data.accounts is an array
        if (response.data && Array.isArray(response.data.accounts)) {
          // Sort accounts alphabetically
          const sortedAccounts = [...response.data.accounts].sort((a, b) => a.localeCompare(b));
          setAccounts(sortedAccounts);
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

  /**
   * Adds a new empty posting to the transaction
   */
  const handleAddPosting = () => {
    setPostings([...postings, { account: '', amount: '', currency: '₹' }]);
  };

  /**
   * Removes a posting at the specified index
   * @param {number} index - The index of the posting to remove
   */
  const handleRemovePosting = (index) => {
    const newPostings = [...postings];
    newPostings.splice(index, 1);
    setPostings(newPostings);
  };

  /**
   * Updates a specific field of a posting at the given index
   * @param {number} index - The index of the posting to update
   * @param {string} field - The field name to update ('account', 'amount', or 'currency')
   * @param {string} value - The new value for the field
   */
  const handlePostingChange = (index, field, value) => {
    const newPostings = [...postings];
    newPostings[index][field] = value;
    setPostings(newPostings);
  };

  /**
   * Handles form submission, validates entries, and sends to the API
   * @param {Event} e - The form submission event
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate postings - ensure they balance to zero (double-entry accounting)
    const total = postings.reduce((sum, posting) => {
      return sum + (parseFloat(posting.amount) || 0);
    }, 0);

    if (Math.abs(total) > 0.01) {
      setError('Transaction does not balance');
      return;
    }

    // Format date for API (YYYY-MM-DD)
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

    // Send transaction to the API using axiosInstance instead of direct axios
    axiosInstance.post('/api/v1/transactions', transactionData)
      .then(response => {
        // Reset form on success
        setDate(new Date());
        setStatus('');
        setPayee('');
        setPostings([
          { account: '', amount: '', currency: '₹' },
          { account: '', amount: '', currency: '₹' },
        ]);
        setSuccess('Transaction added successfully!');
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
        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {success}
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Date picker field */}
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Date"
                  value={date}
                  onChange={setDate}
                  slots={{
                    textField: (params) => <TextField {...params} fullWidth />
                  }}
                />
              </LocalizationProvider>
            </Grid>
            {/* Transaction status field */}
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
            {/* Payee field */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Payee"
                value={payee}
                onChange={(e) => setPayee(e.target.value)}
                required
              />
            </Grid>
            {/* Posting entries (dynamic) */}
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
                    InputProps={{
                      startAdornment: posting.currency,
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  {index >= 2 && (
                    <IconButton 
                      onClick={() => handleRemovePosting(index)}
                      color="error"
                      sx={{ mt: 1 }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Grid>
              </React.Fragment>
            ))}
            
            {/* Add posting button */}
            <Grid item xs={12}>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddPosting}
                sx={{ mt: 2 }}
              >
                Add Entry
              </Button>
            </Grid>
            
            {/* Submit button */}
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                type="submit"
                sx={{ mt: 3 }}
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