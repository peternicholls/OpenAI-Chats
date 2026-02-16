import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
    test('should display the main heading', async ({ page }) => {
        await page.goto('/')
        await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    })

    test('should display navigation elements', async ({ page }) => {
        await page.goto('/')
        await expect(page.locator('nav')).toBeVisible()
    })

    test('should display search functionality', async ({ page }) => {
        await page.goto('/')
        await expect(page.getByPlaceholder(/search/i)).toBeVisible()
    })

    test('should display conversation list', async ({ page }) => {
        await page.goto('/')
        // Wait for conversations to load
        await page.waitForLoadState('networkidle')
        // Should have a list area for conversations
        await expect(page.locator('[data-testid="conversation-list"], main')).toBeVisible()
    })

    test('should be responsive on mobile', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 })
        await page.goto('/')
        await expect(page.locator('body')).toBeVisible()
        // Content should still be visible
        await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    })
})
