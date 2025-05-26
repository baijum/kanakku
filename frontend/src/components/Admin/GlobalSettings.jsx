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
  Snackbar,
  Card,
  CardContent,
  CardActions,
  Chip,
  Link,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import InfoIcon from '@mui/icons-material/Info';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
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

  // Common configuration templates
  const configTemplates = [
    {
      key: 'GEMINI_API_TOKEN',
      description: 'Google Gemini API Token for email processing',
      placeholder: 'AIzaSy...',
      helpText: 'Get your API key from Google AI Studio (https://aistudio.google.com/app/apikey)',
      is_encrypted: true,
      required: true
    }
  ];

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

  const validateGeminiApiToken = (token) => {
    // Basic validation for Gemini API token format
    if (!token) return 'API token is required';
    if (!token.startsWith('AIzaSy')) return 'Gemini API tokens should start with "AIzaSy"';
    if (token.length < 30) return 'API token appears to be too short';
    return null;
  };

  const handleAddConfiguration = async () => {
    try {
      // Validate Gemini API token if that's what we're adding
      if (formData.key === 'GEMINI_API_TOKEN') {
        const validationError = validateGeminiApiToken(formData.value);
        if (validationError) {
          setSnackbar({
            open: true,
            message: validationError,
            severity: 'error'
          });
          return;
        }
      }

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
      // Validate Gemini API token if that's what we're editing
      if (selectedConfig.key === 'GEMINI_API_TOKEN') {
        const validationError = validateGeminiApiToken(formData.value);
        if (validationError) {
          setSnackbar({
            open: true,
            message: validationError,
            severity: 'error'
          });
          return;
        }
      }

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

  const handleQuickSetup = (template) => {
    setFormData({
      key: template.key,
      value: '',
      description: template.description,
      is_encrypted: template.is_encrypted
    });
    setOpenAddDialog(true);
  };

  const isConfigurationExists = (key) => {
    return configurations.some(config => config.key === key);
  };

  const getConfigurationStatus = (key) => {
    const config = configurations.find(c => c.key === key);
    return config ? 'configured' : 'missing';
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

      {/* Quick Setup Section */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Quick Setup</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Configure essential settings for your application features.
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {configTemplates.map((template) => (
              <Card key={template.key} variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" component="div">
                      {template.key.replace(/_/g, ' ')}
                    </Typography>
                    <Chip
                      icon={getConfigurationStatus(template.key) === 'configured' ? <CheckCircleIcon /> : <InfoIcon />}
                      label={getConfigurationStatus(template.key) === 'configured' ? 'Configured' : 'Not Configured'}
                      color={getConfigurationStatus(template.key) === 'configured' ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {template.description}
                  </Typography>
                  {template.helpText && (
                    <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                      {template.helpText.includes('http') ? (
                        <>
                          Get your API key from{' '}
                          <Link href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener">
                            Google AI Studio
                          </Link>
                        </>
                      ) : (
                        template.helpText
                      )}
                    </Typography>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    variant={getConfigurationStatus(template.key) === 'configured' ? 'outlined' : 'contained'}
                    onClick={() => handleQuickSetup(template)}
                    disabled={isConfigurationExists(template.key)}
                  >
                    {getConfigurationStatus(template.key) === 'configured' ? 'Reconfigure' : 'Configure'}
                  </Button>
                </CardActions>
              </Card>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>

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
                  No configurations found. Use the Quick Setup section above or create a new one to get started.
                </TableCell>
              </TableRow>
            ) : (
              configurations.map((config) => (
                <TableRow key={config.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {config.key}
                      {config.key === 'GEMINI_API_TOKEN' && (
                        <Chip label="Email Processing" size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                  </TableCell>
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
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)} maxWidth="sm" fullWidth>
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
            helperText="Unique identifier for this configuration (e.g., GEMINI_API_TOKEN)"
            required
          />
          <TextField
            margin="dense"
            id="value"
            name="value"
            label="Value"
            type={formData.key === 'GEMINI_API_TOKEN' ? 'password' : 'text'}
            fullWidth
            variant="outlined"
            value={formData.value}
            onChange={handleInputChange}
            helperText={
              formData.key === 'GEMINI_API_TOKEN'
                ? 'Enter your Google Gemini API token (starts with AIzaSy...)'
                : 'The configuration value'
            }
            placeholder={
              formData.key === 'GEMINI_API_TOKEN'
                ? 'AIzaSy...'
                : ''
            }
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
            label="Encrypt Value (recommended for sensitive data like API tokens)"
          />
          {formData.key === 'GEMINI_API_TOKEN' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                The Gemini API token is required for automated email processing features.
                Get your API key from{' '}
                <Link href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener">
                  Google AI Studio
                </Link>.
              </Typography>
            </Alert>
          )}
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
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
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
            type={selectedConfig?.key === 'GEMINI_API_TOKEN' ? 'password' : 'text'}
            fullWidth
            variant="outlined"
            value={formData.value}
            onChange={handleInputChange}
            helperText={
              selectedConfig?.key === 'GEMINI_API_TOKEN'
                ? 'Enter your new Google Gemini API token. For security, the current value is not displayed.'
                : 'Enter the new value. For security, the current value is not displayed.'
            }
            placeholder={
              selectedConfig?.key === 'GEMINI_API_TOKEN'
                ? 'AIzaSy...'
                : ''
            }
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
            {selectedConfig?.key === 'GEMINI_API_TOKEN' && (
              <>
                <br /><br />
                <strong>Warning:</strong> Deleting this configuration will disable automated email processing features.
              </>
            )}
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
      <Dialog open={openViewDialog} onClose={() => setOpenViewDialog(false)} maxWidth="sm" fullWidth>
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
              sx={{ mt: 2 }}
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
          {selectedConfig?.key === 'GEMINI_API_TOKEN' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                Keep your API token secure and do not share it with others.
              </Typography>
            </Alert>
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
