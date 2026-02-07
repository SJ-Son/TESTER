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

        // Should see a login prompt or redirection (assuming Google Login initiates)
        // For now, just verifying the initial state is good.
    });

    test('should Generate code when logged in (Mocked)', async ({ page }) => {
        // Mock Login by setting localStorage
        await page.addInitScript(() => {
            localStorage.setItem('tester_token', 'mock_token');
            localStorage.setItem('tester_user', JSON.stringify({ name: 'Test User', email: 'test@example.com' }));
        });

        await page.goto('/');

        // Mock Login: Ensure storage is set before store initializes or force reload
        await page.evaluate(() => {
            localStorage.setItem('tester_token', 'mock_token');
            localStorage.setItem('tester_user', JSON.stringify({ name: 'Test User', email: 'test@example.com' }));
        });

        // Reload to let Pinia pick up the token from localStorage
        await page.reload();

        // 🚨 CRITICAL: Pinia store might be prone to hydration issues in test.
        // We force the state to be logged in by manipulating the window object if accessing store is possible,
        // or re-setting localStorage and dispatching a storage event to ensure reactivity.
        await page.evaluate(() => {
            localStorage.setItem('tester_token', 'mock_token');
            window.dispatchEvent(new Event('storage'));
        });

        // Verify button changes to "Generate" or locate the button by text content
        // In the Vue component: authStore.isLoggedIn ? 'Generate' : 'Login'
        // And there's a span inside the button
        // Wait for the "Please Login First" overlay to disappear
        await expect(page.locator('text=Please Login First')).not.toBeVisible({ timeout: 10000 });

        // Verify button changes to "Generate"
        await expect(page.locator('button', { hasText: 'Generate' })).toBeVisible({ timeout: 10000 });

        // Input code
        const inputCode = 'print("hello world")';
        await page.getByPlaceholder(/Paste your source code/i).fill(inputCode);

        // Debug Network and Console
        page.on('request', request => console.log('>>', request.method(), request.url()));
        page.on('response', response => console.log('<<', response.status(), response.url()));
        page.on('console', msg => console.log('LOG:', msg.text()));

        // Mock API response for Generation
        await page.route(/\/api\/generate/, async route => {
            console.log('Intercepted route:', route.request().url());
            await route.fulfill({
                status: 200,
                contentType: 'text/event-stream',
                body: 'data: {"type": "chunk", "content": "def test_hello():\\n    assert True"}\n\ndata: {"type": "done"}\n\n'
            });
        });

        // Mock Turnstile
        await page.evaluate(() => {
            // @ts-ignore
            window.turnstile = {
                render: (el: any, options: any) => {
                    options.callback('mock_turnstile_token');
                    return 'widget_id';
                }
            };
        });

        // Click Generate
        await page.getByRole('button', { name: /Generate/i }).click();

        // Wait for result
        await expect(page.locator('code')).toContainText('def test_hello');
    });
});
