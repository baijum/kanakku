import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save as SaveIcon,
  Science as TestIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import axiosInstance from '../../api/axiosInstance';

const EmailAutomation = () => {
  const [config, setConfig] = useState({
    is_enabled: false,
    email_address: '',
    app_password: '',
    imap_server: 'imap.gmail.com',
    imap_port: 993,
    polling_interval: 'hourly',
    sample_emails: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [status, setStatus] = useState(null);
  const [sampleEmailDialog, setSampleEmailDialog] = useState(false);
  const [newSampleEmail, setNewSampleEmail] = useState('');

  useEffect(() => {
    fetchConfig();
    fetchStatus();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/v1/email-automation/config');
      if (response.data.config) {
        setConfig({
          ...response.data.config,
          app_password: '', // Don't populate password field for security
          sample_emails: response.data.config.sample_emails || []
        });
      }
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch email configuration');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/email-automation/status');
      setStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      // Validate required fields
      if (!config.email_address) {
        setError('Email address is required');
        return;
      }

      if (!config.app_password && !config.id) {
        setError('App password is required for new configurations');
        return;
      }

      const payload = { ...config };
      
      // Only include app_password if it's been changed
      if (!config.app_password) {
        delete payload.app_password;
      }

      const response = await axiosInstance.post('/api/v1/email-automation/config', payload);
      
      setSuccess('Email configuration saved successfully');
      setConfig(prev => ({
        ...prev,
        ...response.data.config,
        app_password: '' // Clear password field after save
      }));
      
      // Refresh status
      fetchStatus();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setError(null);
      setSuccess(null);

      if (!config.email_address || !config.app_password) {
        setError('Email address and app password are required for testing');
        return;
      }

      const response = await axiosInstance.post('/api/v1/email-automation/test-connection', {
        email_address: config.email_address,
        app_password: config.app_password,
        imap_server: config.imap_server,
        imap_port: config.imap_port
      });

      if (response.data.success) {
        setSuccess('Connection test successful! Your email settings are working correctly.');
      } else {
        setError(response.data.error || 'Connection test failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Connection test failed');
    } finally {
      setTesting(false);
    }
  };

  const handleTriggerProcessing = async () => {
    try {
      setTriggering(true);
      setError(null);
      setSuccess(null);

      const response = await axiosInstance.post('/api/v1/email-automation/trigger');
      
      if (response.data.success) {
        setSuccess(`Email processing job queued successfully. Job ID: ${response.data.job_id}`);
        // Refresh status after a short delay
        setTimeout(fetchStatus, 2000);
      } else {
        setError(response.data.error || 'Failed to trigger email processing');
      }
    } catch (err) {
      if (err.response?.status === 409) {
        // Conflict - job already pending
        const jobStatus = err.response.data.job_status;
        let statusMessage = 'An email processing job is already pending for your account.';
        
        if (jobStatus) {
          const statusParts = [];
          if (jobStatus.has_running_job) statusParts.push('running');
          if (jobStatus.has_scheduled_job) statusParts.push('scheduled');
          if (jobStatus.has_queued_job) statusParts.push('queued');
          
          if (statusParts.length > 0) {
            statusMessage += ` Status: ${statusParts.join(', ')}.`;
          }
        }
        
        setError(statusMessage);
      } else {
        setError(err.response?.data?.error || 'Failed to trigger email processing');
      }
    } finally {
      setTriggering(false);
    }
  };

  const handleAddSampleEmail = () => {
    if (newSampleEmail.trim()) {
      setConfig(prev => ({
        ...prev,
        sample_emails: [...prev.sample_emails, newSampleEmail.trim()]
      }));
      setNewSampleEmail('');
      setSampleEmailDialog(false);
    }
  };

  const handleRemoveSampleEmail = (index) => {
    setConfig(prev => ({
      ...prev,
      sample_emails: prev.sample_emails.filter((_, i) => i !== index)
    }));
  };

  const getStatusColor = (status) => {
    switch (status?.status) {
      case 'enabled': return 'success';
      case 'disabled': return 'warning';
      case 'not_configured': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Email Automation Settings
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Status Section */}
      {status && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Current Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Chip 
              label={status.status || 'Unknown'} 
              color={getStatusColor(status)}
              size="small"
            />
            {status.email_address && (
              <Typography variant="body2" color="text.secondary">
                {status.email_address}
              </Typography>
            )}
          </Box>
          {status.last_check && (
            <Typography variant="body2" color="text.secondary">
              Last checked: {new Date(status.last_check).toLocaleString()}
            </Typography>
          )}
          {status.polling_interval && (
            <Typography variant="body2" color="text.secondary">
              Polling interval: {status.polling_interval}
            </Typography>
          )}
        </Paper>
      )}

      <Paper sx={{ p: 3 }}>
        {/* Enable/Disable Toggle */}
        <FormControlLabel
          control={
            <Switch
              checked={config.is_enabled}
              onChange={(e) => handleInputChange('is_enabled', e.target.checked)}
            />
          }
          label="Enable Email Automation"
          sx={{ mb: 3 }}
        />

        <Divider sx={{ mb: 3 }} />

        {/* Email Configuration */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Gmail Email Address"
              value={config.email_address}
              onChange={(e) => handleInputChange('email_address', e.target.value)}
              type="email"
              required
              helperText="Your Gmail address for bank transaction emails"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Gmail App Password"
              value={config.app_password}
              onChange={(e) => handleInputChange('app_password', e.target.value)}
              type="password"
              required={!config.id}
              helperText="Generate an app password in your Google Account settings"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="IMAP Server"
              value={config.imap_server}
              onChange={(e) => handleInputChange('imap_server', e.target.value)}
              helperText="Usually imap.gmail.com for Gmail"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="IMAP Port"
              value={config.imap_port}
              onChange={(e) => handleInputChange('imap_port', parseInt(e.target.value) || 993)}
              type="number"
              helperText="Usually 993 for SSL/TLS"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Polling Interval</InputLabel>
              <Select
                value={config.polling_interval}
                onChange={(e) => handleInputChange('polling_interval', e.target.value)}
                label="Polling Interval"
              >
                <MenuItem value="hourly">Hourly</MenuItem>
                <MenuItem value="daily">Daily</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Sample Emails Section */}
        <Accordion sx={{ mt: 3 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">
              Sample Transaction Emails ({config.sample_emails.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add sample bank transaction emails to improve AI accuracy. These examples help the system 
              better understand your bank's email format.
            </Typography>
            
            <Button
              startIcon={<AddIcon />}
              onClick={() => setSampleEmailDialog(true)}
              variant="outlined"
              size="small"
              sx={{ mb: 2 }}
            >
              Add Sample Email
            </Button>

            {config.sample_emails.length > 0 && (
              <List dense>
                {config.sample_emails.map((email, index) => (
                  <ListItem key={index} divider>
                    <ListItemText
                      primary={`Sample ${index + 1}`}
                      secondary={email.substring(0, 100) + (email.length > 100 ? '...' : '')}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveSampleEmail(index)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 3, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
          >
            Save Configuration
          </Button>

          <Button
            variant="outlined"
            startIcon={testing ? <CircularProgress size={20} /> : <TestIcon />}
            onClick={handleTestConnection}
            disabled={testing || !config.email_address || !config.app_password}
          >
            Test Connection
          </Button>

          {config.is_enabled && config.id && (
            <Button
              variant="outlined"
              color="secondary"
              startIcon={triggering ? <CircularProgress size={20} /> : <PlayIcon />}
              onClick={handleTriggerProcessing}
              disabled={triggering}
            >
              Trigger Processing
            </Button>
          )}
        </Box>

        {/* Help Section */}
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            <InfoIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Setup Instructions:
          </Typography>
          <Typography variant="body2" component="div">
            1. Enable 2-factor authentication on your Gmail account<br />
            2. Generate an app password: Google Account → Security → App passwords<br />
            3. Use your Gmail address and the generated app password above<br />
            4. Test the connection before enabling automation<br />
            5. Add sample transaction emails to improve accuracy
          </Typography>
        </Alert>
      </Paper>

      {/* Sample Email Dialog */}
      <Dialog 
        open={sampleEmailDialog} 
        onClose={() => setSampleEmailDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add Sample Transaction Email</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Email Content"
            value={newSampleEmail}
            onChange={(e) => setNewSampleEmail(e.target.value)}
            placeholder="Paste the full content of a bank transaction email here..."
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSampleEmailDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddSampleEmail}
            variant="contained"
            disabled={!newSampleEmail.trim()}
          >
            Add Sample
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailAutomation; 