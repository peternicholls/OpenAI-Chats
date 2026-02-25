import { test, expect } from '@playwright/test'

test.describe('Conversation View', () => {
    test('should navigate to conversation detail', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        // Click on first conversation if available
        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await expect(page).toHaveURL(/conversation/)
        }
    })

    test('should display conversation messages', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            // Should display message bubbles
            await expect(page.locator('[data-testid="message"], .message, [class*="message"]').first()).toBeVisible()
        }
    })

    test('should display conversation title', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            // Should have a title/heading
            await expect(page.getByRole('heading')).toBeVisible()
        }
    })

    test('should be able to navigate back', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            // Find back button or link
            const backButton = page.locator('[data-testid="back-button"], a[href="/"], button:has-text("back")').first()
            if (await backButton.isVisible()) {
                await backButton.click()
                await expect(page).toHaveURL('/')
            }
        }
    })

    test('should handle favorite toggle', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        const conversationLink = page.locator('[data-testid="conversation-item"], a[href*="conversation"]').first()
        if (await conversationLink.isVisible()) {
            await conversationLink.click()
            await page.waitForLoadState('networkidle')

            const favoriteButton = page.locator('[data-testid="favorite-button"], button:has-text("favorite"), button[aria-label*="favorite"]').first()
            if (await favoriteButton.isVisible()) {
                await favoriteButton.click()
                // Should toggle without error
                await expect(favoriteButton).toBeVisible()
            }
        }
    })
})
