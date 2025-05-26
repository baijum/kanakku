import React from 'react';
import { Typography, Container, Paper } from '@mui/material';

function Privacy() {
  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Privacy Statement
        </Typography>

        <Typography variant="body1" paragraph>
          Last updated: {new Date().toLocaleDateString()}
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          1. Introduction
        </Typography>
        <Typography variant="body1" paragraph>
          At Kanakku, we respect your privacy and are committed to protecting your personal information. This Privacy Statement explains how we collect, use, disclose, and safeguard your information when you use our service.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          2. Information We Collect
        </Typography>
        <Typography variant="body1" paragraph>
          We collect information that you provide directly to us, such as when you create an account, enter financial data, or contact customer support. This may include your name, email address, financial transaction data, account information, and any other information you choose to provide.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          3. How We Use Your Information
        </Typography>
        <Typography variant="body1" paragraph>
          We use the information we collect to provide, maintain, and improve our services, to process your transactions, communicate with you, and to comply with legal obligations. We may also use anonymized data for analytical purposes to improve our service.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          4. Data Security
        </Typography>
        <Typography variant="body1" paragraph>
          We implement reasonable security measures designed to protect your personal information from unauthorized access, disclosure, alteration, and destruction. However, no method of transmission over the Internet or electronic storage is 100% secure.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          5. Data Retention
        </Typography>
        <Typography variant="body1" paragraph>
          We retain your personal information for as long as necessary to fulfill the purposes outlined in this Privacy Statement, unless a longer retention period is required or permitted by law.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          6. Your Rights
        </Typography>
        <Typography variant="body1" paragraph>
          Depending on your location, you may have certain rights regarding your personal information, such as the right to access, correct, or delete your data. Please contact us if you wish to exercise these rights.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          7. Third-Party Services
        </Typography>
        <Typography variant="body1" paragraph>
          Our service may contain links to third-party websites or services that are not owned or controlled by Kanakku. We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          8. Changes to This Privacy Statement
        </Typography>
        <Typography variant="body1" paragraph>
          We may update our Privacy Statement from time to time. We will notify you of any changes by posting the new Privacy Statement on this page and updating the "Last updated" date.
        </Typography>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          9. Contact Us
        </Typography>
        <Typography variant="body1" paragraph>
          If you have any questions or concerns about this Privacy Statement, please contact us at baiju.m.mail@gmail.com.
        </Typography>
      </Paper>
    </Container>
  );
}

export default Privacy;
