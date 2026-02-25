import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDebounce } from '@/hooks/useDebounce'

describe('useDebounce', () => {
    beforeEach(() => {
        vi.useFakeTimers()
    })

    afterEach(() => {
        vi.useRealTimers()
    })

    it('should return initial value immediately', () => {
        const { result } = renderHook(() => useDebounce('initial', 500))

        expect(result.current).toBe('initial')
    })

    it('should debounce value changes', async () => {
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, 500),
            { initialProps: { value: 'initial' } }
        )

        expect(result.current).toBe('initial')

        rerender({ value: 'changed' })

        // Value should not change immediately
        expect(result.current).toBe('initial')

        // Fast-forward time
        act(() => {
            vi.advanceTimersByTime(500)
        })

        // Now it should be updated
        expect(result.current).toBe('changed')
    })

    it('should reset timer on rapid changes', () => {
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, 500),
            { initialProps: { value: 'a' } }
        )

        // Make rapid changes
        rerender({ value: 'b' })
        act(() => vi.advanceTimersByTime(200))

        rerender({ value: 'c' })
        act(() => vi.advanceTimersByTime(200))

        rerender({ value: 'd' })

        // Not enough time passed, should still be initial
        expect(result.current).toBe('a')

        // Now wait full delay
        act(() => vi.advanceTimersByTime(500))

        // Should be final value
        expect(result.current).toBe('d')
    })

    it('should use custom delay', () => {
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value, 1000),
            { initialProps: { value: 'initial' } }
        )

        rerender({ value: 'changed' })

        act(() => vi.advanceTimersByTime(500))
        expect(result.current).toBe('initial')

        act(() => vi.advanceTimersByTime(500))
        expect(result.current).toBe('changed')
    })

    it('should default to 500ms delay', () => {
        const { result, rerender } = renderHook(
            ({ value }) => useDebounce(value),
            { initialProps: { value: 'initial' } }
        )

        rerender({ value: 'changed' })

        act(() => vi.advanceTimersByTime(499))
        expect(result.current).toBe('initial')

        act(() => vi.advanceTimersByTime(1))
        expect(result.current).toBe('changed')
    })
})
