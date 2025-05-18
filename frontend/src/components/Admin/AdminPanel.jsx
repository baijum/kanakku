import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Alert,
  CircularProgress,
} from '@mui/material';
import UserManagement from './UserManagement';
import GlobalSettings from './GlobalSettings';
import axiosInstance from '../../api/axiosInstance';

const AdminPanel = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await axiosInstance.get('/api/v1/auth/me');
        if (response.data && response.data.is_admin) {
          setIsAdmin(true);
        } else {
          setError('You do not have administrator privileges to access this page.');
        }
      } catch (err) {
        setError(err.response?.data?.error || err.message || 'Failed to verify admin status');
      } finally {
        setLoading(false);
      }
    };

    checkAdminStatus();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 10 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 10 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!isAdmin) {
    return (
      <Container maxWidth="lg" sx={{ mt: 10 }}>
        <Alert severity="warning">
          This page is restricted to administrators only.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 10, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Panel
      </Typography>
      
      <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="User Management" />
            <Tab label="Global Settings" />
            {/* Add more admin tabs here as needed */}
          </Tabs>
        </Box>
        
        {tabValue === 0 && (
          <UserManagement />
        )}
        
        {tabValue === 1 && (
          <GlobalSettings />
        )}
        
        {/* Add more tab panels here as needed */}
      </Paper>
    </Container>
  );
};

export default AdminPanel; 