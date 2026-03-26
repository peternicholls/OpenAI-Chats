import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { MarkdownRenderer } from '@/components/conversations/MarkdownRenderer'
import { markdownMessageText } from '@/__tests__/mocks/handlers'

describe('MarkdownRenderer', () => {
    it('renders headings, lists, links, and blockquotes', () => {
        render(<MarkdownRenderer text={markdownMessageText} />)

        expect(screen.getByRole('heading', { name: 'Release Notes' })).toBeInTheDocument()
        expect(screen.getByText('Added formatted transcript rendering')).toBeInTheDocument()
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
})