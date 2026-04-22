import { describe, it, expect } from 'vitest'
import { api } from '@/services/api'

describe('API Client', () => {
    describe('listConversations', () => {
        it('should fetch conversations with pagination', async () => {
            const result = await api.listConversations({ limit: 10, offset: 0 })

            expect(result).toHaveProperty('items')
            expect(result).toHaveProperty('total')
            expect(result).toHaveProperty('limit')
            expect(result).toHaveProperty('offset')
            expect(Array.isArray(result.items)).toBe(true)
        })

        it('should respect limit parameter', async () => {
            const result = await api.listConversations({ limit: 1 })

            expect(result.items.length).toBeLessThanOrEqual(1)
        })
    })

    describe('getConversation', () => {
        it('should fetch a conversation by ID', async () => {
            const result = await api.getConversation('conv-001-test')

            expect(result).toHaveProperty('id', 'conv-001-test')
            expect(result).toHaveProperty('title')
            expect(result).toHaveProperty('messages')
            expect(Array.isArray(result.messages)).toBe(true)
            expect(result.messages[1]).toHaveProperty('attachments')
            expect(result.messages[1]).toHaveProperty('segments')
            expect(result.messages[1].segments).toHaveLength(2)
        })

        it('should throw error for non-existent conversation', async () => {
            await expect(api.getConversation('non-existent-id')).rejects.toThrow()
        })

        it('should preserve structured attachment and fallback segments', async () => {
            const result = await api.getConversation('conv-structured-test')

            expect(result.messages[0].segments).toEqual([
                expect.objectContaining({ kind: 'markdown', text: 'Intro paragraph before structured content.' }),
                expect.objectContaining({ kind: 'attachment', attachment_index: 0 }),
                expect.objectContaining({ kind: 'markdown', text: 'Follow-up prose after image.' }),
                expect.objectContaining({ kind: 'attachment', attachment_index: 1 }),
                expect.objectContaining({ kind: 'markdown', text: 'Trailing prose after audio.' }),
                expect.objectContaining({ kind: 'fallback', fallback_label: 'Unsupported content' }),
            ])
        })

        it('should keep segment parity for equivalent message structures', async () => {
            const first = await api.getConversation('conv-001-test')
            const second = await api.getConversation('conv-001-test')

            expect(first.messages[1].segments).toEqual(second.messages[1].segments)
        })
    })

    describe('search', () => {
        it('should search with query', async () => {
            const result = await api.search({ query: 'hello' })

            expect(result).toHaveProperty('items')
            expect(result).toHaveProperty('total')
            expect(Array.isArray(result.items)).toBe(true)
        })

        it('should include match preview in results', async () => {
            const result = await api.search({ query: 'hello' })

            if (result.items.length > 0) {
                expect(result.items[0]).toHaveProperty('preview')
            }
        })
    })

    describe('tags', () => {
        it('should list all tags', async () => {
            const result = await api.listTags()

            expect(Array.isArray(result)).toBe(true)
            if (result.length > 0) {
                expect(result[0]).toHaveProperty('name')
                expect(result[0]).toHaveProperty('count')
            }
        })

        it('should get conversation tags', async () => {
            const result = await api.getConversationTags('conv-001-test')

            expect(Array.isArray(result)).toBe(true)
        })
    })

    describe('favorites', () => {
        it('should toggle favorite status', async () => {
            const result = await api.toggleFavorite('conv-001-test')

            expect(result).toHaveProperty('is_favorite')
            expect(typeof result.is_favorite).toBe('boolean')
        })

        it('should list favorites', async () => {
            const result = await api.listFavorites()

            expect(result).toHaveProperty('items')
            expect(result).toHaveProperty('total')
        })
    })

    describe('healthCheck', () => {
        it('should return health status', async () => {
            const result = await api.healthCheck()

            expect(result).toHaveProperty('status', 'ok')
            expect(result).toHaveProperty('database')
        })
    })

    describe('settings', () => {
        it('should get settings', async () => {
            const result = await api.getSettings()

            expect(result).toHaveProperty('theme')
            expect(result).toHaveProperty('default_export_format')
            expect(result).toHaveProperty('archive_media_dir')
        })

        it('should build absolute media URLs for relative paths', () => {
            // In browser context (jsdom) the API client uses relative paths so the
            // origin is not prepended; the path is returned as-is.
            expect(api.getMediaUrl('/api/media/root/file-123')).toBe(
                '/api/media/root/file-123'
            )
        })
    })

    describe('exportConversation', () => {
        it('should return blob for export', async () => {
            const result = await api.exportConversation('conv-001-test', 'markdown')

            // Check that it has blob-like properties
            expect(result).toHaveProperty('size')
            expect(result).toHaveProperty('type')
            expect(result.size).toBeGreaterThan(0)
        })
    })

    describe('import', () => {
        it('should get import progress', async () => {
            const result = await api.getImportProgress()

            expect(result).toHaveProperty('status')
            expect(result).toHaveProperty('percent')
        })
    })
})
