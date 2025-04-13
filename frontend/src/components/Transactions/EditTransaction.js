import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  CircularProgress,
  Alert,
  IconButton,
  Divider,
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

// Function to get the token
const getToken = () => localStorage.getItem('token');

function EditTransaction() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [accounts, setAccounts] = useState([]);
  
  // Transaction fields
  const [date, setDate] = useState(new Date());
  const [payee, setPayee] = useState('');
  const [status, setStatus] = useState('');
  const [postings, setPostings] = useState([
    { account: '', amount: '', currency: 'USD' },
  ]);
  
  // Track the original transaction data for comparison
  const [originalTransaction, setOriginalTransaction] = useState(null);

  useEffect(() => {
    // Validate transaction ID before fetching
    if (!id || id === 'undefined') {
      setError('Invalid transaction ID. Please go back and try again.');
      setLoading(false);
      console.error('Invalid transaction ID:', id);
      return;
    }
    
    console.log('Fetching transaction with ID:', id);
    
    // Fetch transaction details when component mounts
    fetchTransaction();
    fetchAccounts();
  }, [id]);

  useEffect(() => {
    // For debugging - log postings and accounts whenever they change
    if (postings.length > 0 && accounts.length > 0) {
      console.log('Current postings:', postings);
      console.log('Available accounts:', accounts);
    }
  }, [postings, accounts]);

  const fetchTransaction = async () => {
    setLoading(true);
    const token = getToken();
    
    try {
      const response = await axios.get(`/api/transactions/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      console.log('Transaction data received:', response.data);
      
      // Store original transaction data
      setOriginalTransaction(response.data);

      // Also fetch accounts to prepare for initializing postings
      const accountsResponse = await axios.get('/api/accounts/details', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const accountsList = Array.isArray(accountsResponse.data) ? accountsResponse.data : [];
      console.log('Accounts for initializing:', accountsList);

      // Set form values from transaction data
      if (response.data) {
        console.log('Setting transaction data:');
        console.log('Date:', response.data.date);
        console.log('Payee:', response.data.payee);
        console.log('Account:', response.data.account_name);
        
        setDate(new Date(response.data.date));
        setPayee(response.data.payee || '');
        
        // Initialize with current transaction as first posting
        const initialPosting = {
          account: response.data.account_name || '',
          account_id: response.data.account_id,
          amount: response.data.amount.toString(),
          currency: response.data.currency || 'USD',
        };
        
        // Try to find a suitable offsetting account for the balancing posting
        // Prefer an account of a different type than the first account
        let balancingAccountName = '';
        
        // Find the type of the first account
        const firstAccountType = accountsList.find(a => a.name === response.data.account_name)?.type || '';
        
        // Find accounts of different types
        const otherTypeAccounts = accountsList.filter(a => a.type !== firstAccountType);
        
        if (otherTypeAccounts.length > 0) {
          // Choose an account of a different type
          balancingAccountName = otherTypeAccounts[0].name;
        } else if (accountsList.length > 0) {
          // If no different type accounts, just pick the first account that's not the same as initialPosting
          const differentAccount = accountsList.find(a => a.name !== response.data.account_name);
          balancingAccountName = differentAccount ? differentAccount.name : accountsList[0].name;
        }
        
        // We need to add a second posting for balancing, initialized with a selected account if possible
        const balancingPosting = {
          account: balancingAccountName,
          amount: (-response.data.amount).toString(), // Opposite amount for balancing
          currency: response.data.currency || 'USD',
        };
        
        console.log('Initial posting:', initialPosting);
        console.log('Balancing posting:', balancingPosting);
        
        setPostings([initialPosting, balancingPosting]);
      }
    } catch (err) {
      console.error('Error fetching transaction:', err);
      setError(err.response?.data?.error || 'Failed to load transaction data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    const token = getToken();
    
    try {
      // Try to get the full account details first
      const detailsResponse = await axios.get('/api/accounts/details', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (detailsResponse.data && Array.isArray(detailsResponse.data)) {
        console.log('Account details:', detailsResponse.data);
        // Set accounts with full details
        setAccounts(detailsResponse.data.map(account => ({
          id: account.id,
          name: account.name,
          type: account.type,
          fullName: `${account.name} (${account.type})`
        })));
        return;
      }
      
      // Fallback to the regular accounts endpoint
      const response = await axios.get('/api/accounts', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data && Array.isArray(response.data.accounts)) {
        console.log('Accounts names only:', response.data.accounts);
        // Create account objects with just names
        setAccounts(response.data.accounts.map(name => ({
          name: name,
          fullName: name
        })));
      } else {
        console.error('Unexpected response structure for accounts:', response.data);
      }
    } catch (err) {
      console.error('Error fetching accounts:', err);
      setError('Failed to load accounts. Please try again.');
    }
  };

  const handleAddPosting = () => {
    // Find the first account as a default, if available
    const defaultAccount = accounts.length > 0 ? accounts[0].name : '';
    
    setPostings([
      ...postings, 
      { 
        account: defaultAccount, 
        amount: '0', 
        currency: 'USD' 
      }
    ]);
  };

  const handleRemovePosting = (index) => {
    const newPostings = [...postings];
    newPostings.splice(index, 1);
    setPostings(newPostings);
  };

  const handlePostingChange = (index, field, value) => {
    const newPostings = [...postings];
    newPostings[index][field] = value;
    console.log(`Updating posting ${index}, field ${field} to ${value}`);
    console.log('New postings:', newPostings);
    setPostings(newPostings);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validate form
    if (!payee.trim()) {
      setError('Payee is required');
      return;
    }
    
    // Validate postings
    for (const posting of postings) {
      if (!posting.account) {
        setError('All postings must have an account');
        return;
      }
      
      if (!posting.amount || isNaN(Number(posting.amount))) {
        setError('All postings must have a valid amount');
        return;
      }
    }
    
    // Check if transaction balances (sum of all postings should be close to 0)
    const total = postings.reduce((sum, posting) => sum + (parseFloat(posting.amount) || 0), 0);
    
    if (Math.abs(total) > 0.01) {
      setError('Transaction does not balance (sum of all postings must be 0)');
      return;
    }

    const token = getToken();
    const formattedDate = date instanceof Date && !isNaN(date)
      ? date.toISOString().split('T')[0]
      : (typeof date === 'string' ? date : '');
      
    // Prepare transaction data in the format expected by the API
    const transactionData = {
      date: formattedDate,
      payee,
      status,
      postings: postings.map(posting => ({
        account: posting.account,
        amount: parseFloat(posting.amount),
        currency: posting.currency || 'USD',
      })),
      original_transaction_id: id
    };

    try {
      // We'll use the update endpoint that handles multiple postings
      const response = await axios.put(`/api/transactions/${id}/update_with_postings`, transactionData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setSuccess('Transaction updated successfully');
      setTimeout(() => {
        navigate('/transactions');
      }, 1500);
    } catch (err) {
      console.error('Error updating transaction:', err);
      setError(err.response?.data?.error || 'Failed to update transaction. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Show error with back button if there's an error
  if (error && !success) {
    return (
      <Box sx={{ p: { xs: 2, sm: 3 } }}>
        <Typography variant="h4" gutterBottom>
          Edit Transaction
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => navigate('/transactions')}
          sx={{ mt: 2 }}
        >
          Back to Transactions
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Edit Transaction
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
            
            {/* Postings */}
            {postings.map((posting, index) => {
              console.log(`Rendering posting ${index}, account:`, posting.account);
              return (
                <React.Fragment key={index}>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                  </Grid>
                  <Grid item xs={12} sm={5}>
                    <FormControl fullWidth>
                      <InputLabel>Account</InputLabel>
                      <Select
                        value={posting.account || ''}
                        onChange={(e) => handlePostingChange(index, 'account', e.target.value)}
                        label="Account"
                        required
                        renderValue={(selected) => {
                          console.log(`Rendering value for posting ${index}, selected:`, selected);
                          // Find the account with matching name
                          const selectedAccount = accounts.find(a => a.name === selected);
                          console.log(`Found matching account:`, selectedAccount);
                          return selectedAccount ? selectedAccount.fullName : selected;
                        }}
                      >
                        {accounts && accounts.length > 0 ? (
                          accounts.map((account, accountIndex) => (
                            <MenuItem key={accountIndex} value={account.name}>
                              {account.fullName}
                            </MenuItem>
                          ))
                        ) : (
                          <MenuItem value="" disabled>
                            No accounts available
                          </MenuItem>
                        )}
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
              );
            })}
            
            <Grid item xs={12}>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddPosting}
                variant="outlined"
                sx={{ mr: 2 }}
              >
                Add Posting
              </Button>
              <Button
                onClick={fetchAccounts}
                variant="outlined"
                color="secondary"
              >
                Refresh Accounts
              </Button>
            </Grid>
            
            <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/transactions')}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                variant="contained" 
                color="primary"
              >
                Update Transaction
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}

export default EditTransaction; 