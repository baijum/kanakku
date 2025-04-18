# Kanakku Tests

This directory contains older test files that are not currently being used. We've moved the active tests to be alongside their respective components in the `src` directory.

## Current Testing Setup

The active tests are located in:
- `src/App.test.js` - Basic test for the App component
- `src/components/BasicTest.test.js` - Simple test component for reference
- `src/components/Auth/Register.test.jsx` - Tests for the Register component
- `src/components/AddTransaction.test.js` - Tests for the AddTransaction component
- `src/components/ViewTransactions.test.js` - Tests for the ViewTransactions component

## Running Tests

You can run tests using the following npm scripts:

- `npm test` - Run all active tests (ignores tests in this directory)
- `npm run test:ci` - Run all tests in CI mode (no watch mode)
- `npm run test:register` - Run only the Register component tests
- `npm run test:addtransaction` - Run only the AddTransaction component tests
- `npm run test:viewtransactions` - Run only the ViewTransactions component tests
- `npm run test:basic` - Run only the BasicTest component tests

## Test Implementation

The tests use:

1. **Jest** - For running tests and assertions
2. **React Testing Library** - For rendering and interacting with components
3. **Component Mocking** - To avoid React Router context issues
4. **Axios Mocking** - To mock API calls

## Common Issues and Fixes

1. **React Router Context Errors**:
   - We mock React Router components to avoid context issues
   - Use the pattern in existing test files for new tests

2. **Axios/API Mocking**:
   - Use jest.mock('axios') to mock axios
   - Implement specific mock responses based on URL patterns

3. **Form Elements**:
   - When testing form elements, ensure labels are properly associated with inputs using htmlFor/id pairs