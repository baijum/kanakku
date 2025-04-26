# End-to-End Testing with Playwright

This directory contains end-to-end tests for the Kanakku application using Playwright.

## Test Structure

- `auth.spec.js` - Tests for authentication flows (login, registration)
- `auth-edge-cases.spec.js` - Tests for authentication edge cases and error handling
- `dashboard.spec.js` - Tests for the dashboard and main navigation
- `transactions.spec.js` - Tests for transaction-related functionality
- `utils/test-utils.js` - Shared utilities and helper functions

## Running Tests

### Prerequisites

Make sure you have installed the required dependencies:

```bash
npm install
```

And installed Playwright browsers:

```bash
npx playwright install
```

### Running All Tests

```bash
npm run test:e2e
```

### Running Tests with UI Mode

UI mode provides a visual interface for running and debugging tests:

```bash
npm run test:e2e:ui
```

### Running Tests in Debug Mode

For step-by-step debugging:

```bash
npm run test:e2e:debug
```

### Running a Specific Test File

```bash
npx playwright test e2e/auth.spec.js
```

## Test Reports

After running tests, you can view HTML reports:

```bash
npx playwright show-report
```

## Notes for Test Development

1. Many tests are marked with `test.skip()` as they require a working backend or specific test data. Update these as needed for your environment.

2. The tests use the common utilities in `utils/test-utils.js` for shared functionality like login.

3. The tests assume standard elements with appropriate ARIA roles and labels. If the application UI changes, tests may need updating.

4. For CI/CD integration, the Playwright configuration automatically sets up retries and other CI-friendly settings when the CI environment variable is set. 