/**
 * Common utilities for Playwright E2E tests
 */

/**
 * Login helper function that can be reused across test files
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {Object} options - Login options
 * @param {string} options.email - Email to login with
 * @param {string} options.password - Password to login with
 * @param {boolean} options.verifyRedirect - Whether to verify redirect to dashboard
 */
async function login(page, { email = 'testuser@example.com', password = 'Password123!', verifyRedirect = true } = {}) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /log in/i }).click();
  
  if (verifyRedirect) {
    // Wait for redirect to dashboard
    await page.waitForURL(/.*dashboard/);
  }
}

/**
 * Register a new user
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {Object} options - Registration options
 * @param {string} options.email - Email for registration
 * @param {string} options.password - Password for registration
 * @param {string} options.confirmPassword - Confirm password
 */
async function registerUser(page, { 
  email = `testuser${Date.now()}@example.com`, 
  password = 'Password123!', 
  confirmPassword = 'Password123!' 
} = {}) {
  await page.goto('/register');
  await page.getByLabel(/email address/i).fill(email);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByLabel(/confirm password/i).fill(confirmPassword);
  await page.getByRole('button', { name: /register/i }).click();
}

/**
 * Generate random test data
 */
function generateTestData() {
  const timestamp = Date.now();
  return {
    email: `testuser${timestamp}@example.com`,
    password: 'Password123!',
  };
}

/**
 * Wait for notifications to appear and disappear
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {Object} options
 * @param {string} options.text - Text to look for in notification
 */
async function waitForNotification(page, { text }) {
  // Wait for notification to appear
  await page.getByText(text).waitFor({ state: 'visible' });
  // Wait for notification to disappear (if it auto-dismisses)
  try {
    await page.getByText(text).waitFor({ state: 'hidden', timeout: 10000 });
  } catch (e) {
    // It's okay if the notification stays visible
  }
}

module.exports = {
  login,
  registerUser,
  generateTestData,
  waitForNotification
}; 