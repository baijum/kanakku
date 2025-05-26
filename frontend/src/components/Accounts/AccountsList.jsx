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
  Button,
  IconButton,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../../api/axiosInstance';

// Function to get the token (assuming it's stored in localStorage)
const getToken = () => localStorage.getItem('token');

function AccountsList() {
  const [accounts, setAccounts] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState(null);
  const navigate = useNavigate();

  const fetchAccounts = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setError('Authentication required.');
      return;
    }

    const fetchConfig = {
      headers: { 'Authorization': `Bearer ${token}` }
    };

    try {
      // Fetch main accounts list
      const [accountsResponse, detailsResponse] = await Promise.all([
        axiosInstance.get('/api/v1/accounts', fetchConfig),
        axiosInstance.get('/api/v1/accounts/details', fetchConfig)
      ]);

      console.log('Names API Response:', accountsResponse.data);

      if (accountsResponse.data && accountsResponse.data.accounts) {
        // Convert names to account objects
        const accountObjects = accountsResponse.data.accounts.map((name, idx) => ({
          id: idx + 1,  // Temporary ID for rendering
          name: name,
          description: '' // Placeholder
        }));

        // Sort accounts alphabetically by name
        accountObjects.sort((a, b) => a.name.localeCompare(b.name));

        setAccounts(accountObjects);
        setTotalCount(accountObjects.length);

        // After successfully getting names, try to get full details
        if (detailsResponse.data && Array.isArray(detailsResponse.data)) {
          // If we get details successfully, update with the full account objects
          const sortedDetails = [...detailsResponse.data].sort((a, b) =>
            a.name.localeCompare(b.name)
          );
          setAccounts(sortedDetails);
          setTotalCount(sortedDetails.length);
        }
      } else {
        console.error('Unexpected response structure for accounts:', accountsResponse.data);
        setAccounts([]);
        setTotalCount(0);
        setError('Failed to load accounts. Unexpected data format.');
      }
    } catch (error) {
      console.error('Error fetching account names:', error);
      setAccounts([]);
      setTotalCount(0);
      setError('Failed to load accounts. Please try again later.');
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleEditAccount = (accountId) => {
    navigate(`/accounts/edit/${accountId}`);
  };

  const handleDeleteAccount = (account) => {
    setAccountToDelete(account);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteAccount = async () => {
    if (!accountToDelete) {
      setError('Invalid account');
      setDeleteDialogOpen(false);
      return;
    }

    console.log('Deleting account:', accountToDelete.id);
    const token = getToken();

    try {
      await axiosInstance.delete(`/api/v1/accounts/${accountToDelete.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setSuccess('Account deleted successfully');
      setDeleteDialogOpen(false);
      fetchAccounts(); // Refresh the accounts list
    } catch (error) {
      console.error('Error deleting account:', error);
      const errorMessage = error.response?.data?.error || 'Failed to delete account. Please try again.';
      setError(errorMessage);
      setDeleteDialogOpen(false);
    }
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setAccountToDelete(null);
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Accounts
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

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/accounts/new')}
        >
          Create Account
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accounts.length > 0 ? (
              accounts
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((account, index) => (
                <TableRow key={account.id || index}>
                  <TableCell>{account.name || ''}</TableCell>
                  <TableCell>{account.description || ''}</TableCell>
                  <TableCell>
                    <IconButton
                      color="primary"
                      onClick={() => handleEditAccount(account.id || index + 1)}
                      aria-label="edit account"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteAccount(account)}
                      aria-label="delete account"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No accounts found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={closeDeleteDialog}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Account
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete the account "{accountToDelete?.name}"?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmDeleteAccount} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AccountsList;
