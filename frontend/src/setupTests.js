// Set up test environment
import '@testing-library/jest-dom';

// Suppress React Router future flag warnings
const originalError = console.error;
const originalWarn = console.warn;

// Filter out specific React Router warnings
console.warn = (...args) => {
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    (args[0].includes('React Router Future Flag Warning') ||
     args[0].includes('v7_startTransition') ||
     args[0].includes('v7_relativeSplatPath'))
  ) {
    return; // Suppress these specific warnings
  }
  originalWarn.apply(console, args);
};

// Filter out specific errors related to React Router
console.error = (...args) => {
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    (args[0].includes('Router') ||
     args[0].includes('basename'))
  ) {
    return; // Suppress these specific errors
  }

  // Suppress transaction update error messages in tests
  if (
    args[0] &&
    typeof args[0] === 'string' &&
    args[0].includes('Error updating transaction:')
  ) {
    return; // Suppress transaction update errors
  }

  originalError.apply(console, args);
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
