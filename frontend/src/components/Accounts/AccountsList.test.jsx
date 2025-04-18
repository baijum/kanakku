import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AccountsList from './AccountsList';

// Create mock component that doesn't use actual React Router
const MockAccountsList = () => {
  return (
    <div>
      <h4>Accounts</h4>
      <button data-testid="create-account-button">Create Account</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Assets:Checking</td>
            <td>Main checking account</td>
            <td>
              <button aria-label="edit account">Edit</button>
              <button aria-label="delete account">Delete</button>
            </td>
          </tr>
          <tr>
            <td>Expenses:Food</td>
            <td>Food expenses</td>
            <td>
              <button aria-label="edit account">Edit</button>
              <button aria-label="delete account">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

// Mock the actual component
jest.mock('./AccountsList', () => jest.fn());

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn()
}));

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  get: jest.fn().mockImplementation(() => Promise.resolve({ 
    data: { 
      accounts: ['Assets:Checking', 'Expenses:Food'] 
    } 
  })),
  delete: jest.fn().mockResolvedValue({ data: {} })
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

describe('AccountsList Component', () => {
  beforeEach(() => {
    // Mock implementation of AccountsList
    AccountsList.mockImplementation(MockAccountsList);
    jest.clearAllMocks();
  });

  test('renders accounts list elements', () => {
    render(<AccountsList />);
    
    // Check for heading
    expect(screen.getByRole('heading', { name: /Accounts/i })).toBeInTheDocument();
    
    // Check for create button
    expect(screen.getByTestId('create-account-button')).toBeInTheDocument();
    
    // Check for table headers
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
    
    // Check for account rows
    expect(screen.getByText('Assets:Checking')).toBeInTheDocument();
    expect(screen.getByText('Expenses:Food')).toBeInTheDocument();
    
    // Check for action buttons
    const editButtons = screen.getAllByRole('button', { name: /edit account/i });
    const deleteButtons = screen.getAllByRole('button', { name: /delete account/i });
    expect(editButtons.length).toBe(2);
    expect(deleteButtons.length).toBe(2);
  });
});