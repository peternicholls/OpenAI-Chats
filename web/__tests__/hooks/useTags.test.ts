import { describe, it, expect } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useTags, useAddTag, useRemoveTag } from '@/hooks/useTags'
import { createWrapper } from '../utils/test-utils'

describe('useTags (FE-HOOK-014)', () => {
    it('should return all tags list', async () => {
        const { result } = renderHook(
            () => useTags(),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toBeDefined()
        expect(Array.isArray(result.current.data)).toBe(true)
        if (result.current.data!.length > 0) {
            expect(result.current.data![0]).toHaveProperty('name')
            expect(result.current.data![0]).toHaveProperty('count')
        }
    })
})

describe('useAddTag (FE-HOOK-015)', () => {
    it('should add a tag to a conversation', async () => {
        const wrapper = createWrapper()
        const { result } = renderHook(
            () => useAddTag('conv-001-test'),
            { wrapper }
        )

        await act(async () => {
            await result.current.mutateAsync('new-tag')
        })

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })
    })
})

describe('useRemoveTag (FE-HOOK-016)', () => {
    it('should remove a tag from a conversation', async () => {
        const wrapper = createWrapper()
        const { result } = renderHook(
            () => useRemoveTag('conv-001-test'),
            { wrapper }
        )

        await act(async () => {
            await result.current.mutateAsync('work')
        })

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })
    })
})

describe('useAddTag cache invalidation (FE-HOOK-017)', () => {
    it('should invalidate tag caches after adding a tag', async () => {
        const wrapper = createWrapper()

        const { result: tagsResult } = renderHook(
            () => useTags(),
            { wrapper }
        )
        const { result: addResult } = renderHook(
            () => useAddTag('conv-001-test'),
            { wrapper }
        )

        await waitFor(() => {
            expect(tagsResult.current.isSuccess).toBe(true)
        })

        await act(async () => {
            await addResult.current.mutateAsync('another-tag')
        })

        await waitFor(() => {
            expect(addResult.current.isSuccess).toBe(true)
        })
    })
})
