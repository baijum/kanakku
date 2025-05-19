import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  FormControlLabel,
  Switch,
  Tooltip,
  CircularProgress,
  Alert,
  Box,
  Snackbar
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import axiosInstance from '../../api/axiosInstance';

const GlobalSettings = () => {
  const [configurations, setConfigurations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [formData, setFormData] = useState({
    key: '',
    value: '',
    description: '',
    is_encrypted: true
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/v1/settings/global');
      setConfigurations(response.data.configurations || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch global configurations');
      console.error('Error fetching configurations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'is_encrypted' ? checked : value
    });
  };

  const handleAddConfiguration = async () => {
    try {
      await axiosInstance.post('/api/v1/settings/global', formData);
      setOpenAddDialog(false);
      setFormData({ key: '', value: '', description: '', is_encrypted: true });
      setSnackbar({
        open: true,
        message: 'Configuration added successfully',
        severity: 'success'
      });
      fetchConfigurations();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.error || 'Failed to add configuration',
        severity: 'error'
      });
    }
  };

  const handleEditConfiguration = async () => {
    try {
      await axiosInstance.put(`/api/v1/settings/global/${selectedConfig.key}`, {
        value: formData.value,
        description: formData.description,
        is_encrypted: formData.is_encrypted
      });
      setOpenEditDialog(false);
      setSnackbar({
        open: true,
        message: 'Configuration updated successfully',
        severity: 'success'
      });
      fetchConfigurations();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.error || 'Failed to update configuration',
        severity: 'error'
      });
    }
  };

  const handleDeleteConfiguration = async () => {
    try {
      await axiosInstance.delete(`/api/v1/settings/global/${selectedConfig.key}`);
      setOpenDeleteDialog(false);
      setSnackbar({
        open: true,
        message: 'Configuration deleted successfully',
        severity: 'success'
      });
      fetchConfigurations();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.error || 'Failed to delete configuration',
        severity: 'error'
      });
    }
  };

  const handleViewDecryptedValue = async () => {
    try {
      const response = await axiosInstance.get(`/api/v1/settings/global/${selectedConfig.key}/value`);
      setSelectedConfig({
        ...selectedConfig,
        decryptedValue: response.data.value
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.error || 'Failed to view decrypted value',
        severity: 'error'
      });
    }
  };

  const openEditDialogWithConfig = (config) => {
    setSelectedConfig(config);
    setFormData({
      key: config.key,
      value: '',  // We don't show the actual value for security reasons
      description: config.description || '',
      is_encrypted: config.is_encrypted
    });
    setOpenEditDialog(true);
  };

  const openDeleteDialogWithConfig = (config) => {
    setSelectedConfig(config);
    setOpenDeleteDialog(true);
  };

  const openViewDialogWithConfig = (config) => {
    setSelectedConfig(config);
    setOpenViewDialog(true);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <div>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Global Configuration Settings</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenAddDialog(true)}
        >
          Add Configuration
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell>Key</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Encrypted</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {configurations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No configurations found. Create a new one to get started.
                </TableCell>
              </TableRow>
            ) : (
              configurations.map((config) => (
                <TableRow key={config.id}>
                  <TableCell>{config.key}</TableCell>
                  <TableCell>{config.description || 'No description'}</TableCell>
                  <TableCell>{config.is_encrypted ? 'Yes' : 'No'}</TableCell>
                  <TableCell>
                    {new Date(config.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {config.updated_at
                      ? new Date(config.updated_at).toLocaleDateString()
                      : 'Never'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => openEditDialogWithConfig(config)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    {config.is_encrypted && (
                      <Tooltip title="View Value">
                        <IconButton
                          size="small"
                          onClick={() => openViewDialogWithConfig(config)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => openDeleteDialogWithConfig(config)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Configuration Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>Add New Configuration</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create a new global configuration setting. Use a descriptive key to identify
            the configuration's purpose.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="key"
            name="key"
            label="Key"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.key}
            onChange={handleInputChange}
            helperText="Unique identifier for this configuration"
            required
          />
          <TextField
            margin="dense"
            id="value"
            name="value"
            label="Value"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.value}
            onChange={handleInputChange}
            helperText="The configuration value"
            required
          />
          <TextField
            margin="dense"
            id="description"
            name="description"
            label="Description"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={handleInputChange}
            helperText="Optional description for this configuration"
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_encrypted}
                onChange={handleInputChange}
                name="is_encrypted"
              />
            }
            label="Encrypt Value (recommended for sensitive data)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddConfiguration}
            variant="contained"
            color="primary"
            disabled={!formData.key || !formData.value}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Configuration Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)}>
        <DialogTitle>Edit Configuration</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Update the configuration value or description. The key cannot be modified.
          </DialogContentText>
          <TextField
            margin="dense"
            label="Key"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.key}
            disabled
          />
          <TextField
            margin="dense"
            id="value"
            name="value"
            label="New Value"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.value}
            onChange={handleInputChange}
            helperText="Enter the new value. For security, the current value is not displayed."
            required
          />
          <TextField
            margin="dense"
            id="description"
            name="description"
            label="Description"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={handleInputChange}
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_encrypted}
                onChange={handleInputChange}
                name="is_encrypted"
              />
            }
            label="Encrypt Value"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button
            onClick={handleEditConfiguration}
            variant="contained"
            color="primary"
            disabled={!formData.value}
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Configuration Dialog */}
      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
        <DialogTitle>Delete Configuration</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the configuration with key{' '}
            <strong>{selectedConfig?.key}</strong>? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfiguration}
            variant="contained"
            color="error"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Decrypted Value Dialog */}
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)}>
        <DialogTitle>View Configuration Value</DialogTitle>
        <DialogContent>
          <DialogContentText>
            View the current value for configuration <strong>{selectedConfig?.key}</strong>:
          </DialogContentText>
          {selectedConfig?.decryptedValue ? (
            <TextField
              margin="dense"
              label="Value"
              type="text"
              fullWidth
              variant="outlined"
              value={selectedConfig.decryptedValue}
              InputProps={{
                readOnly: true,
              }}
            />
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <Button
                variant="contained"
                onClick={handleViewDecryptedValue}
                startIcon={<VisibilityIcon />}
              >
                Show Value
              </Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setOpenViewDialog(false);
            setSelectedConfig({...selectedConfig, decryptedValue: null});
          }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default GlobalSettings; 