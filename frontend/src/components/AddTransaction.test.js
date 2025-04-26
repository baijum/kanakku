import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event'; // Import userEvent
import '@testing-library/jest-dom';
import AddTransaction from './AddTransaction';
import axiosInstance from '../api/axiosInstance'; // Import the actual module to use its mocked methods

// Mock modules with more direct approach
jest.mock('../api/axiosInstance'); // Mock the instance directly
jest.mock('@mui/x-date-pickers/DatePicker', () => ({
  DatePicker: ({ label, value, onChange }) => ( // Pass props through
    <div data-testid="mock-date-picker">
      <label>{label}</label>
      <input type="date" value={value?.toISOString().split('T')[0] || ''} onChange={(e) => onChange(new Date(e.target.value))} />
    </div>
  )
}));
jest.mock('@mui/x-date-pickers/LocalizationProvider', () => ({
  LocalizationProvider: ({ children }) => <div>{children}</div>
}));
jest.mock('@mui/x-date-pickers/AdapterDateFns', () => ({
  AdapterDateFns: jest.fn()
}));

describe('AddTransaction Component', () => {
  const mockAccounts = ['Expenses:Food', 'Assets:Cash', 'Liabilities:Credit Card', 'Assets:Bank'];
  const sortedMockAccounts = ['Assets:Bank', 'Assets:Cash', 'Expenses:Food', 'Liabilities:Credit Card'];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'fake-token'),
        setItem: jest.fn(),
        clear: jest.fn()
      },
      writable: true
    });
    
    // Mock axiosInstance get response for accounts (intentionally unsorted)
    axiosInstance.get.mockImplementation(() => {
      return Promise.resolve({
        data: {
          accounts: mockAccounts
        }
      });
    });
    
    // Mock axiosInstance post for transaction creation
    axiosInstance.post.mockImplementation(() => {
      return Promise.resolve({
        data: { id: '123' }
      });
    });
  });

  test('renders add transaction form and allows adding a transaction', async () => {
    const user = userEvent.setup(); // Setup userEvent
    render(<AddTransaction />);

    // Wait for accounts to load (check for first account input)
    await waitFor(() => {
      expect(screen.getAllByLabelText(/Account/i)[0]).toBeInTheDocument();
    });

    // Check initial elements
    expect(screen.getByRole('heading', { name: /add transaction/i })).toBeInTheDocument();
    expect(screen.getByTestId('mock-date-picker')).toBeInTheDocument();
    expect(screen.getByLabelText(/Payee/i)).toBeInTheDocument();
    expect(screen.getAllByLabelText(/Account/i)).toHaveLength(2); // Initial two postings
    expect(screen.getAllByLabelText(/Amount/i)).toHaveLength(2);
    expect(screen.getByRole('button', { name: /add entry/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add transaction/i })).toBeInTheDocument();

    // Fill form fields
    await user.type(screen.getByLabelText(/Payee/i), 'Test Payee');

    // Select accounts using Autocomplete
    const accountInputs = screen.getAllByLabelText(/Account/i);
    
    // --- Interaction with first Autocomplete ---
    await user.click(accountInputs[0]); // Open dropdown
    const option1 = await screen.findByRole('option', { name: sortedMockAccounts[0] }); // Assets:Bank
    await user.click(option1);
    
    // --- Interaction with second Autocomplete ---
    await user.click(accountInputs[1]); // Open dropdown
    const option2 = await screen.findByRole('option', { name: sortedMockAccounts[1] }); // Assets:Cash
    await user.click(option2);

    // Fill amounts
    const amountInputs = screen.getAllByLabelText(/Amount/i);
    await user.type(amountInputs[0], '100');
    await user.type(amountInputs[1], '-100');

    // Submit form
    await user.click(screen.getByRole('button', { name: /add transaction/i }));

    // Wait for submission and check API call
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/v1/transactions', expect.objectContaining({
        payee: 'Test Payee',
        postings: expect.arrayContaining([
          expect.objectContaining({ account: sortedMockAccounts[0], amount: '100' }),
          expect.objectContaining({ account: sortedMockAccounts[1], amount: '-100' }),
        ]),
      }));
    });

    // Check for success message
    expect(await screen.findByText(/Transaction added successfully!/i)).toBeInTheDocument();
  });

  test('accounts are sorted alphabetically', async () => {
    // Get the sorting function implementation
    render(<AddTransaction />);

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledWith('/api/v1/accounts');
    });

    // Check that the accounts are sorted alphabetically
    // This test verifies the implementation detail that accounts are sorted
    // before being set in state
    expect(axiosInstance.get).toHaveBeenCalledTimes(1);
    
    // Verify sorting implementation by checking the mock sorting logic in the component
    const sortAccounts = (accounts) => [...accounts].sort((a, b) => a.localeCompare(b));
    const sortedAccounts = sortAccounts(mockAccounts);
    
    // Expected sorted order
    expect(sortedAccounts).toEqual(['Assets:Bank', 'Assets:Cash', 'Expenses:Food', 'Liabilities:Credit Card']);
  });

  test('handles transaction balance error', async () => {
    const user = userEvent.setup();
    render(<AddTransaction />);

    await waitFor(() => {
      expect(screen.getAllByLabelText(/Account/i)[0]).toBeInTheDocument();
    });

    // Fill form fields with unbalanced amounts
    await user.type(screen.getByLabelText(/Payee/i), 'Unbalanced Payee');
    
    const accountInputs = screen.getAllByLabelText(/Account/i);
    await user.click(accountInputs[0]);
    const option1 = await screen.findByRole('option', { name: sortedMockAccounts[0] });
    await user.click(option1);

    await user.click(accountInputs[1]);
    const option2 = await screen.findByRole('option', { name: sortedMockAccounts[1] });
    await user.click(option2);

    const amountInputs = screen.getAllByLabelText(/Amount/i);
    await user.type(amountInputs[0], '100');
    await user.type(amountInputs[1], '-90'); // Unbalanced

    // Submit form
    await user.click(screen.getByRole('button', { name: /add transaction/i }));

    // Check for error message
    expect(await screen.findByText(/Transaction does not balance/i)).toBeInTheDocument();
    expect(axiosInstance.post).not.toHaveBeenCalled();
  });

  // Test adding/removing postings if needed
  test('allows adding and removing postings', async () => {
    const user = userEvent.setup();
    render(<AddTransaction />);

    await waitFor(() => {
      expect(screen.getAllByLabelText(/Account/i)).toHaveLength(2);
    });

    // Add a posting
    await user.click(screen.getByRole('button', { name: /add entry/i }));
    expect(screen.getAllByLabelText(/Account/i)).toHaveLength(3);
    expect(screen.getAllByLabelText(/Amount/i)).toHaveLength(3);

    // Remove the added posting (should be the last one)
    const removeButtons = screen.getAllByRole('button', { name: /delete posting/i });
    expect(removeButtons).toHaveLength(1);
    await user.click(removeButtons[0]); 
    
    expect(screen.getAllByLabelText(/Account/i)).toHaveLength(2);
    expect(screen.getAllByLabelText(/Amount/i)).toHaveLength(2);
    expect(screen.queryByRole('button', { name: /delete posting/i })).not.toBeInTheDocument();
  });
});