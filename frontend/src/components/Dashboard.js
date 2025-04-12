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

function Dashboard() {
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [balanceReport, setBalanceReport] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecentTransactions();
    fetchBalanceReport();
  }, []);

  const fetchRecentTransactions = () => {
    axios.get('/api/transactions', { params: { limit: 5 } })
      .then(response => {
        setRecentTransactions(response.data.transactions);
      })
      .catch(error => {
        console.error('Error fetching recent transactions:', error);
        setError('Failed to load recent transactions');
      });
  };

  const fetchBalanceReport = () => {
    axios.get('/api/reports/balance', { params: { depth: 1 } })
      .then(response => {
        setBalanceReport(response.data.balance);
      })
      .catch(error => {
        console.error('Error fetching balance report:', error);
        setError('Failed to load balance report');
      });
  };

  return (
    <Box>
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
                                {posting.account}: {posting.currency} {posting.amount}
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
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {balanceReport}
              </pre>
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