import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ThinkingBlock } from '@/components/conversations/ThinkingBlock'

describe('ThinkingBlock', () => {
    it('renders the "Reasoning" label for reasoning activity', () => {
        render(<ThinkingBlock activityType="reasoning" />)

        expect(screen.getByText('Reasoning')).toBeInTheDocument()
    })

    it('renders the "Searched the web" label for search activity', () => {
        render(<ThinkingBlock activityType="search" />)

        expect(screen.getByText('Searched the web')).toBeInTheDocument()
    })

    it('renders the "Reasoning and web search" label for both activity', () => {
        render(<ThinkingBlock activityType="both" />)

        expect(screen.getByText('Reasoning and web search')).toBeInTheDocument()
    })

    it('starts in collapsed state', () => {
        render(<ThinkingBlock activityType="reasoning" />)

        expect(screen.queryByText(/not included in the ChatGPT export/)).not.toBeInTheDocument()
    })

    it('expands to show detail text when clicked', async () => {
        const user = userEvent.setup()

        render(<ThinkingBlock activityType="reasoning" />)

        await user.click(screen.getByRole('button'))

        expect(screen.getByText(/not included in the ChatGPT export/)).toBeInTheDocument()
    })

    it('collapses again when clicked a second time', async () => {
        const user = userEvent.setup()

        render(<ThinkingBlock activityType="reasoning" />)

        const button = screen.getByRole('button')
        await user.click(button)
        expect(screen.getByText(/not included in the ChatGPT export/)).toBeInTheDocument()

        await user.click(button)
        expect(screen.queryByText(/not included in the ChatGPT export/)).not.toBeInTheDocument()
    })

    it('renders with the thinking-block test ID', () => {
        render(<ThinkingBlock activityType="reasoning" />)

        expect(screen.getByTestId('thinking-block')).toBeInTheDocument()
    })

    it('rotates the chevron icon when expanded', async () => {
        const user = userEvent.setup()

        render(<ThinkingBlock activityType="reasoning" />)

        const chevron = screen.getByRole('button').querySelector('svg')
        expect(chevron).not.toHaveClass('rotate-90')

        await user.click(screen.getByRole('button'))
        expect(chevron).toHaveClass('rotate-90')
    })
})
