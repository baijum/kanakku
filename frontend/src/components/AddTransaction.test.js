import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AddTransaction from './AddTransaction';

// Mock modules with more direct approach
jest.mock('axios');
jest.mock('@mui/x-date-pickers/DatePicker', () => ({
  DatePicker: ({ label }) => (
    <div data-testid="mock-date-picker">
      <label>{label}</label>
      <input type="date" />
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
  // Mock axios responses before rendering component
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'fake-token'),
        setItem: jest.fn(),
      },
      writable: true
    });
    
    // Mock axios get response for accounts
    require('axios').get = jest.fn().mockImplementation(() => {
      return Promise.resolve({
        data: {
          accounts: ['Assets:Cash', 'Expenses:Food']
        }
      });
    });
    
    // Mock axios post for transaction creation
    require('axios').post = jest.fn().mockImplementation(() => {
      return Promise.resolve({
        data: { id: '123' }
      });
    });
  });

  test('renders add transaction form - basic elements', async () => {
    render(<AddTransaction />);
    
    // Wait for component to finish loading accounts 
    // and for the "Add Posting" button to be available
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add entry/i })).toBeInTheDocument();
    });
    
    // After waiting, check for all required elements
    expect(screen.getByRole('heading', { name: /add transaction/i })).toBeInTheDocument();
    expect(screen.getByTestId('mock-date-picker')).toBeInTheDocument();
  });
});