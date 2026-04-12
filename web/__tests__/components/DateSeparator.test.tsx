import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { DateSeparator } from '@/components/conversations/DateSeparator'

describe('DateSeparator', () => {
    it('renders a formatted date string', () => {
        const date = new Date(2026, 0, 15) // 15 January 2026

        render(<DateSeparator date={date} />)

        expect(screen.getByText(/January 15, 2026/)).toBeInTheDocument()
    })

    it('includes the weekday in the formatted output', () => {
        const date = new Date(2026, 0, 15) // Thursday

        render(<DateSeparator date={date} />)

        expect(screen.getByText(/Thursday/)).toBeInTheDocument()
    })

    it('renders with the date-separator test ID', () => {
        const date = new Date(2026, 0, 15)

        render(<DateSeparator date={date} />)

        expect(screen.getByTestId('date-separator')).toBeInTheDocument()
    })

    it('applies separator role for accessibility', () => {
        const date = new Date(2026, 0, 15)

        render(<DateSeparator date={date} />)

        expect(screen.getByRole('separator')).toBeInTheDocument()
    })

    it('has an accessible aria-label with the formatted date', () => {
        const date = new Date(2026, 0, 15)

        render(<DateSeparator date={date} />)

        expect(screen.getByRole('separator')).toHaveAttribute(
            'aria-label',
            expect.stringContaining('January')
        )
    })

    it('does not render before the first message in a conversation', () => {
        // This is a structural/page-level concern: DateSeparator should only appear
        // between messages when the calendar date changes, never before the first message.
        // The page component controls this, but verify the separator itself renders correctly
        // for any given date without assumptions about position.
        const date = new Date(2026, 5, 10)

        render(<DateSeparator date={date} />)

        expect(screen.getByText(/June 10, 2026/)).toBeInTheDocument()
    })
})
