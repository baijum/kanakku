import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  List,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
} from '@mui/material';
import axios from 'axios';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function Dashboard() {
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [balanceReport, setBalanceReport] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentTransactions();
    fetchBalanceReport();
  }, []);

  // Function to fetch all postings for a transaction
  const fetchTransactionWithAllPostings = async (transaction) => {
    if (!transaction || !transaction.id) return transaction;
    
    try {
      const token = getToken();
      const response = await axios.get(`/api/v1/transactions/${transaction.id}/related`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data && response.data.transactions && response.data.transactions.length > 0) {
        // Map the postings from the related endpoint
        const allPostings = response.data.transactions.map(tx => ({
          id: tx.id,
          account: tx.account_name,
          amount: tx.amount.toString(),
          currency: tx.currency || 'INR'
        }));
        
        // Return updated transaction with all postings and preserve status
        return {
          ...transaction,
          postings: allPostings
        };
      }
      
      return transaction;
    } catch (error) {
      console.error(`Error fetching postings for transaction ${transaction.id}:`, error);
      return transaction;
    }
  };

  // Main function to fetch recent transactions
  const fetchRecentTransactions = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const response = await axios.get('/api/v1/transactions/recent', { 
        params: { limit: 7 },
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data && Array.isArray(response.data.transactions)) {
        const basicTransactions = response.data.transactions;
        
        // Fetch complete postings for each transaction
        const completeTransactions = await Promise.all(
          basicTransactions.map(async (tx) => {
            // Check if this transaction might have multiple postings
            if (tx.postings && tx.postings.length >= 1) {
              return await fetchTransactionWithAllPostings(tx);
            }
            return tx;
          })
        );
        
        setRecentTransactions(completeTransactions);
      } else {
        console.error('Unexpected response structure for recent transactions:', response.data);
        setRecentTransactions([]);
      }
    } catch (error) {
      console.error('Error fetching recent transactions:', error);
      setError('Failed to load recent transactions');
      setRecentTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchBalanceReport = () => {
    const token = getToken();
    axios.get('/api/v1/reports/balance', { 
      params: { depth: 1 },
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(response => {
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
        setBalanceReport('');
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
              
              {loading ? (
                <Typography variant="body2" color="text.secondary">Loading transactions...</Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Payee</TableCell>
                        <TableCell>Postings</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentTransactions.map((transaction, index) => (
                        <TableRow key={index}>
                          <TableCell>{transaction.date}</TableCell>
                          <TableCell>
                            {transaction.status && transaction.status.trim() ? `${transaction.status} ${transaction.payee}` : transaction.payee}
                          </TableCell>
                          <TableCell>
                            {transaction.postings && transaction.postings.map((posting, pIndex) => (
                              <Box 
                                key={pIndex} 
                                sx={{ 
                                  display: 'flex', 
                                  justifyContent: 'space-between', 
                                  mb: 0.5, 
                                  borderBottom: pIndex < transaction.postings.length - 1 ? '1px solid #f0f0f0' : 'none',
                                  py: 0.5
                                }}
                              >
                                <Typography variant="body2" sx={{ mr: 1 }}>
                                  {posting.account}
                                </Typography>
                                <Typography variant="body2" sx={{ fontWeight: 'medium', whiteSpace: 'nowrap' }}>
                                  {posting.currency === 'INR' ? '₹' : posting.currency} {posting.amount}
                                </Typography>
                              </Box>
                            ))}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
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