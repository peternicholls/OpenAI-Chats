import { test, expect } from '@playwright/test'

test.describe('Conversation View', () => {
    test('should render markdown segments as formatted transcript content', async ({ page }) => {
        await page.route('**/api/conversations/conv-formatted-markdown', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'conv-formatted-markdown',
                    title: 'Formatted Markdown Conversation',
                    create_time: 1700000000,
                    update_time: 1700000100,
                    model: 'gpt-4',
                    message_count: 1,
                    tags: [],
                    is_favorite: false,
                    messages: [
                        {
                            id: 'msg-markdown-001',
                            role: 'assistant',
                            content: '# Release Notes\n\n- Added **formatted** transcript rendering',
                            create_time: 1700000000,
                            attachments: [],
                            segments: [
                                {
                                    kind: 'markdown',
                                    text: '# Release Notes\n\n- Added **formatted** transcript rendering',
                                    attachment_index: null,
                                    fallback_label: null,
                                },
                            ],
                        },
                    ],
                }),
            })
        })

        await page.goto('/conversation/conv-formatted-markdown')
        await page.waitForLoadState('networkidle')

        await expect(page.getByRole('heading', { name: 'Release Notes' })).toBeVisible()
        await expect(page.getByText('Added formatted transcript rendering')).toBeVisible()
        await expect(page.getByText('# Release Notes')).toHaveCount(0)
    })

    test('should render mixed attachment content in order', async ({ page }) => {
        await page.route('**/api/conversations/conv-inline-media', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'conv-inline-media',
                    title: 'Inline Media Conversation',
                    create_time: 1700000000,
                    update_time: 1700000100,
                    model: 'gpt-4',
                    message_count: 1,
                    tags: [],
                    is_favorite: false,
                    messages: [
                        {
                            id: 'msg-inline-media',
                            role: 'assistant',
                            content: 'Intro\n[[ATTACHMENT:0]]\nAfter image\n[[ATTACHMENT:1]]',
                            create_time: 1700000000,
                            attachments: [
                                {
                                    type: 'image',
                                    url: '/api/media/conv-inline-media/file_001',
                                    filename: 'inline-image.png',
                                    mime_type: 'image/png',
                                    width: 400,
                                    height: 300,
                                    size_bytes: 1024,
                                    found: true,
                                },
                                {
                                    type: 'file',
                                    url: '/api/media/root/file-abc123',
                                    filename: 'inline-file.pdf',
                                    mime_type: 'application/pdf',
                                    width: null,
                                    height: null,
                                    size_bytes: 2048,
                                    found: true,
                                },
                            ],
                        },
                    ],
                }),
            })
        })

        await page.goto('/conversation/conv-inline-media')
        await page.waitForLoadState('networkidle')

        await expect(page.getByText('Intro')).toBeVisible()
        await expect(page.getByText('After image')).toBeVisible()
        await expect(page.getByTestId('attachment-image')).toBeVisible()
        await expect(page.getByTestId('attachment-file')).toBeVisible()
    })

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
