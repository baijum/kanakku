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
} from '@mui/material';
import UpdatePassword from './UpdatePassword';

const ProfileSettings = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

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

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
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
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>Username:</strong> {user.username}
            </Typography>
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
          {/* Add more tabs for future settings options */}
        </Tabs>
        <Divider />
        
        <Box p={3}>
          {tabValue === 0 && <UpdatePassword />}
          {/* Additional tabs content will go here */}
        </Box>
      </Paper>
    </Container>
  );
};

export default ProfileSettings; 