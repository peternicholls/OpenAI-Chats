import { useCallback, useEffect } from "react";
import { createPortal } from "react-dom";
import { Download, X } from "lucide-react";

import type { Attachment } from "@/types";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

function formatBytes(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface ImageModalProps {
    attachment: Attachment;
    src: string;
    onClose: () => void;
}

export function ImageModal({ attachment, src, onClose }: ImageModalProps) {
    const handleKeyDown = useCallback(
        (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        },
        [onClose],
    );

    useEffect(() => {
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [handleKeyDown]);

    return createPortal(
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
            role="dialog"
            aria-modal="true"
            aria-label={`Image: ${attachment.filename}`}
            data-testid="image-modal-backdrop"
            onClick={onClose}
        >
            <div
                className="relative flex max-h-[90vh] max-w-4xl flex-col overflow-hidden rounded-xl bg-background shadow-2xl"
                data-testid="image-modal"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between border-b px-4 py-3">
                    <span
                        className="truncate text-sm font-medium"
                        data-testid="image-modal-filename"
                    >
                        {attachment.filename}
                    </span>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button
                                type="button"
                                onClick={onClose}
                                className="ml-4 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                aria-label="Close image preview"
                                data-testid="image-modal-close"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent>Close image preview</TooltipContent>
                    </Tooltip>
                </div>

                {/* Image */}
                <div className="flex min-h-0 flex-1 items-center justify-center overflow-auto bg-muted/30 p-4">
                    <img
                        src={src}
                        alt={attachment.filename}
                        className="max-h-full max-w-full object-contain"
                        data-testid="image-modal-img"
                    />
                </div>

                {/* Footer: metadata + download */}
                <div className="flex items-center justify-between border-t px-4 py-3">
                    <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                        {attachment.width && attachment.height && (
                            <span data-testid="image-modal-dimensions">
                                {attachment.width} × {attachment.height}
                            </span>
                        )}
                        {attachment.size_bytes !== null && (
                            <span data-testid="image-modal-size">
                                {formatBytes(attachment.size_bytes)}
                            </span>
                        )}
                        {attachment.mime_type && (
                            <span data-testid="image-modal-mime">
                                {attachment.mime_type}
                            </span>
                        )}
                    </div>
                    <a
                        href={src}
                        download={attachment.filename}
                        className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        data-testid="image-modal-download"
                    >
                        <Download className="h-3.5 w-3.5" />
                        Download
                    </a>
                </div>
            </div>
        </div>,
        document.body,
    );
}
