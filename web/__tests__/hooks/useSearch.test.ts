import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useSearch } from '@/hooks/useSearch'
import { createWrapper } from '../utils/test-utils'

describe('useSearch', () => {
    it('should not fetch when query is empty', () => {
        const { result } = renderHook(
            () => useSearch({ query: '' }),
            { wrapper: createWrapper() }
        )

        expect(result.current.isLoading).toBe(false)
        expect(result.current.isFetching).toBe(false)
        expect(result.current.data).toBeUndefined()
    })

    it('should not fetch when enabled is false', () => {
        const { result } = renderHook(
            () => useSearch({ query: 'test', enabled: false }),
            { wrapper: createWrapper() }
        )

        expect(result.current.isLoading).toBe(false)
        expect(result.current.data).toBeUndefined()
    })

    it('should fetch when query is provided and enabled', async () => {
        const { result } = renderHook(
            () => useSearch({ query: 'hello' }),
            { wrapper: createWrapper() }
        )

        // Initial state is loading
        expect(result.current.isLoading).toBe(true)

        // Wait for the query to complete
        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        // Should have data
        expect(result.current.data).toBeDefined()
        expect(result.current.data?.items).toBeDefined()
    })

    it('should include search type in query', async () => {
        const { result } = renderHook(
            () => useSearch({ query: 'test', searchType: 'keyword' }),
            { wrapper: createWrapper() }
        )

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false)
        })

        expect(result.current.data).toBeDefined()
    })
})
