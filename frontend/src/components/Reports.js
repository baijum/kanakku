import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
} from '@mui/material';
import axios from 'axios';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function Reports() {
  const [tabValue, setTabValue] = useState(0);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [depth, setDepth] = useState('');
  const [balanceReport, setBalanceReport] = useState('');
  const [registerReport, setRegisterReport] = useState('');

  useEffect(() => {
    const token = getToken();
    // Fetch list of accounts from the standard accounts endpoint
    axios.get('/api/accounts', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(response => {
        // Ensure response.data exists and response.data.accounts is an array
        if (response.data && Array.isArray(response.data.accounts)) {
          setAccounts(response.data.accounts);
        } else {
          // Log unexpected response and set accounts to empty array
          console.error('Unexpected response structure for accounts:', response.data);
          setAccounts([]); 
        }
      })
      .catch(error => {
        console.error('Error fetching accounts:', error);
        // Set accounts to empty array on error to prevent crash
        setAccounts([]); 
      });
  }, []);

  const fetchBalanceReport = useCallback(() => {
    const token = getToken();
    const params = {};
    if (selectedAccount) params.account = selectedAccount;
    if (depth) params.depth = depth;

    axios.get('/api/v1/reports/balance', { 
      params,
      headers: { 'Authorization': `Bearer ${token}` } 
    })
      .then(response => {
        setBalanceReport(response.data.balance);
      })
      .catch(error => {
        console.error('Error fetching balance report:', error);
      });
  }, [selectedAccount, depth]);

  const fetchRegisterReport = useCallback(() => {
    const token = getToken();
    if (!selectedAccount) return;

    axios.get('/api/v1/reports/register', { 
      params: { account: selectedAccount },
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(response => {
        setRegisterReport(response.data.register);
      })
      .catch(error => {
        console.error('Error fetching register report:', error);
      });
  }, [selectedAccount]);

  useEffect(() => {
    if (tabValue === 0) {
      fetchBalanceReport();
    } else {
      fetchRegisterReport();
    }
  }, [tabValue, selectedAccount, depth, fetchBalanceReport, fetchRegisterReport]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleAccountChange = (event) => {
    setSelectedAccount(event.target.value);
  };

  const handleDepthChange = (event) => {
    setDepth(event.target.value);
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Balance Report" />
          <Tab label="Register Report" />
        </Tabs>
        <Box sx={{ mt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Account</InputLabel>
                <Select
                  value={selectedAccount}
                  onChange={handleAccountChange}
                  label="Account"
                >
                  <MenuItem value="">All Accounts</MenuItem>
                  {accounts.map((account) => (
                    <MenuItem key={account} value={account}>
                      {account}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            {tabValue === 0 && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Depth"
                  type="number"
                  value={depth}
                  onChange={handleDepthChange}
                  helperText="Number of account levels to show"
                />
              </Grid>
            )}
          </Grid>
        </Box>
      </Paper>
      <Paper sx={{ p: 3 }}>
        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
          {tabValue === 0 ? balanceReport : registerReport}
        </pre>
      </Paper>
    </Box>
  );
}

export default Reports; 