import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import AddTransaction from '../src/components/AddTransaction';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock localStorage
const mockGetItem = jest.fn(() => 'fake-token');
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: mockGetItem,
    setItem: jest.fn(),
    removeItem: jest.fn(),
  },
  writable: true
});

// Mock DatePicker since it's complex to test
jest.mock('@mui/x-date-pickers/DatePicker', () => {
  const { forwardRef } = require('react');
  return {
    DatePicker: forwardRef(({ label, onChange, value, slots }, ref) => {
      return (
        <div data-testid="date-picker">
          <label>{label}</label>
          <input 
            type="date"
            value={value instanceof Date ? value.toISOString().split('T')[0] : ''}
            onChange={(e) => onChange(new Date(e.target.value))}
            ref={ref}
            data-testid="date-picker-input"
          />
        </div>
      );
    })
  };
});

// Mock LocalizationProvider
jest.mock('@mui/x-date-pickers/LocalizationProvider', () => ({
  LocalizationProvider: ({ children }) => <div>{children}</div>
}));

// Mock AdapterDateFns
jest.mock('@mui/x-date-pickers/AdapterDateFns', () => ({
  AdapterDateFns: jest.fn()
}));

describe('AddTransaction Component', () => {
  const mockAccounts = ['Assets:Checking', 'Expenses:Food', 'Income:Salary'];
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful accounts fetch
    axios.get.mockResolvedValue({
      data: {
        accounts: mockAccounts
      }
    });
    
    // Mock successful transaction creation
    axios.post.mockResolvedValue({
      data: {
        id: '123',
        message: 'Transaction created successfully'
      }
    });
    
    // Render the component
    render(<AddTransaction />);
  });
  
  test('renders the form with initial elements', async () => {
    // Check basic form elements
    expect(screen.getByText(/Add Transaction/i)).toBeInTheDocument();
    expect(screen.getByTestId('date-picker')).toBeInTheDocument();
    expect(screen.getByLabelText(/Payee/i)).toBeInTheDocument();
    
    // Should fetch accounts on load
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/v1/accounts', {
        headers: { 'Authorization': 'Bearer fake-token' }
      });
    });
  });
  
  test('allows adding and removing postings', () => {
    // Initially there should be 2 posting sections
    const initialAccountSelects = screen.getAllByLabelText(/Account/i);
    expect(initialAccountSelects.length).toBe(2);
    
    // Add a new posting
    const addButton = screen.getByText(/Add Posting/i);
    fireEvent.click(addButton);
    
    // Now there should be 3 posting sections
    const updatedAccountSelects = screen.getAllByLabelText(/Account/i);
    expect(updatedAccountSelects.length).toBe(3);
    
    // Delete buttons should be present
    const deleteButtons = screen.getAllByRole('button', { name: '' }); // Delete icon buttons have no accessible name
    expect(deleteButtons.length).toBeGreaterThan(0);
    
    // Remove a posting
    fireEvent.click(deleteButtons[0]);
    
    // Now should be back to 2 posting sections
    const finalAccountSelects = screen.getAllByLabelText(/Account/i);
    expect(finalAccountSelects.length).toBe(2);
  });
  
  test('validates that transaction postings balance', async () => {
    // Fill out the form with unbalanced postings
    const payeeInput = screen.getByLabelText(/Payee/i);
    fireEvent.change(payeeInput, { target: { value: 'Grocery Store' } });
    
    // Select accounts for postings
    const accountSelects = screen.getAllByLabelText(/Account/i);
    const amountInputs = screen.getAllByLabelText(/Amount/i);
    
    // Set up unbalanced transaction (100 + 50 != 0)
    fireEvent.change(accountSelects[0], { target: { value: 'Expenses:Food' } });
    fireEvent.change(amountInputs[0], { target: { value: '100' } });
    
    fireEvent.change(accountSelects[1], { target: { value: 'Assets:Checking' } });
    fireEvent.change(amountInputs[1], { target: { value: '50' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Add Transaction/i });
    fireEvent.click(submitButton);
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/Transaction does not balance/i)).toBeInTheDocument();
    });
    
    // Axios post should not have been called
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('submits a valid transaction successfully', async () => {
    // Fill out the form with valid data
    const payeeInput = screen.getByLabelText(/Payee/i);
    fireEvent.change(payeeInput, { target: { value: 'Grocery Store' } });
    
    // Select status
    const statusSelect = screen.getByLabelText(/Status/i);
    fireEvent.change(statusSelect, { target: { value: '*' } });
    
    // Select accounts for postings
    const accountSelects = screen.getAllByLabelText(/Account/i);
    const amountInputs = screen.getAllByLabelText(/Amount/i);
    
    // Set up balanced transaction (100 + -100 = 0)
    fireEvent.change(accountSelects[0], { target: { value: 'Expenses:Food' } });
    fireEvent.change(amountInputs[0], { target: { value: '100' } });
    
    fireEvent.change(accountSelects[1], { target: { value: 'Assets:Checking' } });
    fireEvent.change(amountInputs[1], { target: { value: '-100' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Add Transaction/i });
    fireEvent.click(submitButton);
    
    // Check that axios.post was called with the correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        '/api/v1/transactions', 
        expect.objectContaining({
          payee: 'Grocery Store',
          status: '*',
          postings: [
            { account: 'Expenses:Food', amount: '100', currency: '₹' },
            { account: 'Assets:Checking', amount: '-100', currency: '₹' }
          ]
        }),
        expect.any(Object)
      );
    });
    
    // Success message should appear
    expect(screen.getByText(/Transaction added successfully/i)).toBeInTheDocument();
    
    // Form should be reset
    expect(payeeInput.value).toBe('');
    expect(statusSelect.value).toBe('');
  });
  
  test('handles API error when adding transaction', async () => {
    // Mock an API error
    axios.post.mockRejectedValueOnce({
      response: {
        data: {
          error: 'Invalid transaction data'
        }
      }
    });
    
    // Fill out the form with valid data
    const payeeInput = screen.getByLabelText(/Payee/i);
    fireEvent.change(payeeInput, { target: { value: 'Grocery Store' } });
    
    // Set up balanced transaction
    const accountSelects = screen.getAllByLabelText(/Account/i);
    const amountInputs = screen.getAllByLabelText(/Amount/i);
    
    fireEvent.change(accountSelects[0], { target: { value: 'Expenses:Food' } });
    fireEvent.change(amountInputs[0], { target: { value: '100' } });
    
    fireEvent.change(accountSelects[1], { target: { value: 'Assets:Checking' } });
    fireEvent.change(amountInputs[1], { target: { value: '-100' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Add Transaction/i });
    fireEvent.click(submitButton);
    
    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/Invalid transaction data/i)).toBeInTheDocument();
    });
  });
  
  test('handles API error when fetching accounts', async () => {
    // Clean up
    jest.clearAllMocks();
    
    // Mock an API error for accounts fetch
    axios.get.mockRejectedValueOnce({
      response: {
        status: 500,
        data: {
          error: 'Failed to fetch accounts'
        }
      }
    });
    
    // Re-render the component
    render(<AddTransaction />);
    
    // Should still render without crashing
    expect(screen.getByText(/Add Transaction/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledTimes(1);
    });
  });
});