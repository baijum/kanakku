import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import EditTransaction from './EditTransaction';
import axiosInstance from '../../api/axiosInstance';

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: '123' })
}));

// Mock axiosInstance
jest.mock('../../api/axiosInstance');

// Mock DatePicker and related components
jest.mock('@mui/x-date-pickers/DatePicker', () => ({
    DatePicker: ({ label, value, onChange }) => (
        <div data-testid="mock-date-picker">
            <label>{label}</label>
            <input 
                type="date" 
                value={value instanceof Date && !isNaN(value) ? value.toISOString().split('T')[0] : ''} 
                onChange={(e) => onChange(e.target.value ? new Date(e.target.value + 'T00:00:00') : null)} 
            />
        </div>
    )
}));
jest.mock('@mui/x-date-pickers/LocalizationProvider', () => ({
    LocalizationProvider: ({ children }) => <div>{children}</div>
}));
jest.mock('@mui/x-date-pickers/AdapterDateFns', () => ({
    AdapterDateFns: jest.fn()
}));

describe('EditTransaction Component', () => {
  jest.setTimeout(15000); // Increase timeout globally for this suite (15 seconds)

  const mockTransactionId = '123';
  const mockAccountsData = [
    { id: 3, name: 'Liabilities:Credit Card', fullName: 'Liabilities:Credit Card' },
    { id: 1, name: 'Expenses:Food', fullName: 'Expenses:Food' },
    { id: 4, name: 'Income:Salary', fullName: 'Income:Salary' },
    { id: 2, name: 'Assets:Checking', fullName: 'Assets:Checking' }
  ];
  const sortedMockAccountNames = ['Assets:Checking', 'Expenses:Food', 'Income:Salary', 'Liabilities:Credit Card'];

  const mockRelatedTransactionData = {
    date: '2023-10-26T00:00:00Z',
    payee: 'Test Mart',
    transactions: [
      {
        id: 123,
        account_name: 'Expenses:Food',
        account_id: 1,
        amount: 50.00,
        currency: 'INR',
        status: '*'
      },
      {
        id: 124,
        account_name: 'Assets:Checking',
        account_id: 2,
        amount: -50.00,
        currency: 'INR',
        status: '*'
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();

    // Setup localStorage mock
    Object.defineProperty(window, 'localStorage', {
        value: {
            getItem: jest.fn(() => 'fake-token'),
            setItem: jest.fn(),
            clear: jest.fn()
        },
        writable: true
    });

    // Mock successful API calls by default
    axiosInstance.get.mockImplementation((url) => {
      if (url.includes(`/api/v1/transactions/${mockTransactionId}/related`)) {
        return Promise.resolve({ data: mockRelatedTransactionData });
      }
      if (url.includes('/api/v1/accounts/details')) {
        return Promise.resolve({ data: mockAccountsData });
      }
      return Promise.reject(new Error(`Unhandled GET request: ${url}`));
    });
    axiosInstance.put.mockResolvedValue({ data: { message: 'Update successful' } });

  });

  test('renders loading state initially', async () => {
    // Make GET requests take a bit longer to show loading
    axiosInstance.get.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: {} }), 10)));
    render(<EditTransaction />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('progressbar')).not.toBeInTheDocument());

  });

  test('renders edit form with data and allows update', async () => {
    const user = userEvent.setup();
    render(<EditTransaction />);

    // console.log("TEST LOG: Waiting for initial heading..."); // Remove Log 1
    expect(await screen.findByRole('heading', { name: /Edit Transaction/i })).toBeInTheDocument();
    // console.log("TEST LOG: Waiting for payee value..."); // Remove Log 2
    expect(await screen.findByDisplayValue(mockRelatedTransactionData.payee)).toBeInTheDocument();
    // console.log("TEST LOG: Initial data loaded. Verifying fields..."); // Remove Log 3

    // Verify initial fields are populated
    expect(screen.getByLabelText(/Payee/i)).toHaveValue(mockRelatedTransactionData.payee);
    // Check date using Testing Library's recommended approach
    const datePicker = screen.getByTestId('mock-date-picker');
    expect(within(datePicker).getByDisplayValue('2023-10-26')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: /Status/i })).toHaveTextContent('Cleared'); 

    // Check postings (account and amount)
    const accountInputs = screen.getAllByLabelText(/Account/i);
    expect(accountInputs[0]).toHaveValue(mockRelatedTransactionData.transactions[0].account_name);
    expect(accountInputs[1]).toHaveValue(mockRelatedTransactionData.transactions[1].account_name);
    const amountInputs = screen.getAllByLabelText(/Amount/i);
    expect(amountInputs[0]).toHaveValue(mockRelatedTransactionData.transactions[0].amount);
    expect(amountInputs[1]).toHaveValue(mockRelatedTransactionData.transactions[1].amount);
    // console.log("TEST LOG: Fields verified. Starting interactions..."); // Remove Log 4

    // Modify payee
    const payeeInput = screen.getByLabelText(/Payee/i);
    // console.log("TEST LOG: Clearing payee input..."); // Remove Log 4a
    await user.clear(payeeInput);
    // console.log("TEST LOG: Typing into payee input..."); // Remove Log 4b
    await user.type(payeeInput, 'Updated Payee');
    // console.log("TEST LOG: Payee interaction complete."); // Remove Log 4c

    // Modify first account using Autocomplete
    // console.log("TEST LOG: Clicking first account autocomplete..."); // Remove Log 5
    await user.click(accountInputs[0]); // Open dropdown
    // console.log("TEST LOG: Finding autocomplete option..."); // Remove Log 6
    const newAccountOption = await screen.findByRole('option', { name: sortedMockAccountNames[2] }); // Income:Salary
    // console.log("TEST LOG: Clicking autocomplete option..."); // Remove Log 7
    await user.click(newAccountOption);
    expect(accountInputs[0]).toHaveValue(sortedMockAccountNames[2]);
    // console.log("TEST LOG: Account selected. Clicking submit..."); // Remove Log 8

    // Submit the form
    await user.click(screen.getByRole('button', { name: /Update Transaction/i }));
    // console.log("TEST LOG: Submit clicked. Waiting for PUT call..."); // Remove Log 9

    // Wait for API call
    await waitFor(() => {
      expect(axiosInstance.put).toHaveBeenCalledWith(
        `/api/v1/transactions/${mockTransactionId}/update_with_postings`,
        expect.objectContaining({
          payee: 'Updated Payee',
          postings: expect.arrayContaining([
            expect.objectContaining({ 
              account: sortedMockAccountNames[2], // Income:Salary
              amount: mockRelatedTransactionData.transactions[0].amount,
              id: mockRelatedTransactionData.transactions[0].id 
            }),
            expect.objectContaining({ 
              account: mockRelatedTransactionData.transactions[1].account_name, 
              amount: mockRelatedTransactionData.transactions[1].amount,
              id: mockRelatedTransactionData.transactions[1].id 
            }),
          ]),
          original_transaction_ids: [mockRelatedTransactionData.transactions[0].id, mockRelatedTransactionData.transactions[1].id],
          date: expect.any(String), // Accept any string for the date
          status: mockRelatedTransactionData.transactions[0].status,
        })
      );
    });
    // console.log("TEST LOG: PUT call verified. Waiting for success message..."); // Remove Log 10

    // Check for success message
    expect(await screen.findByText(/Transaction updated successfully/i)).toBeInTheDocument();
    // // console.log("TEST LOG: Success message found."); // Remove Log 11
    
    // Uncomment navigation check and increase timeout
    await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/transactions');
    }, { timeout: 2000 }); // Increase waitFor timeout to 2000ms
  });

  test('renders error message when transaction fetch fails', async () => {
    const errorMessage = 'Failed to load transaction data';
    axiosInstance.get.mockImplementation((url) => {
      if (url.includes(`/api/v1/transactions/${mockTransactionId}/related`)) {
        return Promise.reject({ response: { data: { error: errorMessage } } });
      }
      if (url.includes('/api/v1/accounts/details')) {
        return Promise.resolve({ data: mockAccountsData });
      }
      return Promise.reject(new Error(`Unhandled GET request: ${url}`));
    });

    render(<EditTransaction />);

    expect(await screen.findByText(new RegExp(errorMessage, 'i'))).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Back to Transactions/i })).toBeInTheDocument();
    expect(screen.queryByLabelText(/Payee/i)).not.toBeInTheDocument();
  });

  test('handles update failure', async () => {
    const user = userEvent.setup();
    const updateErrorMessage = 'Failed to update transaction';
    axiosInstance.put.mockRejectedValue({ response: { data: { error: updateErrorMessage } } });
    
    render(<EditTransaction />);

    expect(await screen.findByRole('heading', { name: /Edit Transaction/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Update Transaction/i }));

    expect(await screen.findByText(new RegExp(updateErrorMessage, 'i'))).toBeInTheDocument();
    expect(axiosInstance.put).toHaveBeenCalledTimes(1);
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});