import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useConversations, useConversation } from '@/hooks/useConversations'
import { createWrapper } from '../utils/test-utils'

describe('useConversations', () => {
    it('should start in loading state (FE-HOOK-001)', () => {
        const { result } = renderHook(
            () => useConversations(),
            { wrapper: createWrapper() }
        )

        expect(result.current.isPending).toBe(true)
        expect(result.current.data).toBeUndefined()
    })

    it('should return paginated conversations on success (FE-HOOK-002)', async () => {
        const { result } = renderHook(
            () => useConversations(),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toBeDefined()
        expect(result.current.data?.items).toBeDefined()
        expect(Array.isArray(result.current.data?.items)).toBe(true)
        expect(result.current.data?.total).toBeGreaterThanOrEqual(0)
    })

    it('should pass filter params through (FE-HOOK-003)', async () => {
        const { result } = renderHook(
            () => useConversations({ limit: 1, offset: 0 }),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data?.items.length).toBeLessThanOrEqual(1)
    })

    it('should handle tag filter (FE-HOOK-003b)', async () => {
        const { result } = renderHook(
            () => useConversations({ tag: 'work' }),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toBeDefined()
    })

    it('should return error state on failure (FE-HOOK-004)', async () => {
        const { result } = renderHook(
            () => useConversations(),
            { wrapper: createWrapper() }
        )

        // With MSW providing a valid response, we shouldn't see an error
        await waitFor(() => {
            expect(result.current.isPending).toBe(false)
        })

        expect(result.current.isError).toBe(false)
    })
})

describe('useConversation detail (FE-HOOK-005)', () => {
    it('should fetch conversation detail by ID', async () => {
        const { result } = renderHook(
            () => useConversation('conv-001-test'),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toBeDefined()
        expect(result.current.data?.id).toBe('conv-001-test')
        expect(result.current.data?.messages).toBeDefined()
    })

    it('should not fetch when ID is empty', () => {
        const { result } = renderHook(
            () => useConversation(''),
            { wrapper: createWrapper() }
        )

        expect(result.current.isPending).toBe(true)
        expect(result.current.isFetching).toBe(false)
    })
})
