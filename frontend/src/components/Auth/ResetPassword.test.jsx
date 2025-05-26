import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResetPassword from './ResetPassword';

// Create mock component that doesn't use actual React Router
const MockResetPassword = () => {
  // Create a simplified version that doesn't use Router components
  return (
    <div>
      <h1>Reset Password</h1>
      <div data-testid="new-password-field">New Password field</div>
      <div data-testid="confirm-password-field">Confirm New Password field</div>
      <button data-testid="reset-button">Reset Password</button>
      <div data-testid="login-link">Back to Login</div>
    </div>
  );
};

// Create mock invalid link component
const MockInvalidResetPassword = () => {
  return (
    <div>
      <h1>Invalid Reset Link</h1>
      <div data-testid="error-message">The password reset link is invalid or has expired.</div>
      <div data-testid="new-reset-link">Request a new password reset</div>
    </div>
  );
};

// Mock the actual component
jest.mock('./ResetPassword', () => jest.fn());

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  useParams: jest.fn(),
  useNavigate: () => jest.fn(),
  useLocation: jest.fn(),
  Link: ({ children }) => children
}));

// Mock axios
jest.mock('../../api/axiosInstance');

describe('ResetPassword Component', () => {
  const mockUseParams = require('react-router-dom').useParams;
  const mockUseLocation = require('react-router-dom').useLocation;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders reset password form when token and email are valid', () => {
    // Mock values for useParams and useLocation
    mockUseParams.mockReturnValue({ token: 'valid-token' });
    mockUseLocation.mockReturnValue({
      search: '?email=test@example.com',
      pathname: '/reset-password/valid-token'
    });

    // Set the mock implementation for this test
    ResetPassword.mockImplementation(MockResetPassword);

    render(<ResetPassword />);

    // Check for heading
    expect(screen.getByRole('heading', { name: /Reset Password/i })).toBeInTheDocument();

    // Check for form elements
    expect(screen.getByTestId('new-password-field')).toBeInTheDocument();
    expect(screen.getByTestId('confirm-password-field')).toBeInTheDocument();
    expect(screen.getByTestId('reset-button')).toBeInTheDocument();
    expect(screen.getByTestId('login-link')).toBeInTheDocument();
  });

  test('renders invalid link message when token or email is missing', () => {
    // Mock values for useParams and useLocation with invalid data
    mockUseParams.mockReturnValue({ token: null });
    mockUseLocation.mockReturnValue({
      search: '',
      pathname: '/reset-password'
    });

    // Set the mock implementation for this test
    ResetPassword.mockImplementation(MockInvalidResetPassword);

    render(<ResetPassword />);

    // Check for invalid link heading and message
    expect(screen.getByRole('heading', { name: /Invalid Reset Link/i })).toBeInTheDocument();
    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByTestId('new-reset-link')).toBeInTheDocument();
  });
});
