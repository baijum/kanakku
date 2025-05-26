import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BasicTest from './BasicTest';

test('renders basic test component', () => {
  render(<BasicTest />);

  // Check for heading
  expect(screen.getByText(/Basic Test Component/i)).toBeInTheDocument();

  // Check for paragraph
  expect(screen.getByText(/This is a simple component for testing purposes/i)).toBeInTheDocument();
});
