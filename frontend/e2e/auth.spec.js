const { test, expect } = require('@playwright/test');

test.describe('Authentication flow tests', () => {
  // Enable all tests
  test('should navigate to the registration page', async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');

    // Check if there's a login link on the home page and click it first
    const loginLink = page.getByRole('link', { name: /sign in/i });
    if (await loginLink.isVisible()) {
      await loginLink.click();
    }

    // From login page, click on "Sign Up" link
    await page.getByRole('link', { name: /sign up/i }).click();

    // Verify that we're on the registration page
    await expect(page).toHaveURL(/.*register/);
    await expect(page.getByRole('heading', { name: /register/i })).toBeVisible();
  });

  test('should show validation errors on empty registration form submission', async ({ page }) => {
    // Navigate to the registration page
    await page.goto('/register');

    // Try to submit the form without filling it
    await page.getByRole('button', { name: /register/i }).click();

    // Verify validation errors are shown
    await expect(page.getByText(/all fields are required/i)).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');

    // Check if there's already a login link on the home page
    const loginLink = page.getByRole('link', { name: /sign in/i });
    if (await loginLink.isVisible()) {
      await loginLink.click();
    }

    // Verify that we're on the login page
    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors on empty login form submission', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');

    // Try to submit the form without filling it
    await page.getByRole('button', { name: /log in/i }).click();

    // Verify validation errors are shown - using the actual error message
    await expect(page.getByText(/email and password are required/i)).toBeVisible();
  });

  // These tests need a backend - skip for now
  test.skip('should register a new user and redirect to dashboard', async ({ page }) => {
    // Navigate to the registration page
    await page.goto('/register');

    // Fill the registration form
    const email = `testuser${Date.now()}@example.com`;
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('Password123!');
    await page.getByLabel(/confirm password/i).fill('Password123!');

    // Submit the form
    await page.getByRole('button', { name: /register/i }).click();

    // Verify that we're redirected to the dashboard after successful registration
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.skip('should login a user and redirect to dashboard', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');

    // Fill the login form with valid credentials
    await page.getByLabel(/email/i).fill('testuser@example.com');
    await page.getByLabel(/^password$/i).fill('Password123!');

    // Submit the form
    await page.getByRole('button', { name: /log in/i }).click();

    // Verify that we're redirected to the dashboard after successful login
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
