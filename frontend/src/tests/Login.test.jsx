import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Login from '../components/Auth/Login';
import { MemoryRouter } from 'react-router-dom'; // Assuming you use react-router

// Mock the API call (replace with your actual API call structure if different)
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ token: 'fake-jwt-token' }),
  })
);

// Mock useNavigate if you use it for redirection
const mockedNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), // use actual for all non-hook parts
  useNavigate: () => mockedNavigate,
}));

describe('Login Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    fetch.mockClear();
    mockedNavigate.mockClear();
    render(
      <MemoryRouter> {/* Wrap with MemoryRouter if using Link or useNavigate */} 
        <Login />
      </MemoryRouter>
    );
  });

  test('renders login form elements', () => {
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('allows user to enter username and password', () => {
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });

  test('submits form and calls API on login button click', async () => {
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
      // Add more specific checks for the fetch call if needed
      // e.g., expect(fetch).toHaveBeenCalledWith('/api/v1/auth/login', expect.any(Object));
      // Check if navigation happened after successful login
      // expect(mockedNavigate).toHaveBeenCalledWith('/dashboard'); // Adjust the target route
    });
  });

  test('displays error message on failed login', async () => {
    // Mock fetch to simulate a failed login
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ message: 'Invalid credentials' }),
      })
    );

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);

    // Wait for the error message to appear (adjust selector as needed)
    const errorMessage = await screen.findByText(/invalid credentials/i);
    expect(errorMessage).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(mockedNavigate).not.toHaveBeenCalled();
  });
}); 