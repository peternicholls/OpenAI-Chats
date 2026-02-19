import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConversationCard } from '@/components/conversations/ConversationCard'
import type { Conversation } from '@/types'
import { createWrapper } from '../utils/test-utils'

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
    const renderWithProviders = (conversation: Conversation) =>
        render(<ConversationCard conversation={conversation} />, {
            wrapper: createWrapper(),
        })

    it('renders conversation title', () => {
        renderWithProviders(mockConversation)

        expect(screen.getByText('Test Conversation Title')).toBeInTheDocument()
    })

    it('renders message count', () => {
        renderWithProviders(mockConversation)

        expect(screen.getByText(/5 messages/)).toBeInTheDocument()
    })

    it('renders model name when present', () => {
        renderWithProviders(mockConversation)

        expect(screen.getByText(/gpt-4/)).toBeInTheDocument()
    })

    it('renders "[Untitled]" when title is missing', () => {
        const untitledConv: Conversation = {
            ...mockConversation,
            title: '',
        }
        renderWithProviders(untitledConv)

        expect(screen.getByText('[Untitled]')).toBeInTheDocument()
    })

    it('shows favorite star when is_favorite is true', () => {
        const favoriteConv: Conversation = {
            ...mockConversation,
            is_favorite: true,
        }
        renderWithProviders(favoriteConv)

        // Star icon should be present (SVG)
        const star = document.querySelector('svg')
        expect(star).toBeInTheDocument()
    })

    it('renders tags when present', () => {
        const taggedConv: Conversation = {
            ...mockConversation,
            tags: ['work', 'important'],
        }
        renderWithProviders(taggedConv)

        expect(screen.getByText('work')).toBeInTheDocument()
        expect(screen.getByText('important')).toBeInTheDocument()
    })

    it('does not render tags section when no tags', () => {
        renderWithProviders(mockConversation)

        // Check that no badge elements exist
        expect(screen.queryByText('work')).not.toBeInTheDocument()
    })

    it('links to conversation detail page', () => {
        renderWithProviders(mockConversation)

        const link = screen.getByRole('link')
        expect(link).toHaveAttribute('href', '/conversation/test-conv-1')
    })

    it('formats date correctly', () => {
        renderWithProviders(mockConversation)

        // November 14, 2023 (timestamp 1700000000)
        expect(screen.getByText(/Nov 14, 2023/)).toBeInTheDocument()
    })
})
