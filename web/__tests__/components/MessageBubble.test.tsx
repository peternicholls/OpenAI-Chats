import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MessageBubble } from '@/components/conversations/MessageBubble'
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

const mockUserMessage: Message = {
    id: 'msg-001',
    role: 'user',
    content: 'Hello, how are you?',
    create_time: 1700000000,
    attachments: [],
}

const longUserPromptContent =
    'I have been thinking about this problem for a while now and wanted to get your perspective. ' +
    'The situation is fairly complex: we have a distributed system with multiple services that need to ' +
    'coordinate state changes across a network partition. The challenge is that we cannot guarantee ' +
    'message delivery ordering, and at the same time we need to ensure that no two services apply ' +
    'conflicting updates simultaneously. I have read about the Raft consensus algorithm and also about ' +
    'CRDTs as potential solutions, but I am not sure which approach fits our constraints best given that ' +
    'our throughput requirements are quite high and we also need to keep latency under 50 milliseconds. ' +
    'One key concern is the operational complexity of running a Raft cluster: we would need an odd number of ' +
    'nodes to maintain quorum, and leadership elections could introduce latency spikes that violate our SLA. ' +
    'On the other hand, CRDTs are naturally commutative and do not require coordination, which appeals to us, ' +
    'but they impose constraints on the data model that might force us to redesign how we represent state. ' +
    'I am also weighing whether a hybrid approach — using CRDTs for eventual-consistency data and a lightweight ' +
    'consensus protocol only for the critical path — could give us the best of both worlds without the full ' +
    'overhead of a complete Raft implementation across every service in the mesh. ' +
    'We currently serve around twelve thousand requests per second at peak, and any solution must gracefully ' +
    'degrade under network partitions without corrupting shared state or requiring a full cluster restart. ' +
    'Could you walk me through the trade-offs so I can make an informed decision before our next architecture review?'

const mockLongUserMessage: Message = {
    id: 'msg-long-001',
    role: 'user',
    content: longUserPromptContent,
    create_time: 1700000000,
    attachments: [],
}

const mockAssistantMessage: Message = {
    id: 'msg-002',
    role: 'assistant',
    content: 'I am doing well, thank you!',
    create_time: 1700000100,
    attachments: [],
}

