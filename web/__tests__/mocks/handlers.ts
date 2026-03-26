import { http, HttpResponse } from 'msw'

const API_URL = 'http://localhost:8000'

export const markdownMessageText = [
    '# Release Notes',
    '',
    '- Added **formatted** transcript rendering',
    '- Supports [links](https://example.com) and `inline code`',
    '',
    '> Blockquotes remain readable',
    '',
    '```python',
    "print('hello')",
    '```',
].join('\n')

export function buildRenderSegment(
    kind: 'markdown' | 'attachment' | 'fallback',
    overrides: Partial<{
        text: string | null
        attachment_index: number | null
        fallback_label: string | null
    }> = {}
) {
    return {
        kind,
        text: kind === 'attachment' ? null : '',
        attachment_index: kind === 'attachment' ? 0 : null,
        fallback_label: kind === 'fallback' ? 'Unsupported content' : null,
        ...overrides,
    }
}

export function buildMockMessage(
    overrides: Partial<{
        id: string
        role: 'user' | 'assistant' | 'system' | 'tool'
        content: string | null
        create_time: number | null
        attachments: Array<{
            type: 'image' | 'audio' | 'file'
            url: string
            filename: string
            mime_type: string | null
            width: number | null
            height: number | null
            size_bytes: number | null
            found: boolean
        }>
        segments: Array<ReturnType<typeof buildRenderSegment>>
    }> = {}
) {
    return {
        id: 'msg-001',
        role: 'assistant' as const,
        content: markdownMessageText,
        create_time: 1700000000,
        attachments: [],
        segments: [
            buildRenderSegment('markdown', { text: markdownMessageText, attachment_index: null }),
        ],
        ...overrides,
    }
}

export const mixedStructuredPayloadMessage = buildMockMessage({
    id: 'msg-mixed-structured',
    content: [
        'Intro paragraph before structured content.',
        '[[ATTACHMENT:0]]',
        'Follow-up prose after image.',
        '[[ATTACHMENT:1]]',
        'Trailing prose after audio.',
        "{'content_type': 'unsupported_widget', 'metadata': {'label': 'chart', 'version': 1}}",
    ].join('\n'),
    attachments: [
        {
            type: 'image',
            url: '/api/media/conv-001-test/file_001',
            filename: 'sample.png',
            mime_type: 'image/png',
            width: 512,
            height: 512,
            size_bytes: 2048,
            found: true,
        },
        {
            type: 'audio',
            url: '/api/media/conv-001-test/audio_001',
            filename: 'sample.wav',
            mime_type: 'audio/wav',
            width: null,
            height: null,
            size_bytes: 1024,
            found: true,
        },
    ],
    segments: [
        buildRenderSegment('markdown', { text: 'Intro paragraph before structured content.', attachment_index: null }),
        buildRenderSegment('attachment', { text: null, attachment_index: 0 }),
        buildRenderSegment('markdown', { text: 'Follow-up prose after image.', attachment_index: null }),
        buildRenderSegment('attachment', { text: null, attachment_index: 1 }),
        buildRenderSegment('markdown', { text: 'Trailing prose after audio.', attachment_index: null }),
        buildRenderSegment('fallback', {
            text: "{'content_type': 'unsupported_widget', 'metadata': {'label': 'chart', 'version': 1}}",
            fallback_label: 'Unsupported content',
            attachment_index: null,
        }),
    ],
})

// Sample test data
export const mockConversations = [
    {
        id: 'conv-001-test',
        title: 'Test Conversation 1',
        create_time: 1700000000,
        update_time: 1700001000,
        message_count: 2,
        model: 'gpt-4',
        tags: [],
        is_favorite: false,
    },
    {
        id: 'conv-002-test',
        title: 'Test Conversation 2',
        create_time: 1700100000,
        update_time: 1700101000,
        message_count: 3,
        model: 'gpt-4',
        tags: ['work'],
        is_favorite: true,
    },
]

export const mockConversationDetail = {
    id: 'conv-001-test',
    title: 'Test Conversation 1',
    create_time: 1700000000,
    update_time: 1700001000,
    message_count: 2,
    model: 'gpt-4',
    tags: [],
    is_favorite: false,
    messages: [
        {
            id: 'msg-001',
            role: 'user',
            content: 'Hello, how are you?',
            create_time: 1700000000,
            attachments: [],
        },
        {
            id: 'msg-002',
            role: 'assistant',
            content: 'I am doing well, thank you for asking!\n[[ATTACHMENT:0]]',
            create_time: 1700000100,
            attachments: [
                {
                    type: 'image',
                    url: '/api/media/conv-001-test/file_001',
                    filename: 'sample.png',
                    mime_type: 'image/png',
                    width: 512,
                    height: 512,
                    size_bytes: 2048,
                    found: true,
                },
            ],
            segments: [
                buildRenderSegment('markdown', {
                    text: 'I am doing well, thank you for asking!',
                    attachment_index: null,
                }),
                buildRenderSegment('attachment', { text: null, attachment_index: 0 }),
            ],
        },
    ],
}

