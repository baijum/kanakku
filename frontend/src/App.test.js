import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';
import { BrowserRouter } from 'react-router-dom';

// Mock components and API calls to simplify the test
jest.mock('./components/Auth/Login', () => () => <div data-testid="mock-login">Mock Login</div>);
jest.mock('./components/Auth/Register', () => () => <div data-testid="mock-register">Mock Register</div>);
jest.mock('./components/Dashboard', () => () => <div data-testid="mock-dashboard">Mock Dashboard</div>);
jest.mock('./api/axiosInstance', () => ({
  __esModule: true,
  default: jest.fn()
}));

test('renders the app component', () => {
  // Render App with BrowserRouter
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  
  // Check if the App loads without crashing
  expect(screen.getByText(/Loading/i) || screen.getByTestId('mock-login') || 
         screen.getByTestId('mock-dashboard')).toBeInTheDocument();
});