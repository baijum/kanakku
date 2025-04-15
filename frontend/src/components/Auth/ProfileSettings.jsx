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
import { add } from 'date-fns';

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

        const response = await fetch('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        setUser(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);
  
  const fetchTokens = async () => {
    setLoadingTokens(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch('/api/auth/tokens', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        // If it's a 404, it's not an error - the user just doesn't have tokens yet
        if (response.status === 404) {
          setTokens([]);
          return;
        }
        
        // Try to get more detailed error information
        const errorData = await response.json().catch(() => null);
        if (errorData && errorData.error) {
          throw new Error(errorData.error);
        }
        
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setTokens(data);
      // Clear any previous errors when successful
      setTokenError(null);
    } catch (err) {
      // Don't show connection errors if we're in the background
      if (!document.hasFocus() && err.message.includes('Failed to fetch')) {
        console.warn('Background token fetch failed:', err.message);
        return;
      }
      
      setTokenError(err.message);
    } finally {
      setLoadingTokens(false);
    }
  };
  
  useEffect(() => {
    if (tabValue === 1) {
      fetchTokens();
    }
  }, [tabValue]);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }
      
      const response = await fetch('/api/auth/test', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        console.log('Authentication test successful:', data);
        alert('Authentication test successful. Your token is valid.');
        // Retry token fetch
        fetchTokens();
      } else {
        console.error('Authentication test failed:', data);
        alert(`Authentication test failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Authentication test error:', err);
      alert(`Authentication test error: ${err.message}`);
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
      
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      // Prepare payload
      const payload = {
        name: tokenName,
      };
      
      // Add expiry date if set
      if (expiryDate) {
        payload.expires_at = expiryDate.toISOString();
      }
      
      const response = await fetch('/api/auth/tokens', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create token');
      }
      
      const newToken = await response.json();
      
      // Show the newly created token value
      setNewTokenValue(newToken.token);
      setShowNewToken(true);
      
      // Reset form
      setTokenName('');
      setExpiryDate(null);
      setExpiryOption('never');
      
      // Refresh token list
      fetchTokens();
      
    } catch (err) {
      setTokenError(err.message);
    }
  };
  
  const handleDeleteToken = (tokenId) => {
    setTokenToDelete(tokenId);
    setDeleteDialogOpen(true);
  };
  
  const confirmDeleteToken = async () => {
    try {
      const jwtToken = localStorage.getItem('token');
      
      const response = await fetch(`/api/auth/tokens/${tokenToDelete}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${jwtToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete token');
      }
      
      // Remove the deleted token from state
      setTokens(tokens.filter(token => token.id !== tokenToDelete));
      
    } catch (err) {
      setTokenError(err.message);
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
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Profile Settings
        </Typography>
        {user && (
          <Box mb={3}>
            <Typography variant="body1">
              <strong>Email:</strong> {user.email}
            </Typography>
          </Box>
        )}
      </Paper>

      <Paper elevation={3}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="Change Password" />
          <Tab label="API Tokens" />
        </Tabs>
        <Divider />
        
        <Box p={3}>
          {tabValue === 0 && <UpdatePassword />}
          
          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                API Access Tokens
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Create API tokens to access your account programmatically. Tokens can be set to expire automatically.
              </Typography>
              
              {tokenError && !loadingTokens && (
                <Alert 
                  severity="error" 
                  sx={{ mb: 2 }}
                  action={
                    <Button 
                      color="inherit" 
                      size="small"
                      onClick={checkAuthStatus}
                    >
                      Test Auth
                    </Button>
                  }
                >
                  {tokenError}
                </Alert>
              )}
              
              {showNewToken && (
                <Alert 
                  severity="info" 
                  sx={{ mb: 3 }}
                  action={
                    <IconButton 
                      aria-label="copy" 
                      color="inherit" 
                      size="small"
                      onClick={copyTokenToClipboard}
                    >
                      <ContentCopyIcon />
                    </IconButton>
                  }
                >
                  <Typography variant="body2">
                    Your new token: <strong>{newTokenValue}</strong>
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Make sure to copy this token now. You won't be able to see it again!
                  </Typography>
                </Alert>
              )}
              
              <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Create a New Token
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <TextField
                    label="Token Name"
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    fullWidth
                    placeholder="e.g., Development, Data Import, etc."
                    variant="outlined"
                    size="small"
                  />
                  
                  <FormControl fullWidth size="small">
                    <InputLabel>Expiration</InputLabel>
                    <Select
                      value={expiryOption}
                      onChange={handleExpiryOptionChange}
                      label="Expiration"
                    >
                      <MenuItem value="never">Never expires</MenuItem>
                      <MenuItem value="30days">30 days</MenuItem>
                      <MenuItem value="90days">90 days</MenuItem>
                      <MenuItem value="1year">1 year</MenuItem>
                      <MenuItem value="custom">Custom date</MenuItem>
                    </Select>
                  </FormControl>
                  
                  {expiryOption === 'custom' && (
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                      <DatePicker
                        label="Expiry Date"
                        value={expiryDate}
                        onChange={(date) => setExpiryDate(date)}
                        renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                        disablePast
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
              
              <Typography variant="subtitle1" gutterBottom>
                Your Tokens
              </Typography>
              
              {loadingTokens ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : tokens.length === 0 ? (
                <Typography variant="body2" color="textSecondary">
                  You don't have any tokens yet.
                </Typography>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Name</strong></TableCell>
                        <TableCell><strong>Created</strong></TableCell>
                        <TableCell><strong>Expires</strong></TableCell>
                        <TableCell><strong>Last Used</strong></TableCell>
                        <TableCell></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tokens.map((token) => (
                        <TableRow key={token.id}>
                          <TableCell>{token.name}</TableCell>
                          <TableCell>{new Date(token.created_at).toLocaleDateString()}</TableCell>
                          <TableCell>
                            {token.expires_at 
                              ? new Date(token.expires_at).toLocaleDateString()
                              : 'Never'}
                          </TableCell>
                          <TableCell>
                            {token.last_used_at
                              ? new Date(token.last_used_at).toLocaleDateString()
                              : 'Never used'}
                          </TableCell>
                          <TableCell>
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDeleteToken(token.id)}
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
              
              {/* Delete confirmation dialog */}
              <Dialog
                open={deleteDialogOpen}
                onClose={() => setDeleteDialogOpen(false)}
              >
                <DialogTitle>Delete Token</DialogTitle>
                <DialogContent>
                  <DialogContentText>
                    Are you sure you want to delete this API token? 
                    This action cannot be undone and applications using this token will no longer be able to access your account.
                  </DialogContentText>
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                  <Button onClick={confirmDeleteToken} color="error" autoFocus>
                    Delete
                  </Button>
                </DialogActions>
              </Dialog>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default ProfileSettings; 