import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Divider,
  Alert,
  CircularProgress,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import UpdatePassword from './UpdatePassword';
import BookManagement from '../Books/BookManagement';
import { add } from 'date-fns';
import axiosInstance from '../../api/axiosInstance'; // Import the configured instance

const ProfileSettings = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Token state
  const [tokens, setTokens] = useState([]);
  const [loadingTokens, setLoadingTokens] = useState(false);
  const [tokenName, setTokenName] = useState('');
  const [expiryDate, setExpiryDate] = useState(null);
  const [expiryOption, setExpiryOption] = useState('never');
  const [newTokenValue, setNewTokenValue] = useState(null);
  const [showNewToken, setShowNewToken] = useState(false);
  const [tokenError, setTokenError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [tokenToDelete, setTokenToDelete] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('Not authenticated');
        }

        // Use axiosInstance instead of fetch
        const response = await axiosInstance.get('/api/v1/auth/me');
        setUser(response.data);
      } catch (err) {
        setError(err.response?.data?.error || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);
  
  const fetchTokens = async () => {
    setLoadingTokens(true);
    try {
      // Use axiosInstance instead of fetch
      const response = await axiosInstance.get('/api/v1/auth/tokens');
      setTokens(response.data);
      // Clear any previous errors when successful
      setTokenError(null);
    } catch (err) {
      // Don't show connection errors if we're in the background
      if (!document.hasFocus() && err.message?.includes('Network Error')) {
        console.warn('Background token fetch failed:', err.message);
        return;
      }
      
      // If it's a 404, it's not an error - the user just doesn't have tokens yet
      if (err.response?.status === 404) {
        setTokens([]);
        setTokenError(null);
        return;
      }
      
      setTokenError(err.response?.data?.error || err.message);
    } finally {
      setLoadingTokens(false);
    }
  };
  
  useEffect(() => {
    if (tabValue === 2) {
      fetchTokens();
    }
  }, [tabValue]);

  const checkAuthStatus = async () => {
    try {
      // Use axiosInstance instead of fetch
      await axiosInstance.get('/api/v1/auth/test');
      alert('Authentication test successful. Your token is valid.');
      // Retry token fetch
      fetchTokens();
    } catch (err) {
      console.error('Authentication test error:', err);
      alert(`Authentication test error: ${err.response?.data?.error || err.message}`);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleExpiryOptionChange = (event) => {
    const value = event.target.value;
    setExpiryOption(value);
    
    // Set expiry date based on option
    if (value === 'never') {
      setExpiryDate(null);
    } else if (value === '30days') {
      setExpiryDate(add(new Date(), { days: 30 }));
    } else if (value === '90days') {
      setExpiryDate(add(new Date(), { days: 90 }));
    } else if (value === '1year') {
      setExpiryDate(add(new Date(), { days: 365 }));
    }
    // 'custom' option will use the date picker
  };
  
  const handleCreateToken = async () => {
    try {
      if (!tokenName) {
        setTokenError('Token name is required');
        return;
      }
      
      // Prepare payload
      const payload = {
        name: tokenName,
      };
      
      // Add expiry date if set
      if (expiryDate) {
        payload.expires_at = expiryDate.toISOString();
      }
      
      // Use axiosInstance instead of fetch
      const response = await axiosInstance.post('/api/v1/auth/tokens', payload);
      
      // Show the newly created token value
      setNewTokenValue(response.data.token);
      setShowNewToken(true);
      
      // Reset form
      setTokenName('');
      setExpiryDate(null);
      setExpiryOption('never');
      
      // Refresh token list
      fetchTokens();
      
    } catch (err) {
      setTokenError(err.response?.data?.error || err.message);
    }
  };
  
  const handleDeleteToken = (tokenId) => {
    setTokenToDelete(tokenId);
    setDeleteDialogOpen(true);
  };
  
  const confirmDeleteToken = async () => {
    try {
      // Use axiosInstance instead of fetch
      await axiosInstance.delete(`/api/v1/auth/tokens/${tokenToDelete}`);
      
      // Remove the deleted token from state
      setTokens(tokens.filter(token => token.id !== tokenToDelete));
      
    } catch (err) {
      setTokenError(err.response?.data?.error || err.message);
    } finally {
      setDeleteDialogOpen(false);
      setTokenToDelete(null);
    }
  };
  
  const copyTokenToClipboard = () => {
    if (newTokenValue) {
      navigator.clipboard.writeText(newTokenValue)
        .then(() => {
          alert('Token copied to clipboard');
        })
        .catch(() => {
          alert('Failed to copy token');
        });
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 10, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Profile Settings
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <>
          <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Account Information
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1">
                <strong>Email:</strong> {user?.email}
              </Typography>
              <Typography variant="body1">
                <strong>Account Created:</strong>{' '}
                {user?.created_at
                  ? new Date(user.created_at).toLocaleString()
                  : 'Unknown'}
              </Typography>
              <Typography variant="body1">
                <strong>Account Status:</strong>{' '}
                {user?.is_active ? 'Active' : 'Inactive'}
              </Typography>
            </Box>
          </Paper>

          <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3, width: '100%', overflow: 'hidden' }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                allowScrollButtonsMobile
                sx={{
                  '.MuiTab-root': {
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    minWidth: { xs: '80px', sm: '120px' },
                    py: { xs: 1 },
                    px: { xs: 1, sm: 2 }
                  }
                }}
              >
                <Tab label="Books" />
                <Tab label="Update Password" />
                <Tab label="API Tokens" />
              </Tabs>
            </Box>
            
            {tabValue === 0 && (
              <BookManagement />
            )}
            
            {tabValue === 1 && (
              <UpdatePassword />
            )}
            
            {tabValue === 2 && (
              <Box>
                {tokenError && (
                  <Alert 
                    severity="error" 
                    sx={{ mb: 2 }}
                    onClose={() => setTokenError(null)}
                  >
                    {tokenError}
                  </Alert>
                )}
                
                {/* API Token Creation Form */}
                <Paper elevation={0} sx={{ p: { xs: 2, sm: 3 }, mb: 4, bgcolor: 'background.paper' }}>
                  <Typography variant="h6" gutterBottom>
                    Create New API Token
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 1.5, sm: 2 }, maxWidth: 'sm' }}>
                    <TextField
                      label="Token Name"
                      value={tokenName}
                      onChange={(e) => setTokenName(e.target.value)}
                      fullWidth
                      required
                      size="small"
                      helperText="Give your token a descriptive name for its intended use"
                    />
                    
                    <FormControl fullWidth size="small">
                      <InputLabel>Expiration</InputLabel>
                      <Select
                        value={expiryOption}
                        onChange={handleExpiryOptionChange}
                        label="Expiration"
                      >
                        <MenuItem value="never">Never</MenuItem>
                        <MenuItem value="30days">30 Days</MenuItem>
                        <MenuItem value="90days">90 Days</MenuItem>
                        <MenuItem value="1year">1 Year</MenuItem>
                        <MenuItem value="custom">Custom Date</MenuItem>
                      </Select>
                    </FormControl>
                    
                    {expiryOption === 'custom' && (
                      <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DatePicker
                          label="Expiry Date"
                          value={expiryDate}
                          onChange={(newDate) => setExpiryDate(newDate)}
                          renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                          minDate={new Date()}
                        />
                      </LocalizationProvider>
                    )}
                    
                    <Button 
                      variant="contained" 
                      color="primary" 
                      onClick={handleCreateToken}
                      sx={{ alignSelf: 'flex-start' }}
                    >
                      Create Token
                    </Button>
                  </Box>
                </Paper>
                
                {/* Display newly created token */}
                {showNewToken && newTokenValue && (
                  <Paper elevation={0} sx={{ p: { xs: 2, sm: 3 }, mb: 4, bgcolor: 'background.paper' }}>
                    <Alert severity="success" sx={{ mb: 2 }}>
                      Token created successfully! Save this token now - you won't be able to see it again.
                    </Alert>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <TextField
                        value={newTokenValue}
                        variant="outlined"
                        fullWidth
                        size="small"
                        InputProps={{
                          readOnly: true,
                        }}
                      />
                      <IconButton 
                        color="primary"
                        onClick={() => copyTokenToClipboard()}
                        sx={{ ml: 1 }}
                      >
                        <ContentCopyIcon />
                      </IconButton>
                    </Box>
                    <Button 
                      variant="outlined" 
                      onClick={() => setShowNewToken(false)}
                      size="small"
                    >
                      Close
                    </Button>
                  </Paper>
                )}
                
                {/* Token List */}
                <Typography variant="h6" gutterBottom>
                  Your API Tokens
                </Typography>
                
                {loadingTokens ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                    <CircularProgress size={24} />
                  </Box>
                ) : tokens.length === 0 ? (
                  <Typography variant="body2" color="textSecondary">
                    You haven't created any API tokens yet. API tokens allow you to access your data
                    programmatically without having to log in through the web interface.
                  </Typography>
                ) : (
                  <TableContainer 
                    component={Paper} 
                    elevation={0}
                    sx={{ 
                      maxWidth: '100%', 
                      overflowX: 'auto' 
                    }}
                  >
                    <Table 
                      size="small"
                      sx={{ 
                        minWidth: { xs: 450, sm: 650 },
                        "& .MuiTableCell-root": { 
                          py: { xs: 1 }, 
                          px: { xs: 1, sm: 2 },
                          whiteSpace: { xs: 'nowrap' }
                        }
                      }}
                    >
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Name</strong></TableCell>
                          <TableCell><strong>Created</strong></TableCell>
                          <TableCell><strong>Last Used</strong></TableCell>
                          <TableCell><strong>Expires</strong></TableCell>
                          <TableCell><strong>Status</strong></TableCell>
                          <TableCell><strong>Actions</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tokens.map((token) => (
                          <TableRow key={token.id}>
                            <TableCell>{token.name}</TableCell>
                            <TableCell>
                              {new Date(token.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell>
                              {token.last_used_at 
                                ? new Date(token.last_used_at).toLocaleDateString()
                                : 'Never used'}
                            </TableCell>
                            <TableCell>
                              {token.expires_at 
                                ? new Date(token.expires_at).toLocaleDateString()
                                : 'Never'}
                            </TableCell>
                            <TableCell>
                              {token.is_active 
                                ? (token.expires_at && new Date(token.expires_at) < new Date() 
                                  ? 'Expired' 
                                  : 'Active')
                                : 'Revoked'}
                            </TableCell>
                            <TableCell>
                              <IconButton 
                                color="error" 
                                onClick={() => handleDeleteToken(token.id)}
                                size="small"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
                
                <Box sx={{ mt: 3 }}>
                  <Button 
                    variant="outlined" 
                    onClick={checkAuthStatus}
                    size="small"
                  >
                    Test Current Auth Token
                  </Button>
                  <Button
                    variant="text"
                    onClick={fetchTokens}
                    sx={{ ml: 2 }}
                    size="small"
                  >
                    Refresh Token List
                  </Button>
                </Box>
                
                {/* Delete Confirmation Dialog */}
                <Dialog
                  open={deleteDialogOpen}
                  onClose={() => setDeleteDialogOpen(false)}
                >
                  <DialogTitle>Delete Token</DialogTitle>
                  <DialogContent>
                    <DialogContentText>
                      Are you sure you want to delete this API token? This action cannot be undone.
                      Any applications using this token will no longer be able to access your account.
                    </DialogContentText>
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
                      Cancel
                    </Button>
                    <Button onClick={confirmDeleteToken} color="error">
                      Delete
                    </Button>
                  </DialogActions>
                </Dialog>
              </Box>
            )}
          </Paper>
        </>
      )}
    </Container>
  );
};

export default ProfileSettings; 