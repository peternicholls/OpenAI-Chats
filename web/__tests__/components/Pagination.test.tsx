import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Pagination } from '@/components/common/Pagination'

describe('Pagination', () => {
    const mockOnPageChange = vi.fn()

    beforeEach(() => {
        mockOnPageChange.mockClear()
    })

    it('renders page numbers correctly', () => {
        render(
            <Pagination
                total={100}
                offset={0}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        expect(screen.getByText('Page 1 of 10')).toBeInTheDocument()
    })

    it('renders showing range correctly', () => {
        render(
            <Pagination
                total={100}
                offset={0}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        expect(screen.getByText('Showing 1-10 of 100')).toBeInTheDocument()
    })

    it('shows correct range for middle pages', () => {
        render(
            <Pagination
                total={100}
                offset={30}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        expect(screen.getByText('Showing 31-40 of 100')).toBeInTheDocument()
        expect(screen.getByText('Page 4 of 10')).toBeInTheDocument()
    })

    it('shows correct range for last partial page', () => {
        render(
            <Pagination
                total={95}
                offset={90}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        expect(screen.getByText('Showing 91-95 of 95')).toBeInTheDocument()
        expect(screen.getByText('Page 10 of 10')).toBeInTheDocument()
    })

    it('disables Previous button on first page', () => {
        render(
            <Pagination
                total={100}
                offset={0}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const prevButton = screen.getByRole('button', { name: /previous/i })
        expect(prevButton).toBeDisabled()
    })

    it('disables Next button on last page', () => {
        render(
            <Pagination
                total={100}
                offset={90}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const nextButton = screen.getByRole('button', { name: /next/i })
        expect(nextButton).toBeDisabled()
    })

    it('enables both buttons on middle pages', () => {
        render(
            <Pagination
                total={100}
                offset={50}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const prevButton = screen.getByRole('button', { name: /previous/i })
        const nextButton = screen.getByRole('button', { name: /next/i })
        expect(prevButton).toBeEnabled()
        expect(nextButton).toBeEnabled()
    })

    it('calls onPageChange with correct offset when clicking Next', () => {
        render(
            <Pagination
                total={100}
                offset={0}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const nextButton = screen.getByRole('button', { name: /next/i })
        fireEvent.click(nextButton)

        expect(mockOnPageChange).toHaveBeenCalledWith(10)
    })

    it('calls onPageChange with correct offset when clicking Previous', () => {
        render(
            <Pagination
                total={100}
                offset={20}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const prevButton = screen.getByRole('button', { name: /previous/i })
        fireEvent.click(prevButton)

        expect(mockOnPageChange).toHaveBeenCalledWith(10)
    })

    it('returns null when total pages is 1 or less', () => {
        const { container } = render(
            <Pagination
                total={5}
                offset={0}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        expect(container.firstChild).toBeNull()
    })

    it('does not go below 0 when clicking Previous on second page', () => {
        render(
            <Pagination
                total={100}
                offset={10}
                limit={10}
                onPageChange={mockOnPageChange}
            />
        )

        const prevButton = screen.getByRole('button', { name: /previous/i })
        fireEvent.click(prevButton)

        expect(mockOnPageChange).toHaveBeenCalledWith(0)
    })
})
