import React, { useState, useEffect } from 'react';
import {
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Switch,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Chip,
} from '@mui/material';
import axiosInstance from '../../api/axiosInstance';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [userToModify, setUserToModify] = useState(null);
  const [newStatus, setNewStatus] = useState(null);

  // Load all users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axiosInstance.get('/api/v1/auth/users');
      setUsers(response.data.users);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('You do not have admin privileges to view this page.');
      } else {
        setError(err.response?.data?.error || err.message || 'Failed to load users');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = (user, newActiveStatus) => {
    setUserToModify(user);
    setNewStatus(newActiveStatus);
    setConfirmDialogOpen(true);
  };

  const confirmStatusChange = async () => {
    if (!userToModify || newStatus === null) return;
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await axiosInstance.post(
        `/api/v1/auth/users/${userToModify.id}/activate`,
        { is_active: newStatus }
      );
      
      // Update the user in the state
      setUsers(users.map(user => 
        user.id === userToModify.id 
          ? { ...user, is_active: newStatus } 
          : user
      ));
      
      setSuccess(response.data.message);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to update user status');
    } finally {
      setLoading(false);
      setConfirmDialogOpen(false);
      setUserToModify(null);
      setNewStatus(null);
    }
  };

  if (loading && users.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && users.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        User Management
      </Typography>
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert 
          severity="success" 
          sx={{ mb: 2 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}
      
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.is_active ? "Active" : "Inactive"} 
                      color={user.is_active ? "success" : "error"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.is_admin ? "Admin" : "User"} 
                      color={user.is_admin ? "primary" : "default"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Switch
                        checked={user.is_active}
                        onChange={() => handleToggleStatus(user, !user.is_active)}
                        color={user.is_active ? "success" : "error"}
                        size="small"
                      />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {user.is_active ? "Deactivate" : "Activate"}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
      >
        <DialogTitle>
          {newStatus ? "Activate User" : "Deactivate User"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {newStatus 
              ? `Are you sure you want to activate the account for ${userToModify?.email}?`
              : `Are you sure you want to deactivate the account for ${userToModify?.email}? They will no longer be able to log in.`
            }
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={confirmStatusChange}
            color={newStatus ? "success" : "error"}
            variant="contained"
          >
            {newStatus ? "Activate" : "Deactivate"}
          </Button>
        </DialogActions>
      </Dialog>

      <Box sx={{ mt: 2 }}>
        <Button 
          variant="outlined" 
          onClick={fetchUsers}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} sx={{ mr: 1 }} /> : null}
          Refresh User List
        </Button>
      </Box>
    </Box>
  );
};

export default UserManagement; 