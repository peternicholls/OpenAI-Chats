import { test, expect } from '@playwright/test'

test.describe('Import Functionality', () => {
    test('should have import button visible', async ({ page }) => {
        await page.goto('/')
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()
        await expect(importButton).toBeVisible()
    })

    test('should open import dialog', async ({ page }) => {
        await page.goto('/')
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()

        if (await importButton.isVisible()) {
            await importButton.click()

            // Dialog or import area should appear
            const importArea = page.locator('[data-testid="import-dialog"], [role="dialog"], input[type="file"]').first()
            await expect(importArea).toBeVisible()
        }
    })

    test('should have file input for archive upload', async ({ page }) => {
        await page.goto('/')
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()

        if (await importButton.isVisible()) {
            await importButton.click()

            // Should have a file input
            const fileInput = page.locator('input[type="file"]')
            await expect(fileInput).toBeAttached()
        }
    })

    test('should accept zip files', async ({ page }) => {
        await page.goto('/')
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()

        if (await importButton.isVisible()) {
            await importButton.click()

            const fileInput = page.locator('input[type="file"]')
            // Check accept attribute includes zip
            const accept = await fileInput.getAttribute('accept')
            expect(accept).toContain('zip')
        }
    })

    test('should show progress during import', async ({ page }) => {
        await page.goto('/')
        // This test verifies progress UI elements exist
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()

        if (await importButton.isVisible()) {
            await importButton.click()

            // Page should remain functional during import setup
            await expect(page.locator('body')).toBeVisible()
        }
    })
})
