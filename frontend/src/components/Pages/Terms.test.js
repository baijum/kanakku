import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Terms from './Terms';

describe('Terms Component', () => {
  test('renders terms of service heading', () => {
    render(<Terms />);
    expect(screen.getByRole('heading', { name: /Terms of Service/i })).toBeInTheDocument();
  });

  test('renders all terms sections', () => {
    render(<Terms />);

    // Check for section headings
    expect(screen.getByText(/1\. Acceptance of Terms/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Description of Service/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. User Accounts/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. Privacy/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Data Security/i)).toBeInTheDocument();
    expect(screen.getByText(/6\. Limitation of Liability/i)).toBeInTheDocument();
    expect(screen.getByText(/7\. Changes to Terms/i)).toBeInTheDocument();
    expect(screen.getByText(/8\. Contact Information/i)).toBeInTheDocument();
  });

  test('renders contact email', () => {
    render(<Terms />);
    expect(screen.getByText(/baiju\.m\.mail@gmail\.com/i)).toBeInTheDocument();
  });
});
