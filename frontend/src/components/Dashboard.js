import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import axios from 'axios';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function Dashboard() {
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [balanceReport, setBalanceReport] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecentTransactions();
    fetchBalanceReport();
  }, []);

  const fetchRecentTransactions = () => {
    const token = getToken(); // Get token
    axios.get('/api/v1/transactions', { 
      params: { limit: 5 },
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Add check for transactions
        if (response.data && Array.isArray(response.data.transactions)) {
          setRecentTransactions(response.data.transactions);
        } else {
          console.error('Unexpected response structure for recent transactions:', response.data);
          setRecentTransactions([]);
        }
      })
      .catch(error => {
        console.error('Error fetching recent transactions:', error);
        setError('Failed to load recent transactions');
        setRecentTransactions([]); // Set to empty array on error
      });
  };

  const fetchBalanceReport = () => {
    const token = getToken(); // Get token
    axios.get('/api/v1/reports/balance', { 
      params: { depth: 1 },
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Add check for balance report string
        if (response.data && typeof response.data.balance === 'string') {
          setBalanceReport(response.data.balance);
        } else {
          console.error('Unexpected response structure for balance report:', response.data);
          setBalanceReport('');
        }
      })
      .catch(error => {
        console.error('Error fetching balance report:', error);
        setError('Failed to load balance report');
        setBalanceReport(''); // Set to empty string on error
      });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Transactions
              </Typography>
              <List>
                {recentTransactions.map((transaction, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={transaction.payee}
                        secondary={
                          <>
                            {transaction.date}
                            <br />
                            {transaction.postings.map((posting, pIndex) => (
                              <span key={pIndex}>
                                {posting.account}: {posting.currency === 'INR' ? `₹${posting.amount}` : `${posting.currency} ${posting.amount}`}
                                <br />
                              </span>
                            ))}
                          </>
                        }
                      />
                    </ListItem>
                    {index < recentTransactions.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Balances
              </Typography>
              {balanceReport ? (
                <Box sx={{ fontFamily: 'monospace' }}>
                  {(() => {
                    // Process the balance report to group by account name
                    const balanceMap = new Map();
                    
                    balanceReport.split('\n').forEach(line => {
                      if (!line.trim()) return;
                      
                      // Split each line into account name and balance parts
                      const parts = line.trim().split(/\s+(?=[\d₹])/);
                      const accountName = parts[0];
                      const balanceStr = parts[1] || '';
                      
                      // Extract numeric value from balance string
                      const numericValue = parseFloat(balanceStr.replace(/[^\d.-]/g, ''));
                      
                      if (!isNaN(numericValue)) {
                        // Get currency symbol/code
                        const currencyMatch = balanceStr.match(/[^\d.\s-]+/);
                        const currency = currencyMatch ? currencyMatch[0] : '';
                        
                        // Use account name as key, store currency and sum value
                        if (balanceMap.has(accountName)) {
                          const existing = balanceMap.get(accountName);
                          existing.value += numericValue;
                        } else {
                          balanceMap.set(accountName, { 
                            value: numericValue, 
                            currency 
                          });
                        }
                      }
                    });
                    
                    // Convert map back to array for rendering
                    return Array.from(balanceMap).map(([accountName, data], index) => {
                      const { value, currency } = data;
                      const formattedBalance = currency === '₹' 
                        ? `${currency}${value.toFixed(2)}` 
                        : `${value.toFixed(2)} ${currency}`;
                      
                      return (
                        <Box 
                          key={index} 
                          sx={{ 
                            display: 'flex', 
                            justifyContent: 'space-between',
                            mb: 0.5,
                            wordBreak: 'break-word'
                          }}
                        >
                          <Box sx={{ mr: 2, maxWidth: '70%' }}>{accountName}</Box>
                          <Box sx={{ textAlign: 'right', whiteSpace: 'nowrap' }}>{formattedBalance}</Box>
                        </Box>
                      );
                    });
                  })()}
                </Box>
              ) : (
                <Typography>No balance data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {error && (
        <Paper sx={{ p: 2, mt: 2, bgcolor: 'error.light' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
    </Box>
  );
}

export default Dashboard; 