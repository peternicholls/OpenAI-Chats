import type { Attachment } from "@/types";
import { api } from "@/services/api";

export function AttachmentImage({ attachment }: { attachment: Attachment }) {
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
        <a
            href={src}
            target="_blank"
            rel="noreferrer"
            className="block max-w-xl overflow-hidden rounded-lg border bg-background"
            data-testid="attachment-image-link"
        >
            <img
                src={src}
                alt={attachment.filename}
                width={attachment.width ?? undefined}
                height={attachment.height ?? undefined}
                loading="lazy"
                className="max-h-[28rem] w-full object-contain"
                data-testid="attachment-image"
            />
        </a>
    );
}