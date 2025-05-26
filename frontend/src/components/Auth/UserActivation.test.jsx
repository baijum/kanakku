import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserActivation from './UserActivation';
import axiosInstance from '../../api/axiosInstance';

// Mock axios instance
jest.mock('../../api/axiosInstance', () => ({
  post: jest.fn(),
}));

describe('UserActivation Component', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
  };

  const mockOnUserUpdate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders correctly with active user', () => {
    render(<UserActivation user={mockUser} onUserUpdate={mockOnUserUpdate} />);

    expect(screen.getByText(/Account Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Your account is currently/, { exact: false })).toBeInTheDocument();

    // Use a more specific selector to find the status in the strong element
    expect(screen.getByText((content, element) => {
      return element.tagName.toLowerCase() === 'strong' && content === 'Active';
    })).toBeInTheDocument();

    const switch_element = screen.getByRole('checkbox');
    expect(switch_element).toBeChecked();
  });

  test('renders correctly with inactive user', () => {
    const inactiveUser = { ...mockUser, is_active: false };
    render(<UserActivation user={inactiveUser} onUserUpdate={mockOnUserUpdate} />);

    expect(screen.getByText(/Account Status/i)).toBeInTheDocument();

    // Fix: Use getAllByText and check the first one since we know there are multiple elements
    const paragraphs = screen.getAllByText((content, element) => {
      return element.tagName.toLowerCase() === 'p' && content.includes('Your account is currently');
    });
    expect(paragraphs.length).toBeGreaterThan(0);
    expect(paragraphs[0]).toBeInTheDocument();

    // Use a more specific selector to find the status in the strong element
    expect(screen.getByText((content, element) => {
      return element.tagName.toLowerCase() === 'strong' && content === 'Inactive';
    })).toBeInTheDocument();

    const switch_element = screen.getByRole('checkbox');
    expect(switch_element).not.toBeChecked();
  });

  test('shows confirmation dialog when toggling status', () => {
    render(<UserActivation user={mockUser} onUserUpdate={mockOnUserUpdate} />);

    // Toggle the switch
    fireEvent.click(screen.getByRole('checkbox'));

    // Check if dialog appears
    expect(screen.getByText(/Deactivate Account/i)).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to deactivate your account/i)).toBeInTheDocument();
  });

  test('calls API and updates user when confirming status change', async () => {
    const mockResponse = {
      data: {
        message: 'Account deactivated successfully',
        user: { ...mockUser, is_active: false }
      }
    };
    axiosInstance.post.mockResolvedValueOnce(mockResponse);

    render(<UserActivation user={mockUser} onUserUpdate={mockOnUserUpdate} />);

    // Toggle the switch
    fireEvent.click(screen.getByRole('checkbox'));

    // Click confirm button in dialog
    fireEvent.click(screen.getByText('Deactivate'));

    // Wait for API call to complete
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/v1/auth/toggle-status', {
        is_active: false
      });
    });

    await waitFor(() => {
      expect(mockOnUserUpdate).toHaveBeenCalledWith(mockResponse.data.user);
    });

    await waitFor(() => {
      expect(screen.getByText(/Account deactivated successfully/i)).toBeInTheDocument();
    });
  });

  test('shows error message when API call fails', async () => {
    const errorMessage = 'Failed to update account status';
    axiosInstance.post.mockRejectedValueOnce({
      response: { data: { error: errorMessage } }
    });

    render(<UserActivation user={mockUser} onUserUpdate={mockOnUserUpdate} />);

    // Toggle the switch
    fireEvent.click(screen.getByRole('checkbox'));

    // Click confirm button in dialog
    fireEvent.click(screen.getByText('Deactivate'));

    // Wait for API call to complete
    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith('/api/v1/auth/toggle-status', {
        is_active: false
      });
    });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});
