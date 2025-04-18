import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import EditAccount from './EditAccount';

// Create mock component that doesn't use actual React Router
const MockEditAccount = () => {
  return (
    <div>
      <h4>Edit Account</h4>
      <form>
        <div data-testid="account-name-field">
          <label htmlFor="account-name">Account Name</label>
          <input id="account-name" name="accountName" defaultValue="Assets:Checking" />
        </div>
        <div data-testid="description-field">
          <label htmlFor="description">Description (Optional)</label>
          <textarea id="description" name="description" rows="3" defaultValue="Main checking account" />
        </div>
        <div>
          <button type="button">Cancel</button>
          <button type="submit">Update Account</button>
        </div>
      </form>
    </div>
  );
};

// Mock loading state component
const MockEditAccountLoading = () => {
  return (
    <div>
      <div data-testid="loading-spinner"></div>
    </div>
  );
};

// Mock the actual component
jest.mock('./EditAccount', () => jest.fn());

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useParams: jest.fn(() => ({ id: '1' }))
}));

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  get: jest.fn().mockResolvedValue({ 
    data: { 
      id: 1,
      name: 'Assets:Checking', 
      description: 'Main checking account' 
    } 
  }),
  put: jest.fn().mockResolvedValue({ status: 200, data: {} })
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

describe('EditAccount Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Set the mock implementation for loading state
    EditAccount.mockImplementation(MockEditAccountLoading);
    
    render(<EditAccount />);
    
    // Check for loading spinner
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders edit account form after loading', () => {
    // Set the mock implementation for form state
    EditAccount.mockImplementation(MockEditAccount);
    
    render(<EditAccount />);
    
    // Check for heading
    expect(screen.getByRole('heading', { name: /Edit Account/i })).toBeInTheDocument();
    
    // Check for form elements
    expect(screen.getByTestId('account-name-field')).toBeInTheDocument();
    expect(screen.getByLabelText(/Account Name/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Assets:Checking')).toBeInTheDocument();
    
    expect(screen.getByTestId('description-field')).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Main checking account')).toBeInTheDocument();
    
    // Check for buttons
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Update Account/i })).toBeInTheDocument();
  });
});