import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { MarkdownRenderer } from '@/components/conversations/MarkdownRenderer'

const markdownMessageText = [
    '# Release Notes',
    '',
    '- Added **formatted** transcript rendering',
    '- Supports [links](https://example.com) and `inline code`',
    '',
    '> Blockquotes remain readable',
    '',
    '```python',
    "print('hello')",
    '```',
].join('\n')

describe('MarkdownRenderer', () => {
    it('renders headings, lists, links, and blockquotes', () => {
        render(<MarkdownRenderer text={markdownMessageText} />)

        expect(screen.getByRole('heading', { name: 'Release Notes' })).toBeInTheDocument()
        expect(
            screen.getByText((_, element) =>
                element?.textContent === 'Added formatted transcript rendering'
            )
        ).toBeInTheDocument()
        expect(screen.getByRole('link', { name: 'links' })).toHaveAttribute('href', 'https://example.com')
        expect(screen.getByText('Blockquotes remain readable')).toBeInTheDocument()
    })

    it('renders inline code and fenced code blocks', () => {
        render(<MarkdownRenderer text={markdownMessageText} />)

        const inlineCode = screen.getByText('inline code')
        expect(inlineCode.tagName).toBe('CODE')

        const blockCode = screen.getByText("print('hello')")
        expect(blockCode.closest('pre')).toBeInTheDocument()
    })

    it('keeps malformed or oversized markdown blocks readable with horizontal overflow', () => {
        const longCode = ['```txt', 'x'.repeat(400), '```'].join('\n')

        render(<MarkdownRenderer text={longCode} />)

        const blockCode = screen.getByText('x'.repeat(400))
        expect(blockCode.closest('pre')).toHaveClass('overflow-x-auto')
    })

    it('renders raw html as inert text without creating DOM nodes from it', () => {
        const { container } = render(
            <MarkdownRenderer text={"<script>alert('x')</script>\n<div>safe?</div>"} />
        )

        expect(screen.getByTestId('markdown-renderer').textContent).toContain(
            "<script>alert('x')</script>"
        )
        expect(screen.getByTestId('markdown-renderer').textContent).toContain('<div>safe?</div>')
        expect(container.querySelector('script')).not.toBeInTheDocument()
    })
})