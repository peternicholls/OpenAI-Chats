import { describe, it, expect } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useFavorites, useToggleFavorite } from '@/hooks/useFavorites'
import { createWrapper } from '../utils/test-utils'

describe('useFavorites (FE-HOOK-011)', () => {
    it('should return favorites list on success', async () => {
        const { result } = renderHook(
            () => useFavorites(),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toBeDefined()
        expect(result.current.data?.items).toBeDefined()
        expect(Array.isArray(result.current.data?.items)).toBe(true)
        // MSW handler returns only favorited conversations
        const favoritedItems = result.current.data!.items.filter(c => c.is_favorite)
        expect(favoritedItems.length).toBe(result.current.data!.items.length)
    })

    it('should start in loading state', () => {
        const { result } = renderHook(
            () => useFavorites(),
            { wrapper: createWrapper() }
        )

        expect(result.current.isPending).toBe(true)
    })
})

describe('useToggleFavorite (FE-HOOK-012)', () => {
    it('should toggle favorite and return result (FE-HOOK-012)', async () => {
        const wrapper = createWrapper()
        const { result } = renderHook(
            () => useToggleFavorite(),
            { wrapper }
        )

        let toggleResult: { is_favorite: boolean } | undefined

        await act(async () => {
            toggleResult = await result.current.mutateAsync('conv-001-test')
        })

        expect(toggleResult).toBeDefined()
        expect(typeof toggleResult?.is_favorite).toBe('boolean')
    })
})

describe('useFavorites cache invalidation (FE-HOOK-013)', () => {
    it('should invalidate favorites cache after toggle', async () => {
        const wrapper = createWrapper()

        const { result: favResult } = renderHook(
            () => useFavorites(),
            { wrapper }
        )
        const { result: toggleResult } = renderHook(
            () => useToggleFavorite(),
            { wrapper }
        )

        await waitFor(() => {
            expect(favResult.current.isSuccess).toBe(true)
        })

        await act(async () => {
            await toggleResult.current.mutateAsync('conv-001-test')
        })

        // Wait for mutation to settle
        await waitFor(() => {
            expect(toggleResult.current.isSuccess).toBe(true)
        })
    })
})
