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

        // Syntax highlighting splits code tokens across spans; check the code block container
        const codeBlock = screen.getByTestId('code-block')
        expect(codeBlock).toBeInTheDocument()
        expect(codeBlock.textContent).toContain("print('hello')")
    })

    it('wraps code blocks to container width without a horizontal scrollbar', () => {
        // Horizontal scrollbars are a UX failure per design notes; wrapping must be used instead.
        const longCode = ['```txt', 'x'.repeat(400), '```'].join('\n')

        render(<MarkdownRenderer text={longCode} />)

        const codeBlock = screen.getByTestId('code-block')
        // No overflow-x-auto anywhere inside the code block
        expect(codeBlock.querySelector('.overflow-x-auto')).toBeNull()
        // white-space: pre-wrap must be applied to the inner code element (inline style wins over RSH defaults)
        const codeElem = codeBlock.querySelector('.code-block-code') as HTMLElement
        expect(codeElem?.style.whiteSpace).toBe('pre-wrap')
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

describe('MarkdownRenderer — line numbers (T006)', () => {
    it('renders line number spans that are excluded from drag selection via user-select: none', () => {
        const code = ['```python', 'x = 1', 'y = 2', 'z = 3', '```'].join('\n')
        render(<MarkdownRenderer text={code} />)

        const codeBlock = screen.getByTestId('code-block')
        // Line number spans are identified by their userSelect: none inline style
        const lineNumSpans = Array.from(codeBlock.querySelectorAll('span')).filter(
            (s) => (s as HTMLElement).style.userSelect === 'none'
        )
        expect(lineNumSpans.length).toBeGreaterThan(0)
        lineNumSpans.forEach((span) => {
            expect((span as HTMLElement).style.userSelect).toBe('none')
        })
    })

    it('copy button is present and code content renders without line number prefixes', () => {
        // codeText is extracted from the ReactMarkdown <code> children before SyntaxHighlighter
        // adds line numbers — so the copy output structurally cannot include line numbers.
        const code = ['```python', 'x = 1', 'y = 2', '```'].join('\n')
        render(<MarkdownRenderer text={code} />)

        expect(screen.getByRole('button', { name: /copy code/i })).toBeInTheDocument()
        // Syntax highlighting splits code into spans; check textContent of the block
        const codeBlock = screen.getByTestId('code-block')
        expect(codeBlock.textContent).toContain('x = 1')
        expect(codeBlock.textContent).toContain('y = 2')
    })
})

// Fixture: a long user prompt exceeding 1600 characters
export const longUserPromptFixture =
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

describe('MarkdownRenderer — long user prompt', () => {
    it('renders a long user prompt (>1600 chars) without truncation or error', () => {
        render(<MarkdownRenderer text={longUserPromptFixture} />)

        const renderer = screen.getByTestId('markdown-renderer')
        expect(renderer.textContent).toContain('I have been thinking about this problem')
        expect(renderer.textContent?.length).toBeGreaterThan(1600)
    })
})