import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '@/components/conversations/MessageBubble'
import type { Message } from '@/types'

const mockUserMessage: Message = {
    id: 'msg-001',
    role: 'user',
    content: 'Hello, how are you?',
    create_time: 1700000000,
}

const mockAssistantMessage: Message = {
    id: 'msg-002',
    role: 'assistant',
    content: 'I am doing well, thank you!',
    create_time: 1700000100,
}

describe('MessageBubble', () => {
    describe('user message', () => {
        it('renders user message content', () => {
            render(<MessageBubble message={mockUserMessage} />)

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
        })

        it('shows "You" label for user messages', () => {
            render(<MessageBubble message={mockUserMessage} />)

            expect(screen.getByText('You')).toBeInTheDocument()
        })

        it('has user-specific styling class', () => {
            const { container } = render(<MessageBubble message={mockUserMessage} />)

            const bubble = container.firstChild
            expect(bubble).toHaveClass('bg-blue-50')
        })
    })

    describe('assistant message', () => {
        it('renders assistant message content', () => {
            render(<MessageBubble message={mockAssistantMessage} />)

            expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument()
        })

        it('shows "Assistant" label for assistant messages', () => {
            render(<MessageBubble message={mockAssistantMessage} />)

            expect(screen.getByText('Assistant')).toBeInTheDocument()
        })

        it('has assistant-specific styling class', () => {
            const { container } = render(<MessageBubble message={mockAssistantMessage} />)

            const bubble = container.firstChild
            expect(bubble).toHaveClass('bg-gray-50')
        })
    })

    describe('system message', () => {
        it('shows "System" label for system messages', () => {
            const systemMessage: Message = {
                ...mockUserMessage,
                role: 'system',
            }
            render(<MessageBubble message={systemMessage} />)

            expect(screen.getByText('System')).toBeInTheDocument()
        })
    })

    describe('empty content', () => {
        it('shows "[No content]" when content is empty', () => {
            const emptyMessage: Message = {
                ...mockUserMessage,
                content: '',
            }
            render(<MessageBubble message={emptyMessage} />)

            expect(screen.getByText('[No content]')).toBeInTheDocument()
        })

        it('shows "[No content]" when content is null', () => {
            const nullMessage: Message = {
                ...mockUserMessage,
                content: null as unknown as string,
            }
            render(<MessageBubble message={nullMessage} />)

            expect(screen.getByText('[No content]')).toBeInTheDocument()
        })
    })

    describe('timestamp', () => {
        it('renders formatted time when create_time is present', () => {
            render(<MessageBubble message={mockUserMessage} />)

            // Timestamp 1700000000 = Nov 14, 2023 at some time
            // The exact time will depend on timezone, so just check it exists
            const container = document.querySelector('.text-xs.text-muted-foreground')
            expect(container).toBeInTheDocument()
        })

        it('does not render time when create_time is null', () => {
            const noTimeMessage: Message = {
                ...mockUserMessage,
                create_time: null,
            }
            render(<MessageBubble message={noTimeMessage} />)

            // Should not have the time span
            const timeSpan = document.querySelector('.text-xs.text-muted-foreground')
            expect(timeSpan).not.toBeInTheDocument()
        })
    })
})
