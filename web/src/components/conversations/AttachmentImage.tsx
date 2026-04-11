import { useState } from "react";

import type { Attachment } from "@/types";
import { api } from "@/services/api";
import { ImageModal } from "@/components/conversations/ImageModal";

export function AttachmentImage({ attachment }: { attachment: Attachment }) {
    const [open, setOpen] = useState(false);

    if (!attachment.found) {
        return (
            <div
                className="rounded-lg border border-dashed border-muted-foreground/40 bg-muted/40 p-4 text-sm text-muted-foreground"
                data-testid="attachment-image-missing"
            >
                Image unavailable: {attachment.filename}
            </div>
        );
    }

    const src = api.getMediaUrl(attachment.url);

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className="cursor-pointer overflow-hidden rounded-lg border bg-background focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label={`Open image: ${attachment.filename}`}
                data-testid="attachment-image-thumbnail-button"
            >
                <img
                    src={src}
                    alt=""
                    loading="lazy"
                    className="h-32 w-48 object-cover"
                    data-testid="attachment-image-thumbnail"
                />
            </button>
            {open && (
                <ImageModal
                    attachment={attachment}
                    src={src}
                    onClose={() => setOpen(false)}
                />
            )}
        </>
    );
}