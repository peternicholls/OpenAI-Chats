"use client";

import { useState, type ReactNode } from "react";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface CollapsibleSectionProps {
    title: string;
    icon?: ReactNode;
    count?: number;
    defaultOpen?: boolean;
    children: ReactNode;
    sectionId: string;
}

/**
 * Sidebar section with a button-driven disclosure. Persists open/closed state
 * per `sectionId` in localStorage so users keep their preference across reloads.
 */
export function CollapsibleSection({
    title,
    icon,
    count,
    defaultOpen = true,
    children,
    sectionId,
}: CollapsibleSectionProps) {
    const storageKey = `sidebar-section:${sectionId}`;

    const [open, setOpen] = useState<boolean>(() => {
        if (typeof window === "undefined") return defaultOpen;
        const stored = window.localStorage.getItem(storageKey);
        if (stored === "open") return true;
        if (stored === "closed") return false;
        return defaultOpen;
    });

    const toggle = () => {
        setOpen((prev) => {
            const next = !prev;
            if (typeof window !== "undefined") {
                window.localStorage.setItem(storageKey, next ? "open" : "closed");
            }
            return next;
        });
    };

    const panelId = `sidebar-section-panel-${sectionId}`;
    const headingId = `sidebar-section-heading-${sectionId}`;

    return (
        <section className="space-y-1" aria-labelledby={headingId}>
            <button
                id={headingId}
                type="button"
                onClick={toggle}
                aria-expanded={open}
                aria-controls={panelId}
                className="group flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
                <ChevronRight
                    className={cn(
                        "h-3.5 w-3.5 shrink-0 text-muted-foreground/70 transition-transform",
                        open && "rotate-90"
                    )}
                    aria-hidden="true"
                />
                {icon ? <span className="text-muted-foreground/80">{icon}</span> : null}
                <span className="flex-1 text-left">{title}</span>
                {typeof count === "number" && (
                    <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-medium normal-case tracking-normal text-muted-foreground">
                        {count}
                    </span>
                )}
            </button>
            <div id={panelId} role="region" hidden={!open} className={cn(open ? "px-1 pt-1 pb-2" : undefined)}>
                {open ? children : null}
            </div>
        </section>
    );
}
