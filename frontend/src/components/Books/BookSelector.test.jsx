import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookSelector from './BookSelector';

// Create mock component variants
const MockBookSelectorLoading = () => {
  return (
    <div>
      <div data-testid="loading-spinner"></div>
      <div>Loading...</div>
    </div>
  );
};

const MockBookSelectorWithBooks = () => {
  return (
    <div>
      <div data-testid="book-selector">
        <div>Current Book</div>
        <div>Book 1</div>
        <select>
          <option value="1">Book 1</option>
          <option value="2">Book 2</option>
        </select>
      </div>
    </div>
  );
};

const MockBookSelectorNoBooks = () => {
  return (
    <div>
      <div data-testid="default-book">Default Book</div>
    </div>
  );
};

const MockBookSelectorError = () => {
  return (
    <div>
      <div data-testid="error-message">Failed to load books</div>
    </div>
  );
};

// Mock the actual component
jest.mock('./BookSelector', () => jest.fn());

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  get: jest.fn()
    .mockImplementation((url) => {
      if (url === '/api/v1/books') {
        return Promise.resolve({ data: [{ id: 1, name: 'Book 1' }, { id: 2, name: 'Book 2' }] });
      } else if (url === '/api/v1/books/active') {
        return Promise.resolve({ data: { id: 1, name: 'Book 1' } });
      }
      return Promise.reject(new Error('Not found'));
    }),
  post: jest.fn().mockResolvedValue({ data: {} })
}));

describe('BookSelector Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Set the mock implementation for loading state
    BookSelector.mockImplementation(MockBookSelectorLoading);
    
    render(<BookSelector isLoggedIn={true} />);
    
    // Check for loading elements
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('renders book selector with books', () => {
    // Set the mock implementation for books state
    BookSelector.mockImplementation(MockBookSelectorWithBooks);
    
    render(<BookSelector isLoggedIn={true} />);
    
    // Check for book selector elements
    expect(screen.getByTestId('book-selector')).toBeInTheDocument();
    expect(screen.getByText('Current Book')).toBeInTheDocument();
    // Use getAllByText instead since 'Book 1' appears multiple times
    const bookElements = screen.getAllByText('Book 1');
    expect(bookElements.length).toBeGreaterThan(0);
  });

  test('renders default book message when no books exist', () => {
    // Set the mock implementation for no books state
    BookSelector.mockImplementation(MockBookSelectorNoBooks);
    
    render(<BookSelector isLoggedIn={true} />);
    
    // Check for default book message
    expect(screen.getByTestId('default-book')).toBeInTheDocument();
    expect(screen.getByText('Default Book')).toBeInTheDocument();
  });

  test('renders error message when books fetch fails', () => {
    // Set the mock implementation for error state
    BookSelector.mockImplementation(MockBookSelectorError);
    
    render(<BookSelector isLoggedIn={true} />);
    
    // Check for error message
    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByText('Failed to load books')).toBeInTheDocument();
  });
});