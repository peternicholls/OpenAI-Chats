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

    it('renders inline math delimiters without showing raw backslash notation', () => {
        render(<MarkdownRenderer text="The area is \\(A = \\pi r^2\\) for a circle." />)

        const renderer = screen.getByTestId('markdown-renderer')
        // Preprocessing should convert \(...\) to $...$
        // The raw delimiter notation should not leak through
        expect(renderer.textContent).toContain('The area is')
        expect(renderer.textContent).toContain('for a circle.')
        expect(renderer.textContent).not.toContain('\\(')
        expect(renderer.textContent).not.toContain('\\)')
    })

    it('renders display math delimiters without showing raw backslash notation', () => {
        render(<MarkdownRenderer text="Consider:\n\\[E = mc^2\\]" />)

        const renderer = screen.getByTestId('markdown-renderer')
        expect(renderer.textContent).toContain('Consider:')
        expect(renderer.textContent).not.toContain('\\[')
        expect(renderer.textContent).not.toContain('\\]')
    })

    it('renders mixed prose and math without breaking layout', () => {
        const text = [
            'The quadratic formula is \\(x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\\).',
            '',
            'In display form:',
            '\\[x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\\]',
        ].join('\n')

        render(<MarkdownRenderer text={text} />)

        const renderer = screen.getByTestId('markdown-renderer')
        expect(renderer.querySelectorAll('.katex').length).toBeGreaterThanOrEqual(2)
        expect(renderer.textContent).toContain('The quadratic formula is')
    })

    it('degrades gracefully for unsupported LaTeX environments instead of crashing', () => {
        const text = 'Before math\n$$\\begin{tikzpicture}\\draw (0,0) -- (1,1);\\end{tikzpicture}$$\nAfter math'

        // Should not throw — KaTeX renders an error span instead of crashing
        const { container } = render(<MarkdownRenderer text={text} />)

        expect(container).toBeInTheDocument()
        const renderer = screen.getByTestId('markdown-renderer')
        // The surrounding prose should still render
        expect(renderer.textContent).toContain('Before math')
        expect(renderer.textContent).toContain('After math')
    })
})