import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Grid,
} from '@mui/material';
import axios from 'axios';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function ViewTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchTransactions = useCallback(() => {
    const token = getToken(); // Get token
    const params = {
      limit: rowsPerPage,
      offset: page * rowsPerPage,
    };

    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    axios.get('/api/transactions', { 
      params, 
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Ensure response.data exists and response.data.transactions is an array
        if (response.data && Array.isArray(response.data.transactions)) {
          setTransactions(response.data.transactions);
        } else {
          // Log unexpected response and set transactions to empty array
          console.error('Unexpected response structure for transactions:', response.data);
          setTransactions([]);
        }
        // Note: In a real implementation, you'd get the total count from the API
        setTotalCount(100); // Placeholder
      })
      .catch(error => {
        console.error('Error fetching transactions:', error);
        // Set transactions to empty array on error to prevent crash
        setTransactions([]);
      });
  }, [page, rowsPerPage, startDate, endDate]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleDateChange = (setter) => (event) => {
    setter(event.target.value);
    setPage(0);
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        View Transactions
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              value={startDate}
              onChange={handleDateChange(setStartDate)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="End Date"
              type="date"
              value={endDate}
              onChange={handleDateChange(setEndDate)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
        </Grid>
      </Paper>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Date</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Status</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Payee</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Postings</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions.map((transaction, index) => (
              <TableRow key={index}>
                <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.date}</TableCell>
                <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.status}</TableCell>
                <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.payee}</TableCell>
                <TableCell sx={{ px: { xs: 1, sm: 2 } }}>
                  {transaction.postings.map((posting, pIndex) => (
                    <div key={pIndex}>
                      {posting.account}: {posting.currency} {posting.amount}
                    </div>
                  ))}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
}

export default ViewTransactions; 