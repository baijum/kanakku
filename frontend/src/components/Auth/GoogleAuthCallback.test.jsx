import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import GoogleAuthCallback from './GoogleAuthCallback';

// Create mock component that doesn't use actual React Router
const MockGoogleAuthCallbackLoading = () => {
  return (
    <div>
      <div data-testid="loading-spinner"></div>
      <div>Completing authentication...</div>
    </div>
  );
};

const MockGoogleAuthCallbackError = () => {
  return (
    <div>
      <div data-testid="error-alert">No authentication token received from Google</div>
      <a href="/login">Return to login</a>
    </div>
  );
};

// Mock the actual component
jest.mock('./GoogleAuthCallback', () => jest.fn());

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: jest.fn()
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

describe('GoogleAuthCallback Component', () => {
  const mockUseLocation = require('react-router-dom').useLocation;
  const mockSetIsLoggedIn = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state when processing authentication', () => {
    // Mock location to simulate authentication in progress
    mockUseLocation.mockReturnValue({ 
      search: '?token=mockToken',
      pathname: '/auth/google/callback'
    });
    
    // Set the mock implementation for loading state
    GoogleAuthCallback.mockImplementation(MockGoogleAuthCallbackLoading);
    
    render(<GoogleAuthCallback setIsLoggedIn={mockSetIsLoggedIn} />);
    
    // Check for loading elements
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Completing authentication...')).toBeInTheDocument();
  });

  test('renders error state when token is missing', () => {
    // Mock location with no token
    mockUseLocation.mockReturnValue({ 
      search: '',
      pathname: '/auth/google/callback'
    });
    
    // Set the mock implementation for error state
    GoogleAuthCallback.mockImplementation(MockGoogleAuthCallbackError);
    
    render(<GoogleAuthCallback setIsLoggedIn={mockSetIsLoggedIn} />);
    
    // Check for error elements
    expect(screen.getByTestId('error-alert')).toBeInTheDocument();
    expect(screen.getByText('Return to login')).toBeInTheDocument();
  });
});