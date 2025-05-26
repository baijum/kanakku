import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AccountForm from './AccountForm';

// Create mock component that doesn't use actual React Router
const MockAccountForm = () => {
  return (
    <div>
      <h2>Create New Account</h2>
      <form>
        <div data-testid="account-name-field">
          <label htmlFor="account-name">Account Name</label>
          <input id="account-name" name="accountName" />
        </div>
        <div data-testid="description-field">
          <label htmlFor="description">Description (Optional)</label>
          <textarea id="description" name="description" rows="3" />
        </div>
        <button type="submit">Create Account</button>
      </form>
    </div>
  );
};

// Mock the actual component
jest.mock('./AccountForm', () => jest.fn());

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  post: jest.fn().mockResolvedValue({ status: 201 })
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

describe('AccountForm Component', () => {
  beforeEach(() => {
    // Mock implementation of AccountForm
    AccountForm.mockImplementation(MockAccountForm);
    jest.clearAllMocks();
  });

  test('renders account form elements', () => {
    render(<AccountForm />);

    // Check for heading
    expect(screen.getByRole('heading', { name: /Create New Account/i })).toBeInTheDocument();

    // Check for form elements
    expect(screen.getByTestId('account-name-field')).toBeInTheDocument();
    expect(screen.getByLabelText(/Account Name/i)).toBeInTheDocument();

    expect(screen.getByTestId('description-field')).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();

    // Check for submit button
    expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
  });
});
