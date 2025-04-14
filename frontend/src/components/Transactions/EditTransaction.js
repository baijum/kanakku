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
    { account: '', amount: '', currency: 'INR' },
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
      // Use the related transactions endpoint to get all postings
      const response = await axios.get(`/api/transactions/${id}/related`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      console.log('Related transactions data received:', response.data);
      
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
        const transactionData = response.data;
        console.log('Setting transaction data:');
        console.log('Date:', transactionData.date);
        console.log('Payee:', transactionData.payee);
        
        setDate(new Date(transactionData.date));
        setPayee(transactionData.payee || '');
        
        // Initialize postings from all related transactions
        if (transactionData.transactions && transactionData.transactions.length > 0) {
          const initialPostings = transactionData.transactions.map(tx => ({
            id: tx.id,
            account: tx.account_name || '',
            account_id: tx.account_id,
            amount: tx.amount.toString(),
            currency: tx.currency || 'INR',
          }));
          
          console.log('Initial postings from related transactions:', initialPostings);
          
          // Check if we need to add a balancing posting
          const totalAmount = initialPostings.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0);
          
          // If the total doesn't balance (within rounding error), add a balancing posting
          if (Math.abs(totalAmount) > 0.01) {
            console.log('Total amount does not balance, adding balancing posting. Current total:', totalAmount);
            
            // Try to find a suitable offsetting account
            let balancingAccountName = '';
            
            // Try to find an account that's not already used in the postings
            const usedAccountNames = initialPostings.map(p => p.account);
            const unusedAccount = accountsList.find(a => !usedAccountNames.includes(a.name));
            
            if (unusedAccount) {
              balancingAccountName = unusedAccount.name;
            } else if (accountsList.length > 0) {
              // Just use the first account if no unused account is found
              balancingAccountName = accountsList[0].name;
            }
            
            const balancingPosting = {
              account: balancingAccountName,
              amount: (-totalAmount).toFixed(2), // Balance out the total
              currency: initialPostings[0]?.currency || 'INR',
            };
            
            console.log('Adding balancing posting:', balancingPosting);
            initialPostings.push(balancingPosting);
          }
          
          setPostings(initialPostings);
        } else {
          // Fallback: if no transactions are provided, create default postings
          console.warn('No transactions provided in response, creating default postings');
          
          // Find two different accounts if possible for the default postings
          let account1 = accountsList.length > 0 ? accountsList[0].name : '';
          let account2 = '';
          
          if (accountsList.length > 1) {
            account2 = accountsList[1].name;
          } else if (accountsList.length > 0) {
            account2 = accountsList[0].name;
          }
          
          setPostings([
            { account: account1, amount: '100', currency: 'INR' },
            { account: account2, amount: '-100', currency: 'INR' }
          ]);
        }
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
        currency: 'INR' 
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
      
    // Get all existing transaction IDs that need to be replaced
    const existingTransactionIds = originalTransaction && 
      originalTransaction.transactions ? 
      originalTransaction.transactions.map(tx => tx.id) : 
      [id]; // Fallback to just the primary ID
      
    // Prepare transaction data in the format expected by the API
    const transactionData = {
      date: formattedDate,
      payee,
      status,
      postings: postings.map(posting => ({
        account: posting.account,
        amount: parseFloat(posting.amount),
        currency: posting.currency || 'INR',
        id: posting.id, // Include original ID if available
      })),
      original_transaction_ids: existingTransactionIds,
      primary_transaction_id: id
    };
    
    console.log('Submitting transaction data:', transactionData);

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
                          console.log(`Rendering account:`, selectedAccount);
                          return selectedAccount ? selectedAccount.fullName : '';
                        }}
                      >
                        {accounts.map((account) => (
                          <MenuItem key={account.id} value={account.name}>
                            {account.fullName}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Amount"
                      type="number"
                      value={posting.amount}
                      onChange={(e) => handlePostingChange(index, 'amount', e.target.value)}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <FormControl fullWidth>
                      <InputLabel>Currency</InputLabel>
                      <Select
                        value={posting.currency || 'INR'}
                        onChange={(e) => handlePostingChange(index, 'currency', e.target.value)}
                        label="Currency"
                        required
                      >
                        <MenuItem value="INR">INR</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <IconButton
                      onClick={() => handleRemovePosting(index)}
                      color="error"
                      aria-label="remove"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Grid>
                </React.Fragment>
              );
            })}
          </Grid>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            sx={{ mt: 3, mr: 1 }}
          >
            Update Transaction
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/transactions')}
            sx={{ mt: 3, ml: 1 }}
          >
            Cancel
          </Button>
        </form>
      </Paper>
    </Box>
  );
}

export default EditTransaction;