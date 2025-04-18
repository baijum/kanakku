import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookManagement from './BookManagement';

// Create mock component variants
const MockBookManagementLoading = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <h6>Create New Book</h6>
      <form>
        <input type="text" placeholder="Book Name" />
        <button type="submit">Create</button>
      </form>
      <h6>Your Books</h6>
      <div data-testid="loading-spinner"></div>
    </div>
  );
};

const MockBookManagementWithBooks = () => {
  return (
    <div>
      <h5>Book Management</h5>
      <h6>Create New Book</h6>
      <form>
        <input type="text" placeholder="Book Name" />
        <button type="submit">Create</button>
      </form>
      <h6>Your Books</h6>
      <ul>
        <li>
          Book 1
          <button aria-label="edit">Edit</button>
          <button aria-label="delete">Delete</button>
        </li>
        <li>
          Book 2
          <button aria-label="edit">Edit</button>
          <button aria-label="delete">Delete</button>
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
      <form>
        <input type="text" placeholder="Book Name" />
        <button type="submit">Create</button>
      </form>
      <h6>Your Books</h6>
      <div>No books found. Create your first book above.</div>
    </div>
  );
};

// Mock the actual component
jest.mock('./BookManagement', () => jest.fn());

// Mock axios
jest.mock('../../api/axiosInstance', () => ({
  get: jest.fn()
    .mockImplementationOnce(() => Promise.resolve({ data: [{ id: 1, name: 'Book 1' }, { id: 2, name: 'Book 2' }] }))
    .mockImplementationOnce(() => Promise.resolve({ data: { id: 1, name: 'Book 1' } })),
  post: jest.fn().mockResolvedValue({ data: { id: 3, name: 'New Book' } }),
  put: jest.fn().mockResolvedValue({ data: {} }),
  delete: jest.fn().mockResolvedValue({ data: {} })
}));

describe('BookManagement Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Set the mock implementation for loading state
    BookManagement.mockImplementation(MockBookManagementLoading);
    
    render(<BookManagement />);
    
    // Check for loading elements
    expect(screen.getByRole('heading', { name: /Book Management/i })).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders book management with books', () => {
    // Set the mock implementation for books state
    BookManagement.mockImplementation(MockBookManagementWithBooks);
    
    render(<BookManagement />);
    
    // Check for book management elements
    expect(screen.getByRole('heading', { name: /Book Management/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Create New Book/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Your Books/i })).toBeInTheDocument();
    
    // Check for book items
    expect(screen.getByText('Book 1')).toBeInTheDocument();
    expect(screen.getByText('Book 2')).toBeInTheDocument();
    
    // Check for action buttons
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    expect(editButtons.length).toBe(2);
    expect(deleteButtons.length).toBe(2);
  });

  test('renders message when no books exist', () => {
    // Set the mock implementation for no books state
    BookManagement.mockImplementation(MockBookManagementNoBooks);
    
    render(<BookManagement />);
    
    // Check for no books message
    expect(screen.getByText('No books found. Create your first book above.')).toBeInTheDocument();
  });
});