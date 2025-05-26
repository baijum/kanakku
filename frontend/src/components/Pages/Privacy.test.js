import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Privacy from './Privacy';

describe('Privacy Component', () => {
  test('renders privacy statement heading', () => {
    render(<Privacy />);
    // Use query by text instead of role since there are multiple headings
    expect(screen.getByText('Privacy Statement')).toBeInTheDocument();
  });

  test('renders all privacy policy sections', () => {
    render(<Privacy />);

    // Check for section headings
    expect(screen.getByText(/1\. Introduction/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Information We Collect/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. How We Use Your Information/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. Data Security/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Data Retention/i)).toBeInTheDocument();
    expect(screen.getByText(/6\. Your Rights/i)).toBeInTheDocument();
    expect(screen.getByText(/7\. Third-Party Services/i)).toBeInTheDocument();
    expect(screen.getByText(/8\. Changes to This Privacy Statement/i)).toBeInTheDocument();
    expect(screen.getByText(/9\. Contact Us/i)).toBeInTheDocument();
  });

  test('renders contact email', () => {
    render(<Privacy />);
    expect(screen.getByText(/baiju\.m\.mail@gmail\.com/i)).toBeInTheDocument();
  });
});
