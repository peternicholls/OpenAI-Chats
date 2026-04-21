"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

/**
 * Compact search field for the sidebar. Submits to /search?q=... on Enter.
 * Uses native form submission so keyboard users can search without a mouse.
 */
export function SidebarSearch({ onNavigate }: { onNavigate?: () => void } = {}) {
    const router = useRouter();
    const [value, setValue] = useState("");

    return (
        <form
            role="search"
            onSubmit={(event) => {
                event.preventDefault();
                const trimmed = value.trim();
                if (!trimmed) {
                    onNavigate?.();
                    router.push("/search");
                    return;
                }
                onNavigate?.();
                router.push(`/search?q=${encodeURIComponent(trimmed)}`);
            }}
            className="relative"
        >
            <label htmlFor="sidebar-search-input" className="sr-only">
                Search conversations
            </label>
            <Search
                aria-hidden="true"
                className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground"
            />
            <Input
                id="sidebar-search-input"
                type="search"
                placeholder="Search conversations…"
                value={value}
                onChange={(event) => setValue(event.target.value)}
                className="h-8 bg-background pl-8 text-[13px]"
                autoComplete="off"
            />
        </form>
    );
}
