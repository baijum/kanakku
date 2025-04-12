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

function ViewTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchTransactions = useCallback(() => {
    const params = {
      limit: rowsPerPage,
      offset: page * rowsPerPage,
    };

    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    axios.get('/api/transactions', { params })
      .then(response => {
        setTransactions(response.data.transactions);
        // Note: In a real implementation, you'd get the total count from the API
        setTotalCount(100); // Placeholder
      })
      .catch(error => {
        console.error('Error fetching transactions:', error);
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
    <Box>
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
              <TableCell>Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Payee</TableCell>
              <TableCell>Postings</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions.map((transaction, index) => (
              <TableRow key={index}>
                <TableCell>{transaction.date}</TableCell>
                <TableCell>{transaction.status}</TableCell>
                <TableCell>{transaction.payee}</TableCell>
                <TableCell>
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