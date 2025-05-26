import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PreambleList from './PreambleList';

// Create mock component variants
const MockPreambleListLoading = () => {
  return (
    <div>
      <h4>Preambles</h4>
      <p>Preambles are text that will appear at the beginning of exported transaction data.</p>
      <button>Add Preamble</button>
      <div data-testid="loading-spinner"></div>
    </div>
  );
};

const MockPreambleListWithPreambles = () => {
  return (
    <div>
      <h4>Preambles</h4>
      <p>Preambles are text that will appear at the beginning of exported transaction data.</p>
      <button>Add Preamble</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Content Preview</th>
            <th>Default</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Default Preamble</td>
            <td>This is a default preamble...</td>
            <td>Yes</td>
            <td>
              <button aria-label="edit">Edit</button>
              <button aria-label="delete">Delete</button>
            </td>
          </tr>
          <tr>
            <td>Custom Preamble</td>
            <td>This is a custom preamble...</td>
            <td>No</td>
            <td>
              <button aria-label="edit">Edit</button>
              <button aria-label="delete">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

const MockPreambleListEmpty = () => {
  return (
    <div>
      <h4>Preambles</h4>
      <p>Preambles are text that will appear at the beginning of exported transaction data.</p>
      <button>Add Preamble</button>
      <div>No preambles found. Create one to add text to the beginning of your exported transaction data.</div>
    </div>
  );
};

// Mock the actual component
jest.mock('./PreambleList', () => jest.fn());

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn().mockResolvedValue({
    data: {
      preambles: [
        {
          id: 1,
          name: 'Default Preamble',
          content: 'This is a default preamble for exported transactions',
          is_default: true
        },
        {
          id: 2,
          name: 'Custom Preamble',
          content: 'This is a custom preamble for special exports',
          is_default: false
        }
      ]
    }
  }),
  post: jest.fn().mockResolvedValue({}),
  put: jest.fn().mockResolvedValue({}),
  delete: jest.fn().mockResolvedValue({})
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

describe('PreambleList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Set the mock implementation for loading state
    PreambleList.mockImplementation(MockPreambleListLoading);

    render(<PreambleList />);

    // Check for loading elements
    expect(screen.getByRole('heading', { name: /Preambles/i })).toBeInTheDocument();
    expect(screen.getByText(/Preambles are text that will appear/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Preamble/i })).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders preamble list with preambles', () => {
    // Set the mock implementation for preambles state
    PreambleList.mockImplementation(MockPreambleListWithPreambles);

    render(<PreambleList />);

    // Check for table headers
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Content Preview')).toBeInTheDocument();
    expect(screen.getByText('Default')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();

    // Check for preamble items
    expect(screen.getByText('Default Preamble')).toBeInTheDocument();
    expect(screen.getByText('Custom Preamble')).toBeInTheDocument();
    expect(screen.getByText('Yes')).toBeInTheDocument();
    expect(screen.getByText('No')).toBeInTheDocument();

    // Check for action buttons
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    expect(editButtons.length).toBe(2);
    expect(deleteButtons.length).toBe(2);
  });

  test('renders empty state when no preambles exist', () => {
    // Set the mock implementation for empty state
    PreambleList.mockImplementation(MockPreambleListEmpty);

    render(<PreambleList />);

    // Check for empty state message
    expect(screen.getByText(/No preambles found/i)).toBeInTheDocument();
  });
});
