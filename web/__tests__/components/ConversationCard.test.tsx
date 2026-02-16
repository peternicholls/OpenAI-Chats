import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConversationCard } from '@/components/conversations/ConversationCard'
import type { Conversation } from '@/types'

// Mock Next.js Link component
vi.mock('next/link', () => ({
    default: ({ children, href }: { children: React.ReactNode; href: string }) => (
        <a href={href}>{children}</a>
    ),
}))

const mockConversation: Conversation = {
    id: 'test-conv-1',
    title: 'Test Conversation Title',
    create_time: 1700000000, // November 14, 2023
    update_time: 1700001000,
    message_count: 5,
    model: 'gpt-4',
    tags: [],
    is_favorite: false,
}

describe('ConversationCard', () => {
    it('renders conversation title', () => {
        render(<ConversationCard conversation={mockConversation} />)

        expect(screen.getByText('Test Conversation Title')).toBeInTheDocument()
    })

    it('renders message count', () => {
        render(<ConversationCard conversation={mockConversation} />)

        expect(screen.getByText(/5 messages/)).toBeInTheDocument()
    })

    it('renders model name when present', () => {
        render(<ConversationCard conversation={mockConversation} />)

        expect(screen.getByText(/gpt-4/)).toBeInTheDocument()
    })

    it('renders "[Untitled]" when title is missing', () => {
        const untitledConv: Conversation = {
            ...mockConversation,
            title: '',
        }
        render(<ConversationCard conversation={untitledConv} />)

        expect(screen.getByText('[Untitled]')).toBeInTheDocument()
    })

    it('shows favorite star when is_favorite is true', () => {
        const favoriteConv: Conversation = {
            ...mockConversation,
            is_favorite: true,
        }
        render(<ConversationCard conversation={favoriteConv} />)

        // Star icon should be present (SVG)
        const star = document.querySelector('svg')
        expect(star).toBeInTheDocument()
    })

    it('renders tags when present', () => {
        const taggedConv: Conversation = {
            ...mockConversation,
            tags: ['work', 'important'],
        }
        render(<ConversationCard conversation={taggedConv} />)

        expect(screen.getByText('work')).toBeInTheDocument()
        expect(screen.getByText('important')).toBeInTheDocument()
    })

    it('does not render tags section when no tags', () => {
        render(<ConversationCard conversation={mockConversation} />)

        // Check that no badge elements exist
        expect(screen.queryByText('work')).not.toBeInTheDocument()
    })

    it('links to conversation detail page', () => {
        render(<ConversationCard conversation={mockConversation} />)

        const link = screen.getByRole('link')
        expect(link).toHaveAttribute('href', '/conversation/test-conv-1')
    })

    it('formats date correctly', () => {
        render(<ConversationCard conversation={mockConversation} />)

        // November 14, 2023 (timestamp 1700000000)
        expect(screen.getByText(/Nov 14, 2023/)).toBeInTheDocument()
    })
})
