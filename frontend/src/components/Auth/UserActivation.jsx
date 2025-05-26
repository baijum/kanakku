import React, { useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  Paper,
  Switch,
  FormControlLabel,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import axiosInstance from '../../api/axiosInstance';

const UserActivation = ({ user, onUserUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [pendingStatus, setPendingStatus] = useState(null);

  const handleToggleStatus = (newStatus) => {
    setPendingStatus(newStatus);
    setConfirmDialogOpen(true);
  };

  const confirmStatusChange = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await axiosInstance.post('/api/v1/auth/toggle-status', {
        is_active: pendingStatus
      });

      setSuccess(response.data.message);

      // Update the user in the parent component
      if (onUserUpdate && response.data.user) {
        onUserUpdate(response.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
      setConfirmDialogOpen(false);
    }
  };

  return (
    <Box>
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

      <Paper elevation={0} sx={{ p: { xs: 2, sm: 3 }, mb: 4, bgcolor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          Account Status
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" paragraph>
            Your account is currently <strong>{user?.is_active ? 'Active' : 'Inactive'}</strong>.
          </Typography>

          {user?.is_active ? (
            <Typography variant="body2" color="text.secondary" paragraph>
              An active account gives you access to all features of the application.
              If your account is deactivated, you won’t be able to log in until an
              administrator reactivates it.
            </Typography>
          ) : (
            <Typography variant="body2" color="text.secondary" paragraph>
              Your account is currently inactive. While inactive, you won't be able to log in.
              To reactivate your account, toggle the switch below.
            </Typography>
          )}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={!!user?.is_active}
                onChange={() => handleToggleStatus(!user?.is_active)}
                color={user?.is_active ? "primary" : "error"}
                disabled={loading}
              />
            }
            label={user?.is_active ? "Active" : "Inactive"}
          />

          {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
        </Box>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
      >
        <DialogTitle>
          {pendingStatus ? "Activate Account" : "Deactivate Account"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {pendingStatus
              ? "Are you sure you want to activate your account? This will allow you to log in and use all features."
              : "Are you sure you want to deactivate your account? You won't be able to log in until you reactivate it."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)} color="primary">
            Cancel
          </Button>
          <Button
            onClick={confirmStatusChange}
            color={pendingStatus ? "success" : "error"}
            variant="contained"
          >
            {pendingStatus ? "Activate" : "Deactivate"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserActivation;
