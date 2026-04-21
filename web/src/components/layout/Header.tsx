"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSidebarUi } from "@/components/layout/SidebarUiContext";

/**
 * Top-of-page header. Search has moved to the sidebar; on desktop the
 * header is hidden so the sidebar provides all primary navigation.
 */
export function Header() {
    const { setMobileOpen } = useSidebarUi();

    return (
        <header
            role="banner"
            className="sticky top-0 z-30 flex h-12 items-center gap-2 border-b bg-background/95 px-3 backdrop-blur supports-backdrop-filter:bg-background/60 md:hidden"
        >
            <Button
                variant="ghost"
                size="icon"
                onClick={() => setMobileOpen(true)}
                aria-label="Open navigation"
                className="h-9 w-9"
            >
                <Menu className="h-5 w-5" aria-hidden="true" />
            </Button>
            <Link href="/" className="font-semibold text-foreground">
                ChatGPT Archive
            </Link>
        </header>
    );
}
