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

    test('should replace structured asset payloads with attachment and fallback blocks', async ({ page }) => {
        await page.route('**/api/conversations/conv-structured-inline', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'conv-structured-inline',
                    title: 'Structured Payload Conversation',
                    create_time: 1700000000,
                    update_time: 1700000100,
                    model: 'gpt-4',
                    message_count: 1,
                    tags: [],
                    is_favorite: false,
                    messages: [
                        {
                            id: 'msg-structured-001',
                            role: 'assistant',
                            content: [
                                'Intro paragraph before structured content.',
                                "{'content_type': 'image_asset_pointer', 'asset_pointer': 'sediment://file_001'}",
                                'Follow-up prose after image.',
                            ].join('\n'),
                            create_time: 1700000000,
                            attachments: [
                                {
                                    type: 'image',
                                    url: '/api/media/conv-structured-inline/file_001',
                                    filename: 'inline-image.png',
                                    mime_type: 'image/png',
                                    width: 400,
                                    height: 300,
                                    size_bytes: 1024,
                                    found: true,
                                },
                            ],
                            segments: [
                                {
                                    kind: 'markdown',
                                    text: 'Intro paragraph before structured content.',
                                    attachment_index: null,
                                    fallback_label: null,
                                },
                                {
                                    kind: 'attachment',
                                    text: null,
                                    attachment_index: 0,
                                    fallback_label: null,
                                },
                                {
                                    kind: 'markdown',
                                    text: 'Follow-up prose after image.',
                                    attachment_index: null,
                                    fallback_label: null,
                                },
                                {
                                    kind: 'fallback',
                                    text: "{'content_type': 'unsupported_widget', 'metadata': {'label': 'chart'}}",
                                    attachment_index: null,
                                    fallback_label: 'Unsupported content',
                                },
                            ],
                        },
                    ],
                }),
            })
        })

        await page.goto('/conversation/conv-structured-inline')
        await page.waitForLoadState('networkidle')

        await expect(page.getByText('Intro paragraph before structured content.')).toBeVisible()
        await expect(page.getByTestId('attachment-image-thumbnail-button')).toBeVisible()
        await expect(page.getByText('Follow-up prose after image.')).toBeVisible()
        await expect(page.getByText('Unsupported content')).toBeVisible()
        await expect(page.getByText(/image_asset_pointer/)).toHaveCount(0)
    })

    test('should degrade gracefully for invalid attachment segments and malformed markdown', async ({ page }) => {
        await page.route('**/api/conversations/conv-fallbacks', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'conv-fallbacks',
                    title: 'Fallback Conversation',
                    create_time: 1700000000,
                    update_time: 1700000100,
                    model: 'gpt-4',
                    message_count: 2,
                    tags: [],
                    is_favorite: false,
                    messages: [
                        {
                            id: 'msg-fallback-001',
                            role: 'assistant',
                            content: '# Heading\n```python\nprint("unterminated fence")',
                            create_time: 1700000000,
                            attachments: [],
                            segments: [
                                {
                                    kind: 'markdown',
                                    text: '# Heading\n```python\nprint("unterminated fence")',
                                    attachment_index: null,
                                    fallback_label: null,
                                },
                            ],
                        },
                        {
                            id: 'msg-fallback-002',
                            role: 'assistant',
                            content: null,
                            create_time: 1700000200,
                            attachments: [],
                            segments: [
                                {
                                    kind: 'attachment',
                                    text: null,
                                    attachment_index: 3,
                                    fallback_label: null,
                                },
                            ],
                        },
                    ],
                }),
            })
        })

        await page.goto('/conversation/conv-fallbacks')
        await page.waitForLoadState('networkidle')

        await expect(page.getByRole('heading', { name: 'Heading' })).toBeVisible()
        await expect(page.getByText(/unterminated fence/)).toBeVisible()
        await expect(page.getByText('Missing attachment')).toBeVisible()
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
        await expect(page.getByTestId('attachment-image-thumbnail-button')).toBeVisible()
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

    // Fixture: a user message exceeding 1600 characters
    const longUserPromptText =
        'I have been thinking about this problem for a while now and wanted to get your perspective. ' +
        'The situation is fairly complex: we have a distributed system with multiple services that need to ' +
        'coordinate state changes across a network partition. The challenge is that we cannot guarantee ' +
        'message delivery ordering, and at the same time we need to ensure that no two services apply ' +
        'conflicting updates simultaneously. I have read about the Raft consensus algorithm and also about ' +
        'CRDTs as potential solutions, but I am not sure which approach fits our constraints best given that ' +
        'our throughput requirements are quite high and we also need to keep latency under 50 milliseconds. ' +
        'One key concern is the operational complexity of running a Raft cluster: we would need an odd number of ' +
        'nodes to maintain quorum, and leadership elections could introduce latency spikes that violate our SLA. ' +
        'On the other hand, CRDTs are naturally commutative and do not require coordination, which appeals to us, ' +
        'but they impose constraints on the data model that might force us to redesign how we represent state. ' +
        'I am also weighing whether a hybrid approach — using CRDTs for eventual-consistency data and a lightweight ' +
        'consensus protocol only for the critical path — could give us the best of both worlds without the full ' +
        'overhead of a complete Raft implementation across every service in the mesh. ' +
        'We currently serve around twelve thousand requests per second at peak, and any solution must gracefully ' +
        'degrade under network partitions without corrupting shared state or requiring a full cluster restart. ' +
        'Could you walk me through the trade-offs so I can make an informed decision before our next architecture review?'

    test('should render a long user prompt (>1600 chars) in full', async ({ page }) => {
        await page.route('**/api/conversations/conv-long-user-prompt', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    id: 'conv-long-user-prompt',
                    title: 'Long User Prompt Conversation',
                    create_time: 1700000000,
                    update_time: 1700000100,
                    model: 'gpt-4',
                    message_count: 2,
                    tags: [],
                    is_favorite: false,
                    messages: [
                        {
                            id: 'msg-long-user-001',
                            role: 'user',
                            content: longUserPromptText,
                            create_time: 1700000000,
                            attachments: [],
                        },
                        {
                            id: 'msg-long-assistant-001',
                            role: 'assistant',
                            content: 'Great question. Let me walk through both approaches.',
                            create_time: 1700000100,
                            attachments: [],
                            segments: [
                                {
                                    kind: 'markdown',
                                    text: 'Great question. Let me walk through both approaches.',
                                    attachment_index: null,
                                    fallback_label: null,
                                },
                            ],
                        },
                    ],
                }),
            })
        })

        await page.goto('/conversation/conv-long-user-prompt')
        await page.waitForLoadState('networkidle')

        // The long user prompt should be present in the DOM
        await expect(page.getByText(/I have been thinking about this problem/)).toBeVisible()
        await expect(page.getByText(/CRDTs as potential solutions/)).toBeVisible()
        // The assistant reply should also be visible
        await expect(page.getByText('Great question. Let me walk through both approaches.')).toBeVisible()
    })
})
