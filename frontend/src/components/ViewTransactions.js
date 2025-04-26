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
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';

function ViewTransactions() {
  // State management
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // Dialog states
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState(null);
  const [openExportDialog, setOpenExportDialog] = useState(false);
  
  // Export related states
  const [exportLoading, setExportLoading] = useState(false);
  const [preambles, setPreambles] = useState([]);
  const [selectedPreamble, setSelectedPreamble] = useState('');
  
  const navigate = useNavigate();

  // Function to fetch transaction details with full posting information
  const fetchTransactionWithAllPostings = async (transaction) => {
    if (!transaction || !transaction.id) return transaction;
    
    try {
      const response = await axiosInstance.get(`/api/v1/transactions/${transaction.id}/related`);
      
      if (response.data && response.data.transactions && response.data.transactions.length > 0) {
        // Map the postings from the related endpoint
        const allPostings = response.data.transactions.map(tx => ({
          id: tx.id,
          account: tx.account_name,
          amount: tx.amount.toString(),
          currency: tx.currency || 'INR'
        }));
        
        // Return updated transaction with all postings
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

  // Main function to fetch transactions with pagination and filtering
  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      };

      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;

      const response = await axiosInstance.get('/api/v1/transactions', { params });
      
      if (response.data && Array.isArray(response.data.transactions)) {
        const basicTransactions = response.data.transactions;
        
        // For each transaction that might have multiple postings,
        // fetch all the related transactions to get complete posting data
        const completeTransactions = await Promise.all(
          basicTransactions.map(async (tx) => {
            // Check if this transaction might have multiple postings
            if (tx.postings && tx.postings.length >= 1) {
              return await fetchTransactionWithAllPostings(tx);
            }
            return tx;
          })
        );
        
        setTransactions(completeTransactions);
        
        // Get total count from API if available, otherwise use a default
        setTotalCount(response.data.total || 100);
      } else {
        console.error('Unexpected response structure for transactions:', response.data);
        setTransactions([]);
        setError('Failed to load transaction data');
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setTransactions([]);
      setError('Error loading transactions. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, startDate, endDate]);

  // Fetch preambles for export functionality
  const fetchPreambles = useCallback(async () => {
    try {
      const response = await axiosInstance.get('/api/v1/preambles');
      
      if (response.data && Array.isArray(response.data.preambles)) {
        setPreambles(response.data.preambles);
        
        // Set first preamble if available
        if (response.data.preambles.length > 0) {
          setSelectedPreamble(response.data.preambles[0].id.toString());
        }
      }
    } catch (error) {
      console.error('Error fetching preambles:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load preambles for export',
        severity: 'warning'
      });
    }
  }, []);

  // Load data when component mounts or dependencies change
  useEffect(() => {
    fetchTransactions();
    fetchPreambles();
  }, [fetchTransactions, fetchPreambles]);

  // Event handlers
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
    if (transactionId) {
      navigate(`/transactions/edit/${transactionId}`);
    } else {
      setSnackbar({
        open: true,
        message: 'Cannot edit: Invalid transaction ID',
        severity: 'error'
      });
    }
  };

  const handleDeleteConfirmOpen = (transactionId) => {
    setTransactionToDelete(transactionId);
    setOpenDeleteDialog(true);
  };

  const handleDeleteConfirmClose = () => {
    setOpenDeleteDialog(false);
  };

  const handleDeleteTransaction = async () => {
    if (!transactionToDelete) return;
    
    try {
      setLoading(true);
      const endpoint = `/api/v1/transactions/${transactionToDelete}/related`;

      await axiosInstance.delete(endpoint);
      
      // After successful deletion, refresh the transaction list
      fetchTransactions();
      
      // Show success message
      setSnackbar({
        open: true,
        message: 'Transaction deleted successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error deleting transaction:', error);
      setSnackbar({
        open: true,
        message: 'Failed to delete transaction',
        severity: 'error'
      });
    } finally {
      setLoading(false);
      // Close the delete confirmation dialog
      setOpenDeleteDialog(false);
      setTransactionToDelete(null);
    }
  };

  // Export dialog handlers
  const handleOpenExportDialog = () => {
    setOpenExportDialog(true);
  };

  const handleCloseExportDialog = () => {
    setOpenExportDialog(false);
  };

  const handlePreambleChange = (event) => {
    setSelectedPreamble(event.target.value);
  };

  const handleExportLedgerFormat = async () => {
    try {
      setExportLoading(true);
      
      let url = '/api/v1/ledgertransactions';
      const params = [];
      
      // Add preamble if selected
      if (selectedPreamble) {
        params.push(`preamble_id=${selectedPreamble}`);
      }
      
      // Add date range parameters if provided
      if (startDate) {
        params.push(`start_date=${startDate}`);
      }
      
      if (endDate) {
        params.push(`end_date=${endDate}`);
      }
      
      // Append parameters if any
      if (params.length > 0) {
        url += `?${params.join('&')}`;
      }
      
      // Set responseType to blob to handle file download
      const response = await axiosInstance.get(url, {
        responseType: 'blob' // Important for handling the response as a file
      });
      
      // Create a download link and trigger the download
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      // Set the filename from the Content-Disposition header if available
      // or use a default name
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'transactions.ledger';
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      // Close the export dialog
      setOpenExportDialog(false);
      
      // Show success message
      setSnackbar({
        open: true,
        message: 'Export successful',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error exporting transactions:', error);
      setSnackbar({
        open: true,
        message: 'Failed to export transactions',
        severity: 'error'
      });
    } finally {
      setExportLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Transactions
      </Typography>

      {/* Filters and Export Section */}
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
              disabled={exportLoading || loading}
              fullWidth
            >
              Export
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Main Content */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : transactions.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No transactions found. Try adjusting your filters.
            </Typography>
          </Box>
        ) : (
          <>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ px: { xs: 1, sm: 2 } }}>Date</TableCell>
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
                      <TableCell sx={{ px: { xs: 1, sm: 2 } }}>
                        {transaction.status && transaction.status.trim() ? `${transaction.status} ${transaction.payee}` : transaction.payee}
                      </TableCell>
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
                          onClick={() => handleEditTransaction(editId)}
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
          </>
        )}
      </TableContainer>

      {/* Dialogs */}
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
                  {preamble.name}
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
            {exportLoading ? <CircularProgress size={24} /> : 'Export'}
          </Button>
        </DialogActions>
      </Dialog>

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

      {/* Feedback Snackbar */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default ViewTransactions; 