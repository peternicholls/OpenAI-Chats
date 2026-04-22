"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
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
            <Tooltip>
                <TooltipTrigger asChild>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setMobileOpen(true)}
                        aria-label="Open navigation"
                        className="h-9 w-9"
                    >
                        <Menu className="h-5 w-5" aria-hidden="true" />
                    </Button>
                </TooltipTrigger>
                <TooltipContent>Open navigation</TooltipContent>
            </Tooltip>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Link href="/" className="rounded-sm font-semibold text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                        ChatGPT Archive
                    </Link>
                </TooltipTrigger>
                <TooltipContent>Return to the conversation browser</TooltipContent>
            </Tooltip>
        </header>
    );
}
