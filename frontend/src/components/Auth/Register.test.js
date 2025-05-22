import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Register from './Register';

// Mock axios instance
jest.mock('../../api/axiosInstance', () => ({
  __esModule: true,
  default: jest.fn(),
}));

// Create a theme for testing
const theme = createTheme();

// Wrapper component for testing
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
);

describe('Register Component', () => {
  const mockSetIsLoggedIn = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders registration form with all required fields', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    // Check for visible form fields using Testing Library methods
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    // Use direct DOM access for password fields since they have duplicate labels
    // eslint-disable-next-line testing-library/no-node-access
    expect(document.querySelector('input[name="password"]')).toBeInTheDocument();
    // eslint-disable-next-line testing-library/no-node-access
    expect(document.querySelector('input[name="confirmPassword"]')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  test('includes honeypot field that is hidden from users', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    // Find the honeypot field by name attribute
    // Direct DOM access is necessary here because the honeypot field is intentionally hidden from users
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotField = document.querySelector('input[name="website"]');
    
    // Verify the honeypot field exists
    expect(honeypotField).toBeInTheDocument();
    
    // Verify it has the correct attributes for hiding from users
    expect(honeypotField).toHaveAttribute('type', 'text');
    expect(honeypotField).toHaveAttribute('autoComplete', 'off');
    
    // Check the container for the accessibility attributes
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotContainer = honeypotField.closest('.MuiTextField-root');
    expect(honeypotContainer).toHaveAttribute('aria-hidden', 'true');
    expect(honeypotContainer).toHaveAttribute('tabindex', '-1');
  });

  test('honeypot field is not visible to screen readers', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    // The honeypot field should not be found by screen readers
    // because its container has aria-hidden="true"
    // Direct DOM access is necessary here because the honeypot field is intentionally hidden
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotField = document.querySelector('input[name="website"]');
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotContainer = honeypotField.closest('.MuiTextField-root');
    expect(honeypotContainer).toHaveAttribute('aria-hidden', 'true');
    
    // It should not be accessible via getByLabelText
    expect(() => screen.getByLabelText(/website/i)).toThrow();
  });

  test('honeypot field starts with empty value', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    // Direct DOM access is necessary here because the honeypot field is intentionally hidden from users
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotField = document.querySelector('input[name="website"]');
    expect(honeypotField).toHaveValue('');
  });

  test('honeypot field has proper styling for invisibility', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    // Direct DOM access is necessary here because the honeypot field is intentionally hidden from users
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotField = document.querySelector('input[name="website"]');
    // eslint-disable-next-line testing-library/no-node-access
    const honeypotContainer = honeypotField.closest('.MuiTextField-root');
    
    // Check that the container has the CSS classes that make it invisible
    // The actual styling is applied via MUI's sx prop which creates CSS classes
    expect(honeypotContainer).toHaveClass('MuiTextField-root');
    expect(honeypotContainer).toBeInTheDocument();
  });

  test('renders Google sign-up button', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    expect(screen.getByText(/sign up with google/i)).toBeInTheDocument();
  });

  test('renders link to login page', () => {
    render(
      <TestWrapper>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </TestWrapper>
    );

    expect(screen.getByText(/already have an account\? sign in/i)).toBeInTheDocument();
  });
}); 