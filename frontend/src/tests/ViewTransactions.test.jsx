import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ViewTransactions from '../components/ViewTransactions';
import { MemoryRouter } from 'react-router-dom';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock react-router-dom's useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock localStorage
const mockGetItem = jest.fn(() => 'fake-token');
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: mockGetItem,
    setItem: jest.fn(),
  },
  writable: true
});

// Sample test data
const mockTransactions = [
  {
    id: '1',
    date: '2023-01-15',
    payee: 'Grocery Store',
    status: '*',
    postings: [
      { id: '1', account: 'Expenses:Food', amount: '50.00', currency: 'INR' },
      { id: '2', account: 'Assets:Checking', amount: '-50.00', currency: 'INR' }
    ]
  },
  {
    id: '2',
    date: '2023-01-20',
    payee: 'Coffee Shop',
    status: '',
    postings: [
      { id: '3', account: 'Expenses:Coffee', amount: '10.00', currency: 'INR' },
      { id: '4', account: 'Assets:Cash', amount: '-10.00', currency: 'INR' }
    ]
  }
];

const mockPreambles = [
  { id: '1', name: 'Default Preamble' },
  { id: '2', name: 'Custom Preamble' }
];

describe('ViewTransactions Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful transactions fetch
    axios.get.mockImplementation((url) => {
      if (url === '/api/v1/transactions') {
        return Promise.resolve({
          data: {
            transactions: mockTransactions,
            total: mockTransactions.length
          }
        });
      } else if (url === '/api/v1/preambles') {
        return Promise.resolve({
          data: {
            preambles: mockPreambles
          }
        });
      } else if (url.includes('/api/v1/transactions/') && url.includes('/related')) {
        // Mock for fetching transaction details
        return Promise.resolve({
          data: {
            transactions: [
              { id: '1', account_name: 'Expenses:Food', amount: 50, currency: 'INR' },
              { id: '2', account_name: 'Assets:Checking', amount: -50, currency: 'INR' }
            ]
          }
        });
      }
      return Promise.reject(new Error('Not found'));
    });
    
    // Render component
    render(
      <MemoryRouter>
        <ViewTransactions />
      </MemoryRouter>
    );
  });
  
  test('renders view transactions component with loading state', () => {
    expect(screen.getByText(/Transactions/i)).toBeInTheDocument();
    // Initially should show loading state
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders transactions after loading', async () => {
    // Wait for transactions to load
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Should display our mock transactions
    expect(screen.getByText('Grocery Store')).toBeInTheDocument();
    expect(screen.getByText('Coffee Shop')).toBeInTheDocument();
    
    // Check for account and amount rendering
    expect(screen.getByText('Expenses:Food')).toBeInTheDocument();
    expect(screen.getByText('Assets:Checking')).toBeInTheDocument();
    expect(screen.getByText('₹ 50.00')).toBeInTheDocument();
    expect(screen.getByText('₹ -50.00')).toBeInTheDocument();
    
    // Check that action buttons are rendered
    const editButtons = screen.getAllByLabelText('edit');
    const deleteButtons = screen.getAllByLabelText('delete');
    expect(editButtons.length).toBe(2);
    expect(deleteButtons.length).toBe(2);
  });

  test('handles date filter changes', async () => {
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Get date inputs
    const startDateInput = screen.getByLabelText('Start Date');
    const endDateInput = screen.getByLabelText('End Date');
    
    // Change date filters
    fireEvent.change(startDateInput, { target: { value: '2023-01-01' } });
    fireEvent.change(endDateInput, { target: { value: '2023-01-31' } });
    
    // Should trigger a new API call with date params
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/v1/transactions', expect.objectContaining({
        params: expect.objectContaining({
          startDate: '2023-01-01',
          endDate: '2023-01-31'
        })
      }));
    });
  });

  test('navigates to edit page when edit button is clicked', async () => {
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Click the first edit button
    const editButtons = screen.getAllByLabelText('edit');
    fireEvent.click(editButtons[0]);
    
    // Should navigate to edit page
    expect(mockNavigate).toHaveBeenCalledWith('/transactions/edit/1');
  });

  test('opens delete confirmation dialog when delete button is clicked', async () => {
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Click the first delete button
    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);
    
    // Should open confirmation dialog
    expect(screen.getByText(/Are you sure you want to delete this transaction/i)).toBeInTheDocument();
    expect(screen.getByText(/This action cannot be undone/i)).toBeInTheDocument();
    
    // Dialog should have cancel and delete buttons
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Delete/i })).toBeInTheDocument();
  });

  test('deletes transaction when delete is confirmed', async () => {
    // Mock successful delete response
    axios.delete.mockResolvedValue({ data: { message: 'Transaction deleted successfully' } });
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Click the first delete button
    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion
    const confirmDeleteButton = screen.getByRole('button', { name: /Delete/i });
    fireEvent.click(confirmDeleteButton);
    
    // Should call delete API
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith('/api/v1/transactions/1/related', expect.any(Object));
    });
    
    // Should trigger a refresh of transactions
    expect(axios.get).toHaveBeenCalledWith('/api/v1/transactions', expect.any(Object));
    
    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/Transaction deleted successfully/i)).toBeInTheDocument();
    });
  });

  test('opens export dialog when export button is clicked', async () => {
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Click export button
    const exportButton = screen.getByRole('button', { name: /Export/i });
    fireEvent.click(exportButton);
    
    // Should open export dialog
    expect(screen.getByText(/Export Transactions/i)).toBeInTheDocument();
    expect(screen.getByText(/Select a preamble/i)).toBeInTheDocument();
    
    // Should load preambles
    expect(screen.getByText('Default Preamble')).toBeInTheDocument();
    expect(screen.getByText('Custom Preamble')).toBeInTheDocument();
  });

  test('exports transactions in ledger format', async () => {
    // Mock URL.createObjectURL and other DOM APIs for export
    global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');
    global.URL.revokeObjectURL = jest.fn();
    
    // Mock document.createElement to track download
    const mockAnchor = {
      href: '',
      download: '',
      click: jest.fn(),
    };
    document.createElement = jest.fn().mockImplementation((tag) => {
      if (tag === 'a') return mockAnchor;
      return document.createElement(tag);
    });
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();
    
    // Mock successful export response
    const mockBlob = new Blob(['fake ledger data'], { type: 'text/plain' });
    axios.get.mockImplementation((url) => {
      if (url === '/api/v1/ledgertransactions') {
        return Promise.resolve({
          data: mockBlob
        });
      }
      // Return the default mocks for other URLs
      return axios.get.getMockImplementation()(url);
    });
    
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Click export button
    const exportButton = screen.getByRole('button', { name: /Export/i });
    fireEvent.click(exportButton);
    
    // Select a preamble
    const preambleSelect = screen.getByLabelText('Preamble');
    fireEvent.change(preambleSelect, { target: { value: '1' } });
    
    // Click export in dialog
    const exportConfirmButton = screen.getByRole('button', { name: /^Export$/i });
    fireEvent.click(exportConfirmButton);
    
    // Should call export API
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        '/api/v1/ledgertransactions?preamble_id=1',
        expect.objectContaining({
          headers: { 'Authorization': 'Bearer fake-token' },
          responseType: 'blob'
        })
      );
    });
    
    // Should create download link
    expect(mockAnchor.download).toBe('transactions.ledger');
    expect(mockAnchor.click).toHaveBeenCalled();
    
    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/Transactions exported successfully/i)).toBeInTheDocument();
    });
  });

  test('handles API error when fetching transactions', async () => {
    // Clean up and re-mock with error
    jest.clearAllMocks();
    axios.get.mockImplementation((url) => {
      if (url === '/api/v1/transactions') {
        return Promise.reject({
          response: {
            status: 500,
            data: { error: 'Failed to load transactions' }
          }
        });
      }
      if (url === '/api/v1/preambles') {
        return Promise.resolve({ data: { preambles: mockPreambles } });
      }
      return Promise.reject(new Error('Not found'));
    });
    
    // Re-render component
    render(
      <MemoryRouter>
        <ViewTransactions />
      </MemoryRouter>
    );
    
    // Should show error message
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
      expect(screen.getByText(/Error loading transactions/i)).toBeInTheDocument();
    });
    
    // Should show empty state
    expect(screen.getByText(/No transactions found/i)).toBeInTheDocument();
  });
});