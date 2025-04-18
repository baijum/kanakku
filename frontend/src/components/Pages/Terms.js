import React from 'react';
import { Typography, Container, Paper } from '@mui/material';

function Terms() {
  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Terms of Service
        </Typography>
        
        <Typography variant="body1" paragraph>
          Last updated: {new Date().toLocaleDateString()}
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          1. Acceptance of Terms
        </Typography>
        <Typography variant="body1" paragraph>
          By accessing or using Kanakku, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the service.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          2. Description of Service
        </Typography>
        <Typography variant="body1" paragraph>
          Kanakku is a financial tracking and management application that allows users to track transactions, manage accounts, and generate financial reports.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          3. User Accounts
        </Typography>
        <Typography variant="body1" paragraph>
          To use certain features of Kanakku, you may be required to create an account. You are responsible for maintaining the confidentiality of your account information and for all activities that occur under your account.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          4. Privacy
        </Typography>
        <Typography variant="body1" paragraph>
          Your privacy is important to us. Please review our Privacy Statement to understand how we collect, use, and protect your information.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          5. Data Security
        </Typography>
        <Typography variant="body1" paragraph>
          We implement reasonable security measures to protect your data. However, we cannot guarantee absolute security. You are responsible for maintaining the security of your account credentials.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          6. Limitation of Liability
        </Typography>
        <Typography variant="body1" paragraph>
          To the maximum extent permitted by law, Kanakku shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          7. Changes to Terms
        </Typography>
        <Typography variant="body1" paragraph>
          We reserve the right to modify these terms at any time. We will provide notice of significant changes. Your continued use of Kanakku after such modifications constitutes your acceptance of the updated terms.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          8. Contact Information
        </Typography>
        <Typography variant="body1" paragraph>
          If you have any questions about these Terms, please contact us at baiju.m.mail@gmail.com.
        </Typography>
      </Paper>
    </Container>
  );
}

export default Terms; 