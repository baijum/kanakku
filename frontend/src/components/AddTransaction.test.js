import React from 'react';
import { render, screen } from '@testing-library/react';
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
    // Remove unnecessary act wrapper 
    render(<AddTransaction />);
    
    // Heading should be present
    expect(screen.getByRole('heading', { name: /add transaction/i })).toBeInTheDocument();
    
    // Date picker should be rendered
    expect(screen.getByTestId('mock-date-picker')).toBeInTheDocument();
    
    // Only test for essential elements
    expect(screen.getByRole('button', { name: /add posting/i })).toBeInTheDocument();
  });
});