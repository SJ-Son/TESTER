import { test, expect } from '@playwright/test';

test.describe('Accessibility Checks', () => {
    test('CodeEditor should have accessible labels', async ({ page }) => {
        await page.goto('/');

        // Verify Source Code Textarea has aria-label
        const codeInput = page.getByRole('textbox', { name: 'Source code input' });
        await expect(codeInput).toBeVisible();

        // Verify Language Selection Buttons have aria-labels
        const pythonBtn = page.getByRole('button', { name: 'Select Python' });
        await expect(pythonBtn).toBeVisible();

        const jsBtn = page.getByRole('button', { name: 'Select JavaScript' });
        await expect(jsBtn).toBeVisible();

        const javaBtn = page.getByRole('button', { name: 'Select Java', exact: true });
        await expect(javaBtn).toBeVisible();

        // Verify Language Selection Buttons have aria-pressed state
        await expect(pythonBtn).toHaveAttribute('aria-pressed', 'true'); // Python is default
        await expect(jsBtn).toHaveAttribute('aria-pressed', 'false');
        await expect(javaBtn).toHaveAttribute('aria-pressed', 'false');

        // Verify clicking changes state
        await jsBtn.click();
        await expect(jsBtn).toHaveAttribute('aria-pressed', 'true');
        await expect(pythonBtn).toHaveAttribute('aria-pressed', 'false');
    });
});
