import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Basic test suite for the App component

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
  });

  test('displays a welcome message', () => {
    render(<App />);
    // Assuming the App component renders a header with the text "Kanakku" or similar
    const welcomeText = screen.getByText(/kanakku/i);
    expect(welcomeText).toBeInTheDocument();
  });
}); 