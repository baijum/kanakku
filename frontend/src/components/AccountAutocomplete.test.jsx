import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import AccountAutocomplete from './AccountAutocomplete';
import axiosInstance from '../api/axiosInstance';

// Mock axiosInstance
jest.mock('../api/axiosInstance');
const mockedAxios = axiosInstance;

describe('AccountAutocomplete Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    const mockOnChange = jest.fn();
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    expect(screen.getByLabelText(/Search transactions/i)).toBeInTheDocument();
  });

  test('does not fetch suggestions without colon', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets');
    
    // Should not call the API without a colon
    expect(mockedAxios.get).not.toHaveBeenCalled();
  });

  test('fetches suggestions when colon is typed', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    const mockSuggestions = {
      data: {
        suggestions: ['Assets:Bank:Checking', 'Assets:Bank:Savings', 'Assets:Cash'],
        prefix: 'Assets:'
      }
    };
    
    mockedAxios.get.mockResolvedValueOnce(mockSuggestions);
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets:');
    
    // Wait for debounced API call
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/accounts/autocomplete', {
        params: {
          prefix: 'Assets:',
          limit: 10
        }
      });
    }, { timeout: 1000 });
  });

  test('displays suggestions when available', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    const mockSuggestions = {
      data: {
        suggestions: ['Assets:Bank:Checking', 'Assets:Bank:Savings'],
        prefix: 'Assets:Bank:'
      }
    };
    
    mockedAxios.get.mockResolvedValueOnce(mockSuggestions);
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets:Bank:');
    
    // Wait for suggestions to appear
    await waitFor(() => {
      expect(screen.getByText('Assets:Bank:Checking')).toBeInTheDocument();
    }, { timeout: 1000 });
    
    expect(screen.getByText('Assets:Bank:Savings')).toBeInTheDocument();
  });

  test('calls onChange when suggestion is selected', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    const mockSuggestions = {
      data: {
        suggestions: ['Assets:Bank:Checking', 'Assets:Bank:Savings'],
        prefix: 'Assets:Bank:'
      }
    };
    
    mockedAxios.get.mockResolvedValueOnce(mockSuggestions);
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets:Bank:');
    
    // Wait for suggestions to appear
    await waitFor(() => {
      expect(screen.getByText('Assets:Bank:Checking')).toBeInTheDocument();
    }, { timeout: 1000 });
    
    // Click on a suggestion
    await user.click(screen.getByText('Assets:Bank:Checking'));
    
    // Should call onChange with the selected value
    expect(mockOnChange).toHaveBeenCalledWith('Assets:Bank:Checking');
  });

  test('handles API errors gracefully', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    // Mock API error
    mockedAxios.get.mockRejectedValueOnce(new Error('API Error'));
    
    // Spy on console.error to verify error handling
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets:');
    
    // Wait for API call and error handling
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching account suggestions:', expect.any(Error));
    }, { timeout: 1000 });
    
    consoleSpy.mockRestore();
  });

  test('shows loading indicator during API call', async () => {
    const mockOnChange = jest.fn();
    const user = userEvent.setup();
    
    // Mock a delayed response
    const mockSuggestions = {
      data: {
        suggestions: ['Assets:Bank:Checking'],
        prefix: 'Assets:'
      }
    };
    
    mockedAxios.get.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockSuggestions), 100))
    );
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
      />
    );
    
    const input = screen.getByLabelText(/Search transactions/i);
    await user.type(input, 'Assets:');
    
    // Should show loading indicator
    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    }, { timeout: 500 });
  });

  test('accepts custom props', () => {
    const mockOnChange = jest.fn();
    
    render(
      <AccountAutocomplete
        value=""
        onChange={mockOnChange}
        label="Custom Label"
        placeholder="Custom Placeholder"
        helperText="Custom Helper Text"
        disabled
      />
    );
    
    expect(screen.getByLabelText(/Custom Label/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Custom Placeholder/i)).toBeInTheDocument();
    expect(screen.getByText(/Custom Helper Text/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Custom Label/i)).toBeDisabled();
  });
}); 