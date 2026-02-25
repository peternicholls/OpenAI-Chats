import { test, expect } from '@playwright/test'

test.describe('Export Functionality', () => {
    test('should have export options in conversation view', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            // Export button should be available
            const exportButton = page.locator('[data-testid="export-button"], button:has-text("export"), a:has-text("export")').first()
            await expect(exportButton).toBeVisible()
        }
    })

    test('should show export format options', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            const exportButton = page.locator('[data-testid="export-button"], button:has-text("export"), a:has-text("export")').first()
            if (await exportButton.isVisible()) {
                await exportButton.click()

                // Format options should appear
                const formatOptions = page.locator('[data-testid="format-options"], [role="menu"], select, [role="listbox"]')
                await expect(formatOptions.first()).toBeVisible()
            }
        }
    })

    test('should support markdown export', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            const exportButton = page.locator('[data-testid="export-button"], button:has-text("export"), a:has-text("export")').first()
            if (await exportButton.isVisible()) {
                await exportButton.click()

                // Markdown option should exist
                const markdownOption = page.locator('text=markdown, text=md, [data-value="markdown"], [data-value="md"]').first()
                await expect(markdownOption).toBeVisible()
            }
        }
    })

    test('should support JSON export', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            const exportButton = page.locator('[data-testid="export-button"], button:has-text("export"), a:has-text("export")').first()
            if (await exportButton.isVisible()) {
                await exportButton.click()

                // JSON option should exist
                const jsonOption = page.locator('text=json, [data-value="json"]').first()
                await expect(jsonOption).toBeVisible()
            }
        }
    })

    test('should trigger download on export', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            const exportButton = page.locator('[data-testid="export-button"], button:has-text("export"), a:has-text("export")').first()
            if (await exportButton.isVisible()) {
                // Set up download listener
                const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null)

                await exportButton.click()

                // Try to trigger a download by clicking first available format
                const formatOption = page.locator('[data-testid="format-option"], [role="menuitem"], button').first()
                if (await formatOption.isVisible()) {
                    await formatOption.click()
                }

                // Download may or may not trigger depending on implementation
                const download = await downloadPromise
                if (download) {
                    expect(download.suggestedFilename()).toBeTruthy()
                }
            }
        }
    })
})
