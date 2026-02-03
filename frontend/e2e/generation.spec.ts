import { test, expect } from '@playwright/test';

test.describe('Code Generation Flow', () => {

    test('should show login prompt when not logged in', async ({ page }) => {
        await page.goto('/');

        // Attempt to type code
        await page.getByPlaceholder(/Paste your source code/i).fill('print("hello")');

        // Check if Generate button is actually a Login button or shows login requirement
        // In our UI: store.isLoggedIn ? 'Generate' : 'Login'
        await expect(page.getByRole('button', { name: /Login/i })).toBeVisible();

        // Click button
        await page.getByRole('button', { name: /Login/i }).click();

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

        // Verify button changes to "Generate"
        await expect(page.getByRole('button', { name: /Generate/i })).toBeVisible();

        // Input code
        const inputCode = 'print("hello world")';
        await page.getByPlaceholder(/Paste your source code/i).fill(inputCode);

        // Mock API response for Generation
        await page.route(/\/api\/generate/, async route => {
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
        // The result component should appear or the text needs to be checked.
        // Assuming TestResult.vue displays the code.
        // We need to know where the result is displayed.
        // Based on previous reads, it's in TestResult component.

        // Let's look for the code content
        await expect(page.locator('code')).toContainText('def test_hello');

        // Wait for result
        // The result component should appear or the text needs to be checked.
        // Assuming TestResult.vue displays the code.
        // We need to know where the result is displayed.
        // Based on previous reads, it's in TestResult component.

        // Let's look for the code content
        await expect(page.locator('code')).toContainText('def test_hello');
    });
});
