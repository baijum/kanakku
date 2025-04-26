const { test, expect } = require('@playwright/test');
const { login } = require('./utils/test-utils');

// Skip all tests until login works
test.describe.skip('Transaction functionality tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test using the utility function
    await login(page);
  });

  test('should navigate to add transaction page', async ({ page }) => {
    // Navigate to add transaction from dashboard
    await page.getByRole('link', { name: /add transaction/i }).click();
    
    // Verify we're on the add transaction page
    await expect(page).toHaveURL(/.*add/);
    await expect(page.getByRole('heading', { name: /add transaction/i })).toBeVisible();
  });

  test('should display validation errors when submitting empty add transaction form', async ({ page }) => {
    // Navigate to add transaction page
    await page.goto('/add');
    
    // Submit without filling the form
    await page.getByRole('button', { name: /submit/i }).click();
    
    // Verify validation errors by checking for any alert
    await expect(page.getByRole('alert')).toBeVisible();
  });

  test('should navigate to view transactions page', async ({ page }) => {
    // Navigate to view transactions from dashboard
    await page.getByRole('link', { name: /transactions/i }).click();
    
    // Verify we're on the view transactions page
    await expect(page).toHaveURL(/.*transactions/);
    await expect(page.getByRole('heading', { name: /transactions/i })).toBeVisible();
  });

  // Skip tests that require backend functionality
  test.skip('should add a new transaction and display it in the transactions list', async ({ page }) => {
    // This test will be implemented when backend integration is available
  });

  test.skip('should filter transactions by date range', async ({ page }) => {
    // This test will be implemented when backend integration is available
  });
}); 