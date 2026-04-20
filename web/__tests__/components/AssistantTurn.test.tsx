import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { AssistantTurn } from '@/components/conversations/AssistantTurn'
import { TooltipProvider } from '@/components/ui/tooltip'
import type { Message } from '@/types'

function renderWithTooltip(ui: React.ReactElement) {
    return render(<TooltipProvider>{ui}</TooltipProvider>)
}

const { copyToClipboard, speakText } = vi.hoisted(() => ({
    copyToClipboard: vi.fn().mockResolvedValue(undefined),
    speakText: vi.fn(),
}))

vi.mock('@/lib/utils', async () => {
    const actual = await vi.importActual<typeof import('@/lib/utils')>('@/lib/utils')
    return {
        ...actual,
        copyToClipboard,
        speakText,
    }
})

beforeEach(() => {
    copyToClipboard.mockClear()
    speakText.mockClear()
})

function createMessage(overrides: Partial<Message>): Message {
    return {
        id: overrides.id ?? 'msg-default',
        role: overrides.role ?? 'assistant',
        content: overrides.content ?? null,
        create_time: overrides.create_time ?? 1700000000,
        attachments: overrides.attachments ?? [],
        segments: overrides.segments,
    }
}

describe('AssistantTurn', () => {
    it('condenses consecutive tool-role messages into one tool block', () => {
        renderWithTooltip(
            <AssistantTurn
                messages={[
                    createMessage({ id: 'assistant-1', content: 'Let me inspect that for you.' }),
                    createMessage({ id: 'tool-1', role: 'tool' }),
                    createMessage({ id: 'tool-2', role: 'tool' }),
                    createMessage({ id: 'tool-3', role: 'tool' }),
                    createMessage({ id: 'assistant-2', content: 'I found the issue in the query builder.' }),
                ]}
            />
        )

        expect(screen.getAllByTestId('tool-block')).toHaveLength(1)
        expect(screen.getByRole('button', { name: 'Toggle 3 tool call details' })).toHaveTextContent('3 tool calls')
    })

    it('copies the raw assistant turn content without tool placeholders', async () => {
        const user = userEvent.setup()

        renderWithTooltip(
            <AssistantTurn
                messages={[
                    createMessage({ id: 'assistant-1', content: 'Step one.' }),
                    createMessage({ id: 'tool-1', role: 'tool' }),
                    createMessage({ id: 'assistant-2', content: 'Step two.' }),
                ]}
            />
        )

        await user.click(screen.getByRole('button', { name: 'Copy turn' }))

        expect(copyToClipboard).toHaveBeenCalledWith('Step one.\n\nStep two.')
    })

    it('speaks the assistant turn content from the turn action', async () => {
        const user = userEvent.setup()

        renderWithTooltip(
            <AssistantTurn
                messages={[
                    createMessage({ id: 'assistant-1', content: 'Summarizing the answer.' }),
                ]}
            />
        )

        await user.click(screen.getByRole('button', { name: 'Speak turn' }))

        expect(speakText).toHaveBeenCalledWith('Summarizing the answer.')
    })
})