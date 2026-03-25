import type { Attachment } from "@/types";
import { api } from "@/services/api";

function formatBytes(sizeBytes: number | null): string | null {
    if (!sizeBytes || sizeBytes <= 0) {
        return null;
    }

    if (sizeBytes < 1024) {
        return `${sizeBytes} B`;
    }
    if (sizeBytes < 1024 * 1024) {
        return `${(sizeBytes / 1024).toFixed(1)} KB`;
    }
    return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function AttachmentFile({ attachment }: { attachment: Attachment }) {
    const sizeLabel = formatBytes(attachment.size_bytes);

    if (!attachment.found) {
        return (
            <div
                className="rounded-lg border border-dashed border-muted-foreground/40 bg-muted/40 p-4 text-sm text-muted-foreground"
                data-testid="attachment-file-missing"
            >
                File unavailable: {attachment.filename}
            </div>
        );
    }

    return (
        <a
            href={api.getMediaUrl(attachment.url)}
            target="_blank"
            rel="noreferrer"
            className="block rounded-lg border bg-background p-4 transition-colors hover:bg-muted/40"
            data-testid="attachment-file"
        >
            <div className="font-medium text-foreground">{attachment.filename}</div>
            <div className="text-sm text-muted-foreground">
                {attachment.mime_type ?? "Unknown file"}
                {sizeLabel ? ` • ${sizeLabel}` : ""}
            </div>
        </a>
    );
}