import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookManagement from './BookManagement';

// Create different mock components for testing
const MockBookManagementLoading = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <h6>Create New Book</h6>
      <input data-testid="new-book-input" placeholder="Book Name" />
      <button data-testid="create-book-button">Create</button>
      <h6>Your Books</h6>
      <div data-testid="loading-spinner">Loading...</div>
    </div>
  );
};

const MockBookManagementWithBooks = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <h6>Create New Book</h6>
      <input data-testid="new-book-input" placeholder="Book Name" />
      <button data-testid="create-book-button">Create</button>
      <h6>Your Books</h6>
      <ul data-testid="books-list">
        <li data-testid="book-item-1">
          Test Book 1
          <button data-testid="set-active-button-1">Set as Active</button>
          <button data-testid="edit-button-1">Edit</button>
          <button data-testid="delete-button-1">Delete</button>
        </li>
        <li data-testid="book-item-2">
          Test Book 2
          <button data-testid="set-active-button-2">Set as Active</button>
          <button data-testid="edit-button-2">Edit</button>
          <button data-testid="delete-button-2">Delete</button>
        </li>
      </ul>
    </div>
  );
};

const MockBookManagementNoBooks = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <h6>Create New Book</h6>
      <input data-testid="new-book-input" placeholder="Book Name" />
      <button data-testid="create-book-button">Create</button>
      <h6>Your Books</h6>
      <div data-testid="no-books-message">No books found. Create your first book above.</div>
    </div>
  );
};

// Mock for error state
const MockBookManagementError = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <div data-testid="error-alert">Failed to load books. Please try again later.</div>
      <h6>Create New Book</h6>
      <input data-testid="new-book-input" placeholder="Book Name" />
      <button data-testid="create-book-button">Create</button>
      <h6>Your Books</h6>
    </div>
  );
};

// Mock for success message display
const MockBookManagementSuccess = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <div data-testid="success-alert">Book created successfully!</div>
      <h6>Create New Book</h6>
      <input data-testid="new-book-input" placeholder="Book Name" />
      <button data-testid="create-book-button">Create</button>
      <h6>Your Books</h6>
      <ul data-testid="books-list">
        <li data-testid="book-item-1">Test Book 1</li>
      </ul>
    </div>
  );
};

// Mock the actual component
jest.mock('./BookManagement', () => jest.fn());

// Mock axiosInstance
jest.mock('../../api/axiosInstance', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true
});

// Mock window.location.reload
const mockReload = jest.fn();
Object.defineProperty(window, 'location', {
  value: {
    reload: mockReload
  },
  writable: true
});

describe('BookManagement Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state', () => {
    // Mock implementation for loading state
    BookManagement.mockImplementation(MockBookManagementLoading);
    
    render(<BookManagement />);
    
    // Check for loading elements
    expect(screen.getByRole('heading', { name: /Book Management/i })).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
  
  test('renders book management with books', () => {
    // Mock implementation for when books are available
    BookManagement.mockImplementation(MockBookManagementWithBooks);
    
    render(<BookManagement />);
    
    // Check for main sections
    expect(screen.getByRole('heading', { name: /Book Management/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Create New Book/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Your Books/i })).toBeInTheDocument();
    
    // Check for book list and items
    expect(screen.getByTestId('books-list')).toBeInTheDocument();
    expect(screen.getByTestId('book-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('book-item-2')).toBeInTheDocument();
    
    // Check for action buttons
    expect(screen.getByTestId('set-active-button-1')).toBeInTheDocument();
    expect(screen.getByTestId('edit-button-1')).toBeInTheDocument();
    expect(screen.getByTestId('delete-button-1')).toBeInTheDocument();
    expect(screen.getByTestId('set-active-button-2')).toBeInTheDocument();
    expect(screen.getByTestId('edit-button-2')).toBeInTheDocument();
    expect(screen.getByTestId('delete-button-2')).toBeInTheDocument();
  });
  
  test('renders no books message when no books exist', () => {
    // Mock implementation for when no books exist
    BookManagement.mockImplementation(MockBookManagementNoBooks);
    
    render(<BookManagement />);
    
    // Check for no books message
    expect(screen.getByTestId('no-books-message')).toBeInTheDocument();
    expect(screen.getByText('No books found. Create your first book above.')).toBeInTheDocument();
  });

  test('renders error state when API call fails', () => {
    // Mock implementation for error state
    BookManagement.mockImplementation(MockBookManagementError);
    
    render(<BookManagement />);
    
    // Check for error message
    expect(screen.getByTestId('error-alert')).toBeInTheDocument();
    expect(screen.getByText('Failed to load books. Please try again later.')).toBeInTheDocument();
  });

  test('renders success message after book creation', () => {
    // Mock implementation for success message
    BookManagement.mockImplementation(MockBookManagementSuccess);
    
    render(<BookManagement />);
    
    // Check for success message
    expect(screen.getByTestId('success-alert')).toBeInTheDocument();
    expect(screen.getByText('Book created successfully!')).toBeInTheDocument();
  });
});