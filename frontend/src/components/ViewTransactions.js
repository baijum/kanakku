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
  Button,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { useNavigate } from 'react-router-dom';
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
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [preambles, setPreambles] = useState([]);
  const [selectedPreamble, setSelectedPreamble] = useState('');
  const [openExportDialog, setOpenExportDialog] = useState(false);
  const navigate = useNavigate();

  const fetchTransactions = useCallback(() => {
    const token = getToken(); // Get token
    const params = {
      limit: rowsPerPage,
      offset: page * rowsPerPage,
    };

    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;

    axios.get('/api/v1/transactions', { 
      params, 
      headers: { 'Authorization': `Bearer ${token}` } // Add header
    })
      .then(response => {
        // Ensure response.data exists and response.data.transactions is an array
        if (response.data && Array.isArray(response.data.transactions)) {
          console.log('Transaction data:', response.data.transactions);
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

  // Fetch preambles when component mounts
  const fetchPreambles = useCallback(() => {
    const token = getToken();
    axios.get('/api/v1/preambles', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(response => {
        if (response.data && Array.isArray(response.data.preambles)) {
          setPreambles(response.data.preambles);
          // Find and set default preamble if available
          const defaultPreamble = response.data.preambles.find(p => p.is_default);
          if (defaultPreamble) {
            setSelectedPreamble(defaultPreamble.id.toString());
          }
        }
      })
      .catch(error => {
        console.error('Error fetching preambles:', error);
      });
  }, []);

  useEffect(() => {
    fetchTransactions();
    fetchPreambles();
  }, [fetchTransactions, fetchPreambles]);

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

  const handleEditTransaction = (transactionId) => {
    // Make sure we have a valid ID before navigating
    if (transactionId) {
      navigate(`/transactions/edit/${transactionId}`);
    } else {
      console.error('Attempted to edit transaction with undefined ID');
    }
  };

  const handleDeleteConfirmOpen = (transactionId) => {
    setTransactionToDelete(transactionId);
    setOpenDeleteDialog(true);
  };

  const handleDeleteConfirmClose = () => {
    setOpenDeleteDialog(false);
  };

  const handleDeleteTransaction = () => {
    if (!transactionToDelete) {
      console.error('No transaction selected for deletion');
      setOpenDeleteDialog(false);
      return;
    }

    const token = getToken();
    const endpoint = `/api/v1/transactions/${transactionToDelete}/related`;

    axios.delete(endpoint, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(response => {
        console.log('Delete response:', response.data);
        // Refresh transactions list
        fetchTransactions();
        // Close dialog
        setOpenDeleteDialog(false);
      })
      .catch(error => {
        console.error('Error deleting transaction:', error);
        setOpenDeleteDialog(false);
        // You could add error state and display message to user
      });
  };

  const handleOpenExportDialog = () => {
    setOpenExportDialog(true);
  };

  const handleCloseExportDialog = () => {
    setOpenExportDialog(false);
  };

  const handlePreambleChange = (event) => {
    setSelectedPreamble(event.target.value);
  };

  const handleExportLedgerFormat = () => {
    setExportLoading(true);
    const token = getToken();
    
    // Prepare URL with preamble ID if selected
    let url = '/api/v1/ledgertransactions';
    if (selectedPreamble) {
      url += `?preamble_id=${selectedPreamble}`;
    }
    
    axios.get(url, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob' // Important for handling the response as a file
    })
      .then(response => {
        // Create a blob from the response data
        const blob = new Blob([response.data], { type: 'text/plain' });
        
        // Create a URL for the blob
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary anchor element to trigger the download
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transactions.ledger';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setExportLoading(false);
        handleCloseExportDialog();
      })
      .catch(error => {
        console.error('Error exporting transactions in ledger format:', error);
        setExportLoading(false);
        handleCloseExportDialog();
        // You could add error state and display message to user
      });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Transactions
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={5}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              value={startDate}
              onChange={handleDateChange(setStartDate)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={5}>
            <TextField
              fullWidth
              label="End Date"
              type="date"
              value={endDate}
              onChange={handleDateChange(setEndDate)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={2} sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<FileDownloadIcon />}
              onClick={handleOpenExportDialog}
              disabled={exportLoading}
              fullWidth
            >
              Export
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Export Dialog */}
      <Dialog open={openExportDialog} onClose={handleCloseExportDialog}>
        <DialogTitle>Export Transactions</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Select a preamble to include at the beginning of the exported file.
          </DialogContentText>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="preamble-select-label">Preamble</InputLabel>
            <Select
              labelId="preamble-select-label"
              id="preamble-select"
              value={selectedPreamble}
              label="Preamble"
              onChange={handlePreambleChange}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {preambles.map((preamble) => (
                <MenuItem key={preamble.id} value={preamble.id.toString()}>
                  {preamble.name} {preamble.is_default ? '(Default)' : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseExportDialog}>Cancel</Button>
          <Button 
            onClick={handleExportLedgerFormat}
            variant="contained"
            disabled={exportLoading}
          >
            Export
          </Button>
        </DialogActions>
      </Dialog>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Date</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Status</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Payee</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Postings</TableCell>
              <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions.map((transaction, index) => {
              // Try to get a valid ID for editing, first from transaction, then from first posting
              const editId = transaction.id || 
                (transaction.postings && transaction.postings.length > 0 ? 
                  transaction.postings[0].id : undefined);
              
              return (
                <TableRow key={index}>
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.date}</TableCell>
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.status}</TableCell>
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>{transaction.payee}</TableCell>
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>
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
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>
                    <IconButton 
                      color="primary" 
                      onClick={() => {
                        console.log('Editing transaction with ID:', editId);
                        handleEditTransaction(editId);
                      }}
                      aria-label="edit"
                      disabled={!editId}
                      sx={{ mr: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton 
                      color="error"
                      onClick={() => handleDeleteConfirmOpen(editId)}
                      aria-label="delete"
                      disabled={!editId}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
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

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={handleDeleteConfirmClose}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this transaction and all related transactions? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteConfirmClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteTransaction} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ViewTransactions; 