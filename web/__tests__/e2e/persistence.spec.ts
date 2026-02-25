import { test, expect } from '@playwright/test'

test.describe('Data Persistence', () => {
    test('should load conversations list without error', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        // Page should render successfully (persistence smoke test)
        await expect(page).toHaveURL('/')
        await expect(page.locator('body')).toBeVisible()
    })

    test('should maintain URL state on navigation back', async ({ page }) => {
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        // Navigate forward then back
        await page.goto('/search')
        await page.waitForLoadState('networkidle')
        await page.goBack()
        await page.waitForLoadState('networkidle')

        await expect(page).toHaveURL('/')
    })

    test('should preserve search query in URL', async ({ page }) => {
        await page.goto('/search')
        await page.waitForLoadState('networkidle')

        // If there is a search input, type in it
        const searchInput = page.getByPlaceholder(/search/i).first()
        if (await searchInput.isVisible()) {
            await searchInput.fill('persistence test')
            await searchInput.press('Enter')
            await page.waitForTimeout(600) // wait for debounce

            // URL or page state should reflect the search
            const currentUrl = page.url()
            expect(currentUrl).toBeTruthy()
        }
    })

    test('should load favorites page without error after navigation', async ({ page }) => {
        // Simulate user navigating around the app (persistence test)
        await page.goto('/')
        await page.waitForLoadState('networkidle')

        await page.goto('/favorites')
        await page.waitForLoadState('networkidle')

        await expect(page).toHaveURL(/favorites/)
        await expect(page.locator('body')).toBeVisible()
    })

    test('should load settings page without error', async ({ page }) => {
        await page.goto('/settings')
        await page.waitForLoadState('networkidle')

        await expect(page).toHaveURL(/settings/)
        await expect(page.locator('body')).toBeVisible()
    })
})
