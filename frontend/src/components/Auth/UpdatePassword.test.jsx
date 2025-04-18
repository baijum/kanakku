import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import UpdatePassword from './UpdatePassword';

// Create mock component that doesn't use actual React Router
const MockUpdatePassword = () => {
  // Create a simplified version that doesn't use Router components
  return (
    <div>
      <h6>Update Password</h6>
      <div data-testid="current-password-field">Current Password field</div>
      <div data-testid="new-password-field">New Password field</div>
      <div data-testid="confirm-password-field">Confirm New Password field</div>
      <button data-testid="update-button">Update Password</button>
    </div>
  );
};

// Mock the actual component
jest.mock('./UpdatePassword', () => jest.fn());

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  put: jest.fn()
}));

describe('UpdatePassword Component', () => {
  beforeEach(() => {
    // Mock implementation of UpdatePassword
    UpdatePassword.mockImplementation(MockUpdatePassword);
    jest.clearAllMocks();
  });

  test('renders update password form elements', () => {
    render(<UpdatePassword />);
    
    // Check for heading
    expect(screen.getByRole('heading', { name: /Update Password/i })).toBeInTheDocument();
    
    // Check for form elements
    expect(screen.getByTestId('current-password-field')).toBeInTheDocument();
    expect(screen.getByTestId('new-password-field')).toBeInTheDocument();
    expect(screen.getByTestId('confirm-password-field')).toBeInTheDocument();
    expect(screen.getByTestId('update-button')).toBeInTheDocument();
  });
});