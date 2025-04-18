# Kanakku Frontend

This is the React frontend for the Kanakku expense tracking application. It provides a modern, responsive user interface for managing financial transactions.

## Technology Stack

- **React 18**: Core UI library
- **Material-UI (MUI)**: Component library for styling
- **Axios**: HTTP client for API requests
- **React Router 6**: For client-side routing
- **Jest/React Testing Library**: For testing

## Project Structure

```
frontend/
├── public/             # Static files
├── src/                # Source code
│   ├── components/     # React components
│   │   ├── Auth/       # Authentication components
│   │   ├── Accounts/   # Account management components
│   │   ├── Transactions/ # Transaction components
│   │   └── ...         # Other components
│   ├── api/            # API client and services
│   ├── tests/          # Test files
│   ├── App.js          # Main application component
│   └── index.js        # Application entry point
├── package.json        # Dependencies and scripts
└── ...
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Development Conventions

### Component Structure

- Use functional components with hooks
- Keep components small and focused
- Use meaningful prop and variable names
- Place related components in the same directory
- Use prop types or TypeScript for type checking

### State Management

- Use React hooks for local component state
- Use context when state needs to be shared between multiple components
- Avoid prop drilling by extracting shared logic into custom hooks

### API Integration

- Use the configured Axios instance from `api/axiosInstance.js`
- Handle API errors with try/catch blocks
- Show loading indicators during API calls
- Validate API responses before updating state

### Styling

- Use Material-UI (MUI) components for consistent styling
- Use theme variables for colors, spacing, and typography
- Follow responsive design principles

### Currency Handling

- Default currency is INR (₹)
- Display currency symbol to the left of amount for INR
- Format currency values appropriately (e.g., ₹1,000.00)

## Testing

Run all tests:
```bash
npm test
```

Run a specific test:
```bash
npm test -- --testMatch="**/ComponentName.test.jsx"
```

### Test Conventions

- Test component behavior, not implementation details
- Mock API calls using Jest mock functions
- Test user interactions using React Testing Library
- Write meaningful test descriptions

## Available Scripts

- `npm start`: Start development server
- `npm test`: Run tests
- `npm run build`: Build for production
- `npm run test:ci`: Run tests in CI mode
- `npm run test:basic`: Run basic tests
- `npm run test:register`: Run registration tests
- `npm run test:addtransaction`: Run transaction tests
- `npm run test:viewtransactions`: Run view transactions tests

## Environment

The frontend is configured to proxy API requests to `http://localhost:8000` for local development. 