describe('MessageBubble', () => {
    describe('user message', () => {
        it('renders user message content', () => {
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
        })

        it('shows "You" label for user messages', () => {
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            expect(screen.getByText('You')).toBeInTheDocument()
        })

        it('has the message test ID', () => {
            const { container } = renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            const bubble = container.firstChild
            expect(bubble).toHaveAttribute('data-testid', 'message')
        })

        it('copies raw turn content from the turn action', async () => {
            const user = userEvent.setup()
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            await user.click(screen.getByRole('button', { name: 'Copy turn' }))

            expect(copyToClipboard).toHaveBeenCalledWith('Hello, how are you?')
        })

        it('shows the check icon as visual feedback after copying', async () => {
            const user = userEvent.setup()
            const { container } = renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            const copyButton = container.querySelector('[data-testid="turn-copy-button"]')!
            // Before click: no green check icon
            expect(copyButton.querySelector('svg')).not.toHaveClass('text-green-600')

            await user.click(copyButton as HTMLElement)

            // After click: Check icon rendered with green colour class
            await waitFor(() => {
                const icon = copyButton.querySelector('svg')
                expect(icon).toHaveClass('text-green-600')
            })
        })

        it('speaks raw turn content from the turn action', async () => {
            const user = userEvent.setup()
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            await user.click(screen.getByRole('button', { name: 'Speak turn' }))

            expect(speakText).toHaveBeenCalledWith('Hello, how are you?')
        })
    })

    describe('assistant message', () => {
        it('renders assistant message content', () => {
            renderWithTooltip(<MessageBubble message={mockAssistantMessage} />)

            expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument()
        })

        it('shows "Assistant" label for assistant messages', () => {
            renderWithTooltip(<MessageBubble message={mockAssistantMessage} />)

            expect(screen.getByText('Assistant')).toBeInTheDocument()
        })

        it('has the message test ID', () => {
            const { container } = renderWithTooltip(<MessageBubble message={mockAssistantMessage} />)

            const bubble = container.firstChild
            expect(bubble).toHaveAttribute('data-testid', 'message')
        })

        it('prefers render segments over raw markdown content', () => {
            const segmentedMessage: Message = {
                ...mockAssistantMessage,
                content: '# Release Notes\n\n- Added **formatted** transcript rendering',
                segments: [
                    {
                        kind: 'markdown',
                        text: '# Release Notes\n\n- Added **formatted** transcript rendering',
                        attachment_index: null,
                        fallback_label: null,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={segmentedMessage} />)

            expect(screen.getByRole('heading', { name: 'Release Notes' })).toBeInTheDocument()
            expect(
                screen.getByText((_, element) =>
                    element?.textContent === 'Added formatted transcript rendering'
                )
            ).toBeInTheDocument()
            expect(screen.queryByText('# Release Notes')).not.toBeInTheDocument()
        })
    })

    describe('system message', () => {
        it('shows "System" label for system messages', () => {
            const systemMessage: Message = {
                ...mockUserMessage,
                role: 'system',
            }
            renderWithTooltip(<MessageBubble message={systemMessage} />)

            expect(screen.getByText('System')).toBeInTheDocument()
        })
    })

    describe('empty content', () => {
        it('shows "[No content]" when content is empty', () => {
            const emptyMessage: Message = {
                ...mockUserMessage,
                content: '',
            }
            renderWithTooltip(<MessageBubble message={emptyMessage} />)

            expect(screen.getByText('[No content]')).toBeInTheDocument()
        })

        it('shows "[No content]" when content is null', () => {
            const nullMessage: Message = {
                ...mockUserMessage,
                content: null as unknown as string,
            }
            renderWithTooltip(<MessageBubble message={nullMessage} />)

            expect(screen.getByText('[No content]')).toBeInTheDocument()
        })
    })

    describe('timestamp', () => {
        it('renders formatted time when create_time is present', () => {
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            // Timestamp 1700000000 = Nov 14, 2023 at some time
            // The exact time will depend on timezone, so just check it exists
            const timeElement = document.querySelector('time')
            expect(timeElement).toBeInTheDocument()
        })

        it('does not render time when create_time is null', () => {
            const noTimeMessage: Message = {
                ...mockUserMessage,
                create_time: null,
            }
            renderWithTooltip(<MessageBubble message={noTimeMessage} />)

            // Should not have the time element
            const timeElement = document.querySelector('time')
            expect(timeElement).not.toBeInTheDocument()
        })
    })

    describe('attachments', () => {
        it('keeps the standard full-width user bubble while rendering the larger image thumbnail', () => {
            const message: Message = {
                id: 'user-image-only',
                role: 'user',
                content: '[[ATTACHMENT:0]]',
                create_time: 1700000000,
                attachments: [
                    {
                        type: 'image',
                        url: '/api/media/conv/image_1',
                        filename: 'gymnast.png',
                        mime_type: 'image/png',
                        width: 400,
                        height: 300,
                        size_bytes: 1000,
                        found: true,
                    },
                ],
                segments: [
                    {
                        kind: 'attachment',
                        text: null,
                        attachment_index: 0,
                        fallback_label: null,
                    },
                ],
            }

            const { container } = renderWithTooltip(<MessageBubble message={message} />)

            const bubble = container.querySelector('[data-testid="message"]')
            const contentColumn = bubble?.children.item(1)
            const thumbnail = screen.getByTestId('attachment-image-thumbnail')

            expect(bubble).toHaveClass('flex', 'gap-3')
            expect(bubble).not.toHaveClass('w-fit', 'max-w-prose', 'self-start')
            expect(contentColumn).toHaveClass('flex-1')
            expect(thumbnail).toHaveClass('h-40', 'w-auto', 'max-w-64', 'object-contain')
        })

        it('renders inline images from attachment tokens', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: 'Before\n[[ATTACHMENT:0]]\nAfter',
                attachments: [
                    {
                        type: 'image',
                        url: '/api/media/conv/file_001',
                        filename: 'sample.png',
                        mime_type: 'image/png',
                        width: 640,
                        height: 480,
                        size_bytes: 1024,
                        found: true,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByText('Before')).toBeInTheDocument()
            expect(screen.getByText('After')).toBeInTheDocument()
            expect(screen.getByTestId('attachment-image-thumbnail-button')).toBeInTheDocument()
        })

        it('renders consecutive image attachments inline within a single row', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: '[[ATTACHMENT:0]][[ATTACHMENT:1]]',
                attachments: [
                    {
                        type: 'image',
                        url: '/api/media/conv/image_1',
                        filename: 'first.png',
                        mime_type: 'image/png',
                        width: 400,
                        height: 300,
                        size_bytes: 1000,
                        found: true,
                    },
                    {
                        type: 'image',
                        url: '/api/media/conv/image_2',
                        filename: 'second.png',
                        mime_type: 'image/png',
                        width: 400,
                        height: 300,
                        size_bytes: 1200,
                        found: true,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            const inlineGroup = screen.getByTestId('attachment-inline-group')
            const buttons = inlineGroup.querySelectorAll('[data-testid="attachment-image-thumbnail-button"]')

            expect(inlineGroup).toHaveClass('flex', 'flex-wrap', 'gap-3')
            expect(buttons).toHaveLength(2)
        })

        it('renders file fallback cards for missing attachments', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: '[[ATTACHMENT:0]]',
                attachments: [
                    {
                        type: 'file',
                        url: '/api/media/root/file-abc',
                        filename: 'document.pdf',
                        mime_type: 'application/pdf',
                        width: null,
                        height: null,
                        size_bytes: 2048,
                        found: false,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByTestId('attachment-file-missing')).toBeInTheDocument()
            expect(screen.getByText(/document.pdf/)).toBeInTheDocument()
        })

        it('renders audio attachments when content is empty', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: null,
                attachments: [
                    {
                        type: 'audio',
                        url: '/api/media/conv/audio_1',
                        filename: 'voice.wav',
                        mime_type: 'audio/wav',
                        width: null,
                        height: null,
                        size_bytes: 5000,
                        found: true,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByTestId('attachment-audio')).toBeInTheDocument()
            expect(screen.queryByText('[No content]')).not.toBeInTheDocument()
        })

        it('preserves mixed text and multiple attachment ordering', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: 'Intro\n[[ATTACHMENT:0]]\nBetween\n[[ATTACHMENT:1]]\nOutro\n[[ATTACHMENT:2]]',
                attachments: [
                    {
                        type: 'image',
                        url: '/api/media/conv/image_1',
                        filename: 'image.png',
                        mime_type: 'image/png',
                        width: 400,
                        height: 300,
                        size_bytes: 1000,
                        found: true,
                    },
                    {
                        type: 'file',
                        url: '/api/media/root/file-abc',
                        filename: 'notes.pdf',
                        mime_type: 'application/pdf',
                        width: null,
                        height: null,
                        size_bytes: 2500,
                        found: true,
                    },
                    {
                        type: 'audio',
                        url: '/api/media/conv/audio_1',
                        filename: 'voice.wav',
                        mime_type: 'audio/wav',
                        width: null,
                        height: null,
                        size_bytes: 3200,
                        found: true,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByText('Intro')).toBeInTheDocument()
            expect(screen.getByText('Between')).toBeInTheDocument()
            expect(screen.getByText('Outro')).toBeInTheDocument()
            expect(screen.getByTestId('attachment-image-thumbnail-button')).toBeInTheDocument()
            expect(screen.getByTestId('attachment-file')).toBeInTheDocument()
            expect(screen.getByTestId('attachment-audio')).toBeInTheDocument()
        })

        it('renders structured attachment and fallback segments without showing raw asset payloads', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: [
                    'Intro paragraph before structured content.',
                    "{'content_type': 'image_asset_pointer', 'asset_pointer': 'sediment://file_001'}",
                    'Follow-up prose after image.',
                ].join('\n'),
                attachments: [
                    {
                        type: 'image',
                        url: '/api/media/conv/image_1',
                        filename: 'image.png',
                        mime_type: 'image/png',
                        width: 400,
                        height: 300,
                        size_bytes: 1000,
                        found: true,
                    },
                ],
                segments: [
                    {
                        kind: 'markdown',
                        text: 'Intro paragraph before structured content.',
                        attachment_index: null,
                        fallback_label: null,
                    },
                    {
                        kind: 'attachment',
                        text: null,
                        attachment_index: 0,
                        fallback_label: null,
                    },
                    {
                        kind: 'markdown',
                        text: 'Follow-up prose after image.',
                        attachment_index: null,
                        fallback_label: null,
                    },
                    {
                        kind: 'fallback',
                        text: "{'content_type': 'unsupported_widget', 'metadata': {'label': 'chart'}}",
                        attachment_index: null,
                        fallback_label: 'Unsupported content',
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByTestId('attachment-image-thumbnail-button')).toBeInTheDocument()
            expect(screen.getByTestId('fallback-block')).toBeInTheDocument()
            expect(screen.queryByText(/image_asset_pointer/)).not.toBeInTheDocument()
            expect(screen.getByText('Unsupported content')).toBeInTheDocument()
        })

        it('shows a fallback block when an attachment segment points to a missing index', () => {
            const message: Message = {
                ...mockAssistantMessage,
                content: null,
                attachments: [],
                segments: [
                    {
                        kind: 'attachment',
                        text: null,
                        attachment_index: 9,
                        fallback_label: null,
                    },
                ],
            }

            renderWithTooltip(<MessageBubble message={message} />)

            expect(screen.getByText('Missing attachment')).toBeInTheDocument()
            expect(screen.getByText(/Attachment index 9 is not available/)).toBeInTheDocument()
        })
    })

    describe('long user prompt', () => {
        it('collapses a long user prompt until expanded', async () => {
            const user = userEvent.setup()
            renderWithTooltip(<MessageBubble message={mockLongUserMessage} />)

            expect(screen.getByText('You')).toBeInTheDocument()
            const bubble = document.querySelector('[data-testid="message"]')
            expect(bubble?.textContent?.length).toBeLessThan(longUserPromptContent.length)
            expect(screen.getByRole('button', { name: 'Read more' })).toBeInTheDocument()

            await user.click(screen.getByRole('button', { name: 'Read more' }))

            expect(screen.getByRole('button', { name: 'Show less' })).toBeInTheDocument()
            expect(bubble?.textContent).toContain('Could you walk me through the trade-offs')
        })

        it('shows the truncation affordance by default for long user prompts', () => {
            renderWithTooltip(<MessageBubble message={mockLongUserMessage} />)

            expect(screen.getByText('You')).toBeInTheDocument()
            expect(screen.getByRole('button', { name: 'Read more' })).toBeInTheDocument()
        })

        it('keeps collapsed long user prompts on the same body typography as markdown-rendered prompts', () => {
            renderWithTooltip(<MessageBubble message={mockLongUserMessage} />)

            const collapsedBody = screen.getByText(/I have been thinking about this problem/)

            expect(collapsedBody).toHaveClass('text-[14px]', 'leading-[1.55]')
        })

        it('does not collapse when long prompt truncation is disabled', () => {
            renderWithTooltip(<MessageBubble message={mockLongUserMessage} enableLongPromptTruncation={false} />)

            const bubble = document.querySelector('[data-testid="message"]')
            expect(bubble?.textContent).toContain('Could you walk me through the trade-offs')
            expect(screen.queryByRole('button', { name: 'Read more' })).not.toBeInTheDocument()
        })
    })

    describe('rule lines (T010)', () => {
        it('does not insert an hr element between message content sections', () => {
            renderWithTooltip(<MessageBubble message={mockAssistantMessage} />)

            const bubble = document.querySelector('[data-testid="message"]')
            expect(bubble?.querySelector('hr')).not.toBeInTheDocument()
        })

        it('does not insert an hr element in user messages', () => {
            renderWithTooltip(<MessageBubble message={mockUserMessage} />)

            const bubble = document.querySelector('[data-testid="message"]')
            expect(bubble?.querySelector('hr')).not.toBeInTheDocument()
        })
    })
})

describe('MessageBubble — ThinkingBlock scoping (T031)', () => {
    it('does not render a ThinkingBlock for a user-role message even when segments include one', () => {
        const userMessageWithThinkingSegment: Message = {
            id: 'user-thinking-leak',
            role: 'user',
            content: 'Here is my image',
            create_time: 1700000002,
            attachments: [],
            segments: [
                { kind: 'thinking', activity_type: 'reasoning', text: null, attachment_index: null, fallback_label: null },
                { kind: 'markdown', text: 'Here is my image', attachment_index: null, fallback_label: null, activity_type: null },
            ],
        }
        renderWithTooltip(<MessageBubble message={userMessageWithThinkingSegment} />)

        // ThinkingBlock renders a disclosure button with its label — it must not appear
        expect(screen.queryByRole('button', { name: /reasoning/i })).not.toBeInTheDocument()
        expect(screen.queryByRole('button', { name: /searched the web/i })).not.toBeInTheDocument()
        // The prose content should still render
        expect(screen.getByText('Here is my image')).toBeInTheDocument()
    })
})
