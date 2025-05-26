import React from 'react';
import { Box, Typography, Link, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 4,
        backgroundColor: (theme) =>
          theme.palette.mode === 'light'
            ? theme.palette.grey[200]
            : theme.palette.grey[800],
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' Kanakku - All rights reserved'}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          <Link component={RouterLink} color="inherit" to="/terms" sx={{ mx: 1 }}>
            Terms of Service
          </Link>
          {' | '}
          <Link component={RouterLink} color="inherit" to="/privacy" sx={{ mx: 1 }}>
            Privacy Statement
          </Link>
        </Typography>
      </Container>
    </Box>
  );
}

export default Footer;
