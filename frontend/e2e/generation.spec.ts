import { test, expect } from '@playwright/test';

test.describe('Code Generation Flow', () => {

    test('should show login prompt when not logged in', async ({ page }) => {
        await page.goto('/');

        // Attempt to type code
        await page.getByPlaceholder(/Paste your source code/i).fill('print("hello")');

        // Check if Generate button is actually a Login button or shows login requirement
        // In our UI: store.isLoggedIn ? 'Generate' : 'Login'
        await expect(page.getByRole('button', { name: 'Login with Google' })).toBeVisible();

        // Click button
        await page.getByRole('button', { name: 'Login with Google' }).click();
    });

    test('should Generate code when logged in (Mocked)', async ({ page }) => {
        // Mock /api/user/status to simulate logged-in user
        await page.route('/api/user/status', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    email: 'test@example.com',
                    weekly_usage: 0,
                    weekly_limit: 30,
                    remaining: 30
                })
            });
        });

        // Mock Turnstile properly (before page load to ensure window.turnstile exists)
        await page.addInitScript(() => {
            // @ts-ignore
            window.turnstile = {
                render: (el: any, options: any) => {
                    options.callback('mock_turnstile_token');
                    return 'widget_id';
                },
                remove: () => { },
                reset: () => { }
            };
        });

        await page.goto('/');

        // Verify button changes to "Generate"
        await expect(page.getByRole('button', { name: /Generate/i })).toBeVisible();

        // Input code
        const inputCode = 'print("hello world")';
        await page.getByPlaceholder(/Paste your source code/i).fill(inputCode);

        // Debug Network and Console
        page.on('console', msg => console.log('LOG:', msg.text()));

        // Mock API response for Generation with correct SSE format
        await page.route(/\/api\/generate/, async route => {
            console.log('Intercepted route:', route.request().url());
            await route.fulfill({
                status: 200,
                contentType: 'text/event-stream',
                body: 'data: {"type": "chunk", "content": "def test_hello():\\n    assert True"}\n\ndata: {"type": "done"}\n\n'
            });
        });

        // Click Generate
        await page.getByRole('button', { name: /Generate/i }).click();

        // Wait for result
        // Use a more specific locator or wait for the text directly
        await expect(page.locator('code')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('code')).toContainText('def test_hello');
    });
});
