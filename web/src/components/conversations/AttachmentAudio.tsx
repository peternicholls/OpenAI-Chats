import type { Attachment } from "@/types";
import { api } from "@/services/api";

export function AttachmentAudio({ attachment }: { attachment: Attachment }) {
    if (!attachment.found) {
        return (
            <div
                className="rounded-lg border border-dashed border-muted-foreground/40 bg-muted/40 p-4 text-sm text-muted-foreground"
                data-testid="attachment-audio-missing"
            >
                Audio unavailable: {attachment.filename}
            </div>
        );
    }

    return (
        <div className="rounded-lg border bg-background p-3" data-testid="attachment-audio">
            <div className="mb-2 text-sm font-medium text-foreground">{attachment.filename}</div>
            <audio controls preload="none" className="w-full">
                <source src={api.getMediaUrl(attachment.url)} type={attachment.mime_type ?? undefined} />
                Your browser does not support audio playback.
            </audio>
        </div>
    );
}