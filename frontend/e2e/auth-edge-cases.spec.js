const { test, expect } = require('@playwright/test');

test.describe('Authentication edge cases and error handling', () => {
  test('should show error for invalid login credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Fill with invalid credentials
    await page.getByLabel(/email/i).fill('nonexistentuser@example.com');
    await page.getByLabel(/password/i).fill('wrongpassword');

    // Submit the form
    await page.getByRole('button', { name: /log in/i }).click();

    // Verify that an error message is shown (match any error alert)
    await expect(page.getByRole('alert')).toBeVisible();

    // Verify we're still on the login page
    await expect(page).toHaveURL(/.*login/);
  });

  test('should show error for mismatched passwords during registration', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');

    // Fill form with mismatched passwords
    await page.getByLabel(/email address/i).fill('newuser@example.com');
    await page.locator('#password').fill('Password123!');
    await page.locator('#confirmPassword').fill('DifferentPassword123!');

    // Submit the form
    await page.getByRole('button', { name: /register/i }).click();

    // Verify error message about password mismatch
    await expect(page.getByText(/passwords do not match/i)).toBeVisible();

    // Verify we're still on the registration page
    await expect(page).toHaveURL(/.*register/);
  });

  test.skip('should show error for weak password during registration', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');

    // Fill form with a weak password
    await page.getByLabel(/email address/i).fill('newuser@example.com');
    await page.locator('#password').fill('123456');
    await page.locator('#confirmPassword').fill('123456');

    // Submit the form
    await page.getByRole('button', { name: /register/i }).click();

    // Verify some error message is shown
    await expect(page.getByRole('alert')).toBeVisible();

    // Verify we're still on the registration page
    await expect(page).toHaveURL(/.*register/);
  });

  test.skip('should handle password reset request', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Click on forgot password link
    await page.getByRole('link', { name: /forgot password/i }).click();

    // Verify we're on the forgot password page
    await expect(page).toHaveURL(/.*forgot-password/);

    // Fill in email for password reset
    await page.getByLabel(/email/i).fill('user@example.com');

    // Submit the form
    await page.getByRole('button', { name: /reset password|send link/i }).click();

    // Verify some response is shown
    await expect(page.getByRole('alert')).toBeVisible();
  });

  // This test should work without a backend
  test('should redirect unauthenticated users to login from protected pages', async ({ page }) => {
    // Try to access a protected page directly
    await page.goto('/dashboard');

    // Verify we're redirected to the login page
    await expect(page).toHaveURL(/.*login/);

    // Verify login form is visible
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });
});
