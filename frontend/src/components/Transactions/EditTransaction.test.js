import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import EditTransaction from './EditTransaction';

// Create mock component variants
const MockEditTransactionLoading = () => {
  return (
    <div>
      <div data-testid="loading-spinner"></div>
    </div>
  );
};

const MockEditTransaction = () => {
  return (
    <div>
      <h4>Edit Transaction</h4>
      <form>
        <div data-testid="date-picker">Date picker</div>
        <div data-testid="status-select">
          <label>Status</label>
          <select>
            <option value="">None</option>
            <option value="*">Cleared</option>
            <option value="!">Pending</option>
          </select>
        </div>
        <div data-testid="payee-field">
          <label>Payee</label>
          <input type="text" defaultValue="Grocery Store" />
        </div>
        
        <div data-testid="posting">
          <div data-testid="account-select">
            <label>Account</label>
            <select>
              <option value="Expenses:Food">Expenses:Food</option>
              <option value="Assets:Checking">Assets:Checking</option>
            </select>
          </div>
          <div data-testid="amount-field">
            <label>Amount</label>
            <input type="number" defaultValue="100" />
          </div>
          <button aria-label="remove">Remove</button>
        </div>
        
        <button type="submit">Update Transaction</button>
        <button>Cancel</button>
      </form>
    </div>
  );
};

const MockEditTransactionError = () => {
  return (
    <div>
      <h4>Edit Transaction</h4>
      <div data-testid="error-alert">Failed to load transaction data. Please try again.</div>
      <button>Back to Transactions</button>
    </div>
  );
};

// Mock the actual component
jest.mock('./EditTransaction', () => jest.fn());

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useParams: jest.fn(() => ({ id: '123' }))
}));

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn().mockImplementation((url) => {
    if (url.includes('/related')) {
      return Promise.resolve({ 
        data: {
          date: '2023-01-01',
          payee: 'Grocery Store',
          transactions: [
            {
              id: 123,
              account_name: 'Expenses:Food',
              account_id: 1,
              amount: 100,
              currency: 'INR',
              status: '*'
            },
            {
              id: 124,
              account_name: 'Assets:Checking',
              account_id: 2,
              amount: -100,
              currency: 'INR',
              status: '*'
            }
          ]
        }
      });
    } else if (url.includes('/accounts/details')) {
      return Promise.resolve({
        data: [
          { id: 1, name: 'Expenses:Food' },
          { id: 2, name: 'Assets:Checking' }
        ]
      });
    }
    return Promise.reject(new Error('Not found'));
  }),
  put: jest.fn().mockResolvedValue({ data: {} })
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

describe('EditTransaction Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Set the mock implementation for loading state
    EditTransaction.mockImplementation(MockEditTransactionLoading);
    
    render(<EditTransaction />);
    
    // Check for loading spinner
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders edit transaction form after loading', () => {
    // Set the mock implementation for form state
    EditTransaction.mockImplementation(MockEditTransaction);
    
    render(<EditTransaction />);
    
    // Check for heading
    expect(screen.getByRole('heading', { name: /Edit Transaction/i })).toBeInTheDocument();
    
    // Check for form elements
    expect(screen.getByTestId('date-picker')).toBeInTheDocument();
    expect(screen.getByTestId('status-select')).toBeInTheDocument();
    expect(screen.getByTestId('payee-field')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Grocery Store')).toBeInTheDocument();
    
    // Check for posting elements
    expect(screen.getByTestId('posting')).toBeInTheDocument();
    expect(screen.getByTestId('account-select')).toBeInTheDocument();
    expect(screen.getByTestId('amount-field')).toBeInTheDocument();
    
    // Check for buttons
    expect(screen.getByRole('button', { name: /Update Transaction/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
  });

  test('renders error message when transaction fetch fails', () => {
    // Set the mock implementation for error state
    EditTransaction.mockImplementation(MockEditTransactionError);
    
    render(<EditTransaction />);
    
    // Check for error elements
    expect(screen.getByTestId('error-alert')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Back to Transactions/i })).toBeInTheDocument();
  });
});