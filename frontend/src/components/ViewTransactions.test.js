import '@testing-library/jest-dom';

// Mock axios and axiosInstance
jest.mock('axios');
jest.mock('../api/axiosInstance');

describe('ViewTransactions Component', () => {
  // This test verifies that the export ledger endpoint URL has been updated
  // from '/api/v1/export/ledger' to '/api/v1/ledgertransactions'
  test('uses updated API endpoint for ledger export', async () => {
    // Read the ViewTransactions source file to verify it contains the correct URL
    const fs = require('fs');
    const viewTransactionsPath = require.resolve('./ViewTransactions');
    const source = fs.readFileSync(viewTransactionsPath, 'utf8');

    // Check that the new endpoint is present and the old endpoint is not
    expect(source).toContain('/api/v1/ledgertransactions');
    expect(source).not.toContain('/api/v1/export/ledger');
  });
});
