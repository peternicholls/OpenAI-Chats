import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import { FallbackBlock } from '@/components/conversations/FallbackBlock'

describe('FallbackBlock', () => {
    it('renders the fallback label and body text', () => {
        render(<FallbackBlock label="Unsupported content" text="{'content_type': 'widget'}" />)

        expect(screen.getByText('Unsupported content')).toBeInTheDocument()
        expect(screen.getByText("{'content_type': 'widget'}")).toBeInTheDocument()
    })

    it('renders label text as inert content', () => {
        const { container } = render(
            <FallbackBlock label="<script>alert(1)</script>" text="payload" />
        )

        expect(screen.getByText('<script>alert(1)</script>')).toBeInTheDocument()
        expect(container.querySelector('script')).not.toBeInTheDocument()
    })
})