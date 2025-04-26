# Frontend Code Patterns and Best Practices

This document outlines the key patterns and best practices to follow when developing the Kanakku frontend.

## API Requests

### Use axiosInstance for All API Requests

Always use the configured axios instance from `src/api/axiosInstance.js` for all API requests. This instance is configured with:

- Authentication headers
- CSRF token management
- Error interceptors
- Base URL configuration

```javascript
// CORRECT: Import the configured instance
import axiosInstance from '../../api/axiosInstance';

// Making API requests
const fetchData = async () => {
  try {
    const response = await axiosInstance.get('/api/v1/endpoint');
    // Process response
  } catch (error) {
    // Handle error
  }
};
```

### NEVER Import Axios Directly

```javascript
// INCORRECT: Never import axios directly
import axios from 'axios';  // ❌ Wrong! 

// This bypasses authentication and other important configurations
const response = await axios.get('/api/endpoint');  // ❌ Wrong!
```

### API Request Best Practices

1. Always handle errors with try/catch blocks
2. Show loading states during API calls
3. Validate API responses before updating state
4. Use async/await for cleaner code

## Component Structure

1. Keep components small and focused on a single responsibility
2. Use React hooks for state management
3. Create custom hooks for reusable logic
4. Follow a consistent naming convention:
   - Components: PascalCase (e.g., `TransactionList.jsx`)
   - Hooks: camelCase with `use` prefix (e.g., `useTransactions.js`)
   - Utilities: camelCase (e.g., `formatCurrency.js`)

## State Management

1. Use React hooks for local component state
2. Use context for shared state across components
3. Consider extracting complex state logic into custom hooks
4. Use reducers for complex state transitions

## Form Handling

1. Use controlled components for form inputs
2. Implement proper validation
3. Show clear error messages
4. Disable the submit button during form submission

## Styling

1. Use Material-UI (MUI) components for consistent UI
2. Use the theme for colors, spacing, and typography
3. Avoid inline styles where possible
4. Use styled components for custom styling

## Testing

1. Write tests for critical functionality
2. Test user flows rather than implementation details
3. Mock API calls in tests
4. Use data-testid attributes for test selectors 