import { test, expect } from '@playwright/test'

test.describe('Search Functionality', () => {
    test('should have search input visible', async ({ page }) => {
        await page.goto('/')
        await expect(page.getByPlaceholder(/search/i)).toBeVisible()
    })

    test('should accept text input', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('test query')
        await expect(searchInput).toHaveValue('test query')
    })

    test('should trigger search on input', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('hello')

        // Wait for debounce and network request
        await page.waitForTimeout(500)
        await page.waitForLoadState('networkidle')

        // Results area should be visible
        await expect(page.locator('main, [data-testid="results"]')).toBeVisible()
    })

    test('should clear search', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('test')
        await expect(searchInput).toHaveValue('test')

        // Clear the input
        await searchInput.clear()
        await expect(searchInput).toHaveValue('')
    })

    test('should show search results', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('conversation')

        await page.waitForTimeout(500)
        await page.waitForLoadState('networkidle')

        // Should show some content area
        await expect(page.locator('main')).toBeVisible()
    })

    test('should handle empty search gracefully', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('')
        await searchInput.press('Enter')

        // Page should still be functional
        await expect(page.locator('body')).toBeVisible()
    })

    test('should handle special characters', async ({ page }) => {
        await page.goto('/')
        const searchInput = page.getByPlaceholder(/search/i)
        await searchInput.fill('test & <script>')

        // Should handle without crashing
        await expect(searchInput).toHaveValue('test & <script>')
    })
})
