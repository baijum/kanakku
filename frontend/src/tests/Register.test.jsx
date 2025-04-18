import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Register from '../components/Auth/Register';
import { MemoryRouter } from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';

// Mock axios instance
jest.mock('../api/axiosInstance', () => ({
  __esModule: true,
  default: jest.fn()
}));

// Mock useNavigate
const mockedNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedNavigate,
}));

// Mock localStorage
const mockSetItem = jest.fn();
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(),
    setItem: mockSetItem,
    removeItem: jest.fn(),
  },
  writable: true
});

describe('Register Component', () => {
  const mockSetIsLoggedIn = jest.fn();
  
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Default successful response
    axiosInstance.mockResolvedValue({
      data: {
        token: 'fake-jwt-token'
      }
    });
    
    render(
      <MemoryRouter>
        <Register setIsLoggedIn={mockSetIsLoggedIn} />
      </MemoryRouter>
    );
  });

  test('renders register form elements', () => {
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Register/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign up with Google/i })).toBeInTheDocument();
    expect(screen.getByText(/Already have an account/i)).toBeInTheDocument();
  });

  test('allows user to enter email and password', () => {
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/^Password$/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
    expect(confirmPasswordInput.value).toBe('password123');
  });

  test('shows error if passwords do not match', async () => {
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/^Password$/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i);
    const registerButton = screen.getByRole('button', { name: /Register$/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'differentpassword' } });
    fireEvent.click(registerButton);

    const errorMessage = await screen.findByText(/Passwords do not match/i);
    expect(errorMessage).toBeInTheDocument();
    expect(axiosInstance).not.toHaveBeenCalled();
  });

  test('shows error if any field is empty', async () => {
    const emailInput = screen.getByLabelText(/Email Address/i);
    const registerButton = screen.getByRole('button', { name: /Register$/i });

    // Only fill email, leave passwords empty
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(registerButton);

    const errorMessage = await screen.findByText(/All fields are required/i);
    expect(errorMessage).toBeInTheDocument();
    expect(axiosInstance).not.toHaveBeenCalled();
  });

  test('submits form and handles successful registration', async () => {
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/^Password$/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i);
    const registerButton = screen.getByRole('button', { name: /Register$/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(axiosInstance).toHaveBeenCalledWith({
        method: 'post',
        url: '/api/v1/auth/register',
        data: {
          email: 'test@example.com',
          password: 'password123',
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      expect(mockSetItem).toHaveBeenCalledWith('token', 'fake-jwt-token');
      expect(mockSetIsLoggedIn).toHaveBeenCalledWith(true);
      expect(mockedNavigate).toHaveBeenCalledWith('/');
    });
  });

  test('handles account activation flow', async () => {
    // Mock response for account that needs activation
    axiosInstance.mockResolvedValueOnce({
      data: {
        message: 'Registration successful. Please check your email to activate your account.'
      }
    });
    
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/^Password$/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i);
    const registerButton = screen.getByRole('button', { name: /Register$/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(mockedNavigate).toHaveBeenCalledWith('/login', {
        state: {
          notification: {
            type: 'success',
            message: 'Registration successful. Please check your email to activate your account.'
          }
        }
      });
      expect(mockSetIsLoggedIn).not.toHaveBeenCalled();
    });
  });

  test('handles registration error from server', async () => {
    // Mock error response
    axiosInstance.mockRejectedValueOnce({
      response: {
        data: {
          error: 'Email is already registered'
        }
      }
    });
    
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/^Password$/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i);
    const registerButton = screen.getByRole('button', { name: /Register$/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(registerButton);

    const errorMessage = await screen.findByText(/Email is already registered/i);
    expect(errorMessage).toBeInTheDocument();
    expect(mockSetIsLoggedIn).not.toHaveBeenCalled();
    expect(mockedNavigate).not.toHaveBeenCalled();
  });

  test('initiates Google authentication', async () => {
    // Mock Google auth response
    axiosInstance.mockResolvedValueOnce({
      data: {
        auth_url: 'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...'
      }
    });
    
    // Override window.location.href setter
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: jest.fn() };
    
    const googleButton = screen.getByRole('button', { name: /Sign up with Google/i });
    fireEvent.click(googleButton);

    await waitFor(() => {
      expect(axiosInstance).toHaveBeenCalledWith({
        method: 'get',
        url: '/api/v1/auth/google',
      });
      
      expect(window.location.href).toBe('https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...');
    });
    
    // Restore original location
    window.location = originalLocation;
  });

  test('handles Google authentication error', async () => {
    // Mock Google auth error
    axiosInstance.mockRejectedValueOnce({
      response: {
        data: {
          error: 'Failed to initiate Google authentication'
        }
      }
    });
    
    const googleButton = screen.getByRole('button', { name: /Sign up with Google/i });
    fireEvent.click(googleButton);

    const errorMessage = await screen.findByText(/Failed to initiate Google authentication/i);
    expect(errorMessage).toBeInTheDocument();
  });
});