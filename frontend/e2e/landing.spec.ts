import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
    test('should load successfully and have correct title', async ({ page }) => {
        // 1. Go to landing page
        await page.goto('/');

        // 2. Check title (adjust based on your actual title)
        await expect(page).toHaveTitle(/QA Test Code Generator|Tester/i);

        // 3. Check for main elements
        await expect(page.getByRole('button', { name: /Login/i })).toBeVisible();
        await expect(page.getByPlaceholder(/Paste your source code/i)).toBeVisible();
    });
});