export const mockSearchResults = [
    {
        conversation_id: 'conv-001-test',
        title: 'Test Conversation 1',
        create_time: 1700000000,
        match_count: 1,
        preview: 'Hello, how are you?',
        relevance_score: 0.95,
    },
]

export const mockTags = [
    { name: 'work', count: 5 },
    { name: 'personal', count: 3 },
]

export const handlers = [
    // Health check
    http.get(`${API_URL}/api/health`, () => {
        return HttpResponse.json({ status: 'ok', database: 'connected' })
    }),

    // List conversations
    http.get(`${API_URL}/api/conversations`, ({ request }) => {
        const url = new URL(request.url)
        const limit = parseInt(url.searchParams.get('limit') || '50', 10)
        const offset = parseInt(url.searchParams.get('offset') || '0', 10)

        const items = mockConversations.slice(offset, offset + limit)
        return HttpResponse.json({
            total: mockConversations.length,
            offset,
            limit,
            items,
        })
    }),

    // Get conversation by ID
    http.get(`${API_URL}/api/conversations/:id`, ({ params }) => {
        const { id } = params
        if (id === 'conv-001-test') {
            return HttpResponse.json(mockConversationDetail)
        }
        return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    }),

    // Search
    http.post(`${API_URL}/api/search`, async ({ request }) => {
        const body = await request.json() as { query?: string }
        if (!body.query) {
            return HttpResponse.json({ detail: 'Query required' }, { status: 422 })
        }
        return HttpResponse.json({
            total: mockSearchResults.length,
            offset: 0,
            limit: 20,
            items: mockSearchResults,
        })
    }),

    // List tags
    http.get(`${API_URL}/api/tags`, () => {
        return HttpResponse.json(mockTags)
    }),

    // Get conversation tags
    http.get(`${API_URL}/api/conversations/:id/tags`, () => {
        return HttpResponse.json(['work', 'important'])
    }),

    // Add tag
    http.post(`${API_URL}/api/conversations/:id/tags`, () => {
        return new HttpResponse(null, { status: 204 })
    }),

    // Remove tag
    http.delete(`${API_URL}/api/conversations/:id/tags/:tagName`, () => {
        return new HttpResponse(null, { status: 204 })
    }),

    // Toggle favorite
    http.post(`${API_URL}/api/conversations/:id/favorite`, () => {
        return HttpResponse.json({ is_favorite: true })
    }),

    // List favorites
    http.get(`${API_URL}/api/favorites`, () => {
        const favorites = mockConversations.filter(c => c.is_favorite)
        return HttpResponse.json({
            total: favorites.length,
            offset: 0,
            limit: 50,
            items: favorites,
        })
    }),

    // Import progress
    http.get(`${API_URL}/api/import/progress`, () => {
        return HttpResponse.json({
            status: 'idle',
            current: 0,
            total: 0,
            percent: 0,
            message: null,
        })
    }),

    // Import archive
    http.post(`${API_URL}/api/import`, () => {
        return HttpResponse.json({
            status: 'processing',
            current: 0,
            total: 0,
            percent: 0,
            message: 'Starting import...',
        }, { status: 202 })
    }),

    // Export conversation
    http.get(`${API_URL}/api/conversations/:id/export`, ({ request }) => {
        const url = new URL(request.url)
        const format = url.searchParams.get('format')

        const content = format === 'json'
            ? JSON.stringify(mockConversationDetail)
            : '# Test Conversation\n\nContent here'

        return new HttpResponse(content, {
            headers: {
                'Content-Type': format === 'json' ? 'application/json' : 'text/markdown',
                'Content-Disposition': `attachment; filename="conversation.${format}"`,
            },
        })
    }),

    // Settings
    http.get(`${API_URL}/api/settings`, () => {
        return HttpResponse.json({
            theme: 'system',
            default_export_format: 'md',
            sidebar_open: true,
            embedding_model: 'text-embedding-3-small',
            items_per_page: 50,
            openai_api_key: '',
            archive_media_dir: '/tmp/archive',
        })
    }),

    http.put(`${API_URL}/api/settings`, async ({ request }) => {
        const body = await request.json() as Record<string, unknown>
        return HttpResponse.json({
            theme: 'system',
            default_export_format: 'md',
            sidebar_open: true,
            embedding_model: 'text-embedding-3-small',
            items_per_page: 50,
            openai_api_key: '',
            archive_media_dir: '/tmp/archive',
            ...body,
        })
    }),
]
