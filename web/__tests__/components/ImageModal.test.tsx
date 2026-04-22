import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ImageModal } from '@/components/conversations/ImageModal'
import { TooltipProvider } from '@/components/ui/tooltip'
import type { Attachment } from '@/types'

function renderWithTooltip(ui: React.ReactElement) {
    return render(<TooltipProvider>{ui}</TooltipProvider>)
}

const baseAttachment: Attachment = {
    type: 'image',
    url: '/api/media/conv-001/file_001',
    filename: 'screenshot.png',
    mime_type: 'image/png',
    width: 1920,
    height: 1080,
    size_bytes: 2457600,
    found: true,
}

describe('ImageModal', () => {
    let onClose: ReturnType<typeof vi.fn>

    beforeEach(() => {
        onClose = vi.fn()
    })

    afterEach(() => {
        vi.restoreAllMocks()
    })

    it('renders the image with correct src', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        const img = screen.getByTestId('image-modal-img')
        expect(img).toHaveAttribute('src', 'http://localhost:8000/api/media/conv-001/file_001')
    })

    it('displays the filename in the header', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.getByTestId('image-modal-filename')).toHaveTextContent('screenshot.png')
    })

    it('calls onClose when the close button is clicked', async () => {
        const user = userEvent.setup()

        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        await user.click(screen.getByTestId('image-modal-close'))
        expect(onClose).toHaveBeenCalledOnce()
    })

    it('calls onClose when the backdrop is clicked', async () => {
        const user = userEvent.setup()

        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        await user.click(screen.getByTestId('image-modal-backdrop'))
        expect(onClose).toHaveBeenCalledOnce()
    })

    it('does not close when the modal content itself is clicked', async () => {
        const user = userEvent.setup()

        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        await user.click(screen.getByTestId('image-modal'))
        expect(onClose).not.toHaveBeenCalled()
    })

    it('calls onClose when Escape is pressed', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        fireEvent.keyDown(document, { key: 'Escape' })
        expect(onClose).toHaveBeenCalledOnce()
    })

    it('displays image dimensions when available', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.getByTestId('image-modal-dimensions')).toHaveTextContent('1920 × 1080')
    })

    it('displays file size when available', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.getByTestId('image-modal-size')).toHaveTextContent('2.3 MB')
    })

    it('displays mime type when available', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.getByTestId('image-modal-mime')).toHaveTextContent('image/png')
    })

    it('hides dimensions when not provided', () => {
        const attachment: Attachment = { ...baseAttachment, width: null, height: null }

        renderWithTooltip(
            <ImageModal
                attachment={attachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.queryByTestId('image-modal-dimensions')).not.toBeInTheDocument()
    })

    it('hides file size when not provided', () => {
        const attachment: Attachment = { ...baseAttachment, size_bytes: null }

        renderWithTooltip(
            <ImageModal
                attachment={attachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        expect(screen.queryByTestId('image-modal-size')).not.toBeInTheDocument()
    })

    it('provides a download link with correct filename and href', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        const download = screen.getByTestId('image-modal-download')
        expect(download).toHaveAttribute('href', 'http://localhost:8000/api/media/conv-001/file_001')
        expect(download).toHaveAttribute('download', 'screenshot.png')
    })

    it('renders as a dialog with proper ARIA attributes', () => {
        renderWithTooltip(
            <ImageModal
                attachment={baseAttachment}
                src="http://localhost:8000/api/media/conv-001/file_001"
                onClose={onClose}
            />
        )

        const dialog = screen.getByRole('dialog')
        expect(dialog).toHaveAttribute('aria-modal', 'true')
        expect(dialog).toHaveAttribute('aria-label', 'Image: screenshot.png')
    })
})
