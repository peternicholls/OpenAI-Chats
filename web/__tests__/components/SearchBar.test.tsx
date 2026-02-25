import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { SearchBar } from '@/components/search/SearchBar'

describe('SearchBar', () => {
    beforeEach(() => {
        vi.useFakeTimers()
    })

    afterEach(() => {
        vi.useRealTimers()
    })

    it('renders search input', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        expect(screen.getByRole('textbox')).toBeInTheDocument()
        expect(screen.getByPlaceholderText(/search conversations/i)).toBeInTheDocument()
    })

    it('has correct aria-label', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        expect(screen.getByLabelText('Search')).toBeInTheDocument()
    })

    it('debounces search calls', async () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} debounceMs={500} />)

        const input = screen.getByRole('textbox')

        // Type a search query
        fireEvent.change(input, { target: { value: 'test query' } })

        // Immediate call should happen for empty initial value
        expect(onSearch).toHaveBeenCalledTimes(1)
        expect(onSearch).toHaveBeenLastCalledWith('')

        // Fast-forward 250ms (not enough)
        act(() => {
            vi.advanceTimersByTime(250)
        })

        // Still only called once
        expect(onSearch).toHaveBeenCalledTimes(1)

        // Fast-forward another 250ms (total 500ms)
        act(() => {
            vi.advanceTimersByTime(250)
        })

        // Now should be called with the query
        expect(onSearch).toHaveBeenCalledTimes(2)
        expect(onSearch).toHaveBeenLastCalledWith('test query')
    })

    it('trims whitespace from query', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} debounceMs={100} />)

        const input = screen.getByRole('textbox')
        fireEvent.change(input, { target: { value: '  hello  ' } })

        act(() => {
            vi.advanceTimersByTime(100)
        })

        expect(onSearch).toHaveBeenLastCalledWith('hello')
    })

    it('shows clear button when input has value', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        const input = screen.getByRole('textbox')

        // Initially no clear button
        expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument()

        // Type something
        fireEvent.change(input, { target: { value: 'test' } })

        // Clear button should appear
        expect(screen.getByLabelText('Clear search')).toBeInTheDocument()
    })

    it('clears input when clear button clicked', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        const input = screen.getByRole('textbox')
        fireEvent.change(input, { target: { value: 'test' } })

        const clearButton = screen.getByLabelText('Clear search')
        fireEvent.click(clearButton)

        expect(input).toHaveValue('')
    })

    it('clears input when Escape key pressed', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        const input = screen.getByRole('textbox')
        fireEvent.change(input, { target: { value: 'test' } })
        expect(input).toHaveValue('test')

        fireEvent.keyDown(input, { key: 'Escape' })

        expect(input).toHaveValue('')
    })

    it('shows loading spinner when isLoading is true', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} isLoading={true} />)

        // The loader has animate-spin class
        const loader = document.querySelector('.animate-spin')
        expect(loader).toBeInTheDocument()
    })

    it('hides clear button when loading', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} isLoading={true} />)

        const input = screen.getByRole('textbox')
        fireEvent.change(input, { target: { value: 'test' } })

        // Clear button should not be visible while loading
        expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument()
    })

    it('uses custom placeholder', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} placeholder="Custom placeholder" />)

        expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument()
    })

    it('uses initial value', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} initialValue="initial query" />)

        expect(screen.getByRole('textbox')).toHaveValue('initial query')
    })

    it('updates when initialValue prop changes', () => {
        const onSearch = vi.fn()
        const { rerender } = render(<SearchBar onSearch={onSearch} initialValue="first" />)

        expect(screen.getByRole('textbox')).toHaveValue('first')

        rerender(<SearchBar onSearch={onSearch} initialValue="second" />)

        expect(screen.getByRole('textbox')).toHaveValue('second')
    })
})
