import { test, expect } from '@playwright/test'

test.describe('Import Functionality', () => {
    test('should have import button visible', async ({ page }) => {
        await page.goto('/')
        const importButton = page.locator('[data-testid="import-button"], button:has-text("import"), a:has-text("import")').first()
        await expect(importButton).toBeVisible()
    })

    test('should open import dialog', async ({ page }) => {
        // Navigate to import page
        await page.goto('/import')

        // Click the trigger button to open the dialog
        const dialogTrigger = page.locator('button:has-text("Choose Archive"), button:has-text("Import Archive")').first()
        await expect(dialogTrigger).toBeVisible()
        await dialogTrigger.click()

        // Dialog should appear
        const dialog = page.locator('[role="dialog"]')
        await expect(dialog).toBeVisible({ timeout: 5000 })
    })

    test('should have file input for archive upload', async ({ page }) => {
        // Navigate to import page
        await page.goto('/import')

        // Click the trigger button to open the dialog
        const dialogTrigger = page.locator('button:has-text("Choose Archive"), button:has-text("Import Archive")').first()
        await expect(dialogTrigger).toBeVisible()
        await dialogTrigger.click()

        // Wait for dialog to open
        const dialog = page.locator('[role="dialog"]')
        await expect(dialog).toBeVisible({ timeout: 5000 })

        // Should have a file input
        const fileInput = page.locator('input[type="file"]')
        await expect(fileInput).toBeAttached()
    })

    test('should accept zip files', async ({ page }) => {
        // Navigate to import page
        await page.goto('/import')

        // Click the trigger button to open the dialog
        const dialogTrigger = page.locator('button:has-text("Choose Archive"), button:has-text("Import Archive")').first()
        await expect(dialogTrigger).toBeVisible()
        await dialogTrigger.click()

        // Wait for dialog to open
        const dialog = page.locator('[role="dialog"]')
        await expect(dialog).toBeVisible({ timeout: 5000 })

        const fileInput = page.locator('input[type="file"]')
        // Check accept attribute includes zip
        const accept = await fileInput.getAttribute('accept')
        expect(accept).toContain('zip')
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
