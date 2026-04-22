"use client";

import Link from "next/link";
import { Suspense } from "react";
import { ArrowLeft, ArrowRight, Download, HelpCircle, MessageSquare, Settings, Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { SidebarConversationList } from "@/components/layout/SidebarConversationList";
import { SidebarFavoritesSection } from "@/components/layout/SidebarFavoritesSection";
import { SidebarSearch } from "@/components/layout/SidebarSearch";
import { SidebarTagsSection } from "@/components/layout/SidebarTagsSection";
import { useSidebarUi } from "@/components/layout/SidebarUiContext";
import { cn } from "@/lib/utils";

const FOOTER_LINKS: Array<{
    name: string;
    href: string;
    icon: typeof Settings;
    tooltip: string;
    external?: boolean;
}> = [
        { name: "Settings", href: "/settings", icon: Settings, tooltip: "Adjust archive preferences" },
        { name: "Import", href: "/import", icon: Upload, tooltip: "Import a ChatGPT archive ZIP" },
        { name: "Export", href: "/?manage=1", icon: Download, tooltip: "Open export and management tools" },
        {
            name: "Help",
            href: "https://github.com/peternicholls/OpenAI-Chats#readme",
            icon: HelpCircle,
            tooltip: "Open the project guide and docs",
            external: true,
        },
    ];

function CollapsedRail() {
    const { toggleCollapsed } = useSidebarUi();
    return (
        <aside
            aria-label="Primary"
            className="hidden w-14 shrink-0 border-r bg-(--sidebar-surface) md:flex md:flex-col"
        >
            <div className="flex flex-col items-center gap-1 px-2 py-3">
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={toggleCollapsed}
                            aria-label="Expand sidebar"
                            aria-expanded={false}
                            className="h-9 w-9"
                        >
                            <ArrowRight className="h-4 w-4" aria-hidden="true" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent side="right">Expand sidebar</TooltipContent>
                </Tooltip>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Link
                            href="/"
                            className="flex h-9 w-9 items-center justify-center rounded-md text-foreground hover:bg-muted"
                            aria-label="Conversations"
                        >
                            <MessageSquare className="h-4 w-4" aria-hidden="true" />
                        </Link>
                    </TooltipTrigger>
                    <TooltipContent side="right">Conversations</TooltipContent>
                </Tooltip>
            </div>
            <div className="mt-auto flex flex-col items-center gap-1 px-2 pb-3">
                {FOOTER_LINKS.map(({ name, href, icon: Icon, tooltip, external }) => (
                    <Tooltip key={name}>
                        <TooltipTrigger asChild>
                            {external ? (
                                <a
                                    href={href}
                                    target="_blank"
                                    rel="noreferrer"
                                    aria-label={name}
                                    className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
                                >
                                    <Icon className="h-4 w-4" aria-hidden="true" />
                                </a>
                            ) : (
                                <Link
                                    href={href}
                                    aria-label={name}
                                    className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
                                >
                                    <Icon className="h-4 w-4" aria-hidden="true" />
                                </Link>
                            )}
                        </TooltipTrigger>
                        <TooltipContent side="right">{tooltip}</TooltipContent>
                    </Tooltip>
                ))}
            </div>
        </aside>
    );
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
    const { toggleCollapsed } = useSidebarUi();
    return (
        <div className="flex h-full min-h-0 flex-col">
            <div className="shrink-0 px-3 pt-4 pb-2">
                <div className="mb-3 flex items-center gap-2">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Link
                                href="/"
                                onClick={() => onNavigate?.()}
                                className="flex flex-1 items-center gap-2 rounded-md px-1 py-1 text-foreground transition-colors hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                            >
                                <MessageSquare className="h-5 w-5 text-primary" aria-hidden="true" />
                                <span className="text-base font-bold tracking-tight">ChatGPT Archive</span>
                            </Link>
                        </TooltipTrigger>
                        <TooltipContent side="bottom" align="start">
                            Return to the conversation browser
                        </TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    toggleCollapsed();
                                }}
                                aria-label="Collapse sidebar"
                                aria-expanded={true}
                                className="hidden h-7 w-7 md:inline-flex"
                            >
                                <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">Collapse sidebar</TooltipContent>
                    </Tooltip>
                </div>
                <SidebarSearch onNavigate={onNavigate} />
            </div>
            <hr className="border-border" role="presentation" />

            <div className="flex min-h-0 flex-1 flex-col gap-2 px-2 pt-2">
                <Suspense fallback={null}>
                    <SidebarTagsSection onNavigate={onNavigate} />
                </Suspense>
                <Suspense fallback={null}>
                    <SidebarFavoritesSection onNavigate={onNavigate} />
                </Suspense>
                <div className="flex min-h-0 flex-1 flex-col">
                    <Suspense fallback={null}>
                        <SidebarConversationList onNavigate={onNavigate} />
                    </Suspense>
                </div>
            </div>

            <hr className="border-border" role="presentation" />
            <nav aria-label="Utilities" className="shrink-0 px-2 py-2">
                <ul className="grid grid-cols-2 gap-1">
                    {FOOTER_LINKS.map(({ name, href, icon: Icon, tooltip, external }) => (
                        <li key={name}>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    {external ? (
                                        <a
                                            href={href}
                                            target="_blank"
                                            rel="noreferrer"
                                            onClick={() => onNavigate?.()}
                                            className="flex items-center gap-2 rounded-md px-2 py-1.5 text-[12.5px] text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        >
                                            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                                            <span className="truncate">{name}</span>
                                        </a>
                                    ) : (
                                        <Link
                                            href={href}
                                            onClick={() => onNavigate?.()}
                                            className="flex items-center gap-2 rounded-md px-2 py-1.5 text-[12.5px] text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                        >
                                            <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                                            <span className="truncate">{name}</span>
                                        </Link>
                                    )}
                                </TooltipTrigger>
                                <TooltipContent side="top" align="start">{tooltip}</TooltipContent>
                            </Tooltip>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );
}

export function Sidebar() {
    const { isCollapsed, isMobileOpen, setMobileOpen } = useSidebarUi();

    return (
        <>
            {isCollapsed ? (
                <CollapsedRail />
            ) : (
                <aside
                    aria-label="Primary"
                    className={cn(
                        "hidden w-72 shrink-0 border-r bg-(--sidebar-surface) md:flex md:flex-col"
                    )}
                >
                    <SidebarContent />
                </aside>
            )}

            {isMobileOpen && (
                <div
                    className="fixed inset-0 z-40 flex md:hidden"
                    role="dialog"
                    aria-modal="true"
                    aria-label="Navigation"
                >
                    <button
                        type="button"
                        aria-label="Close navigation overlay"
                        className="absolute inset-0 bg-foreground/40 backdrop-blur-sm"
                        onClick={() => setMobileOpen(false)}
                    />
                    <aside className="relative flex h-full w-72 max-w-[85vw] flex-col border-r bg-(--sidebar-surface) shadow-xl">
                        <button
                            type="button"
                            aria-label="Close navigation"
                            className="absolute right-2 top-2 z-10 inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                            onClick={() => setMobileOpen(false)}
                        >
                            <X className="h-4 w-4" aria-hidden="true" />
                        </button>
                        <SidebarContent onNavigate={() => setMobileOpen(false)} />
                    </aside>
                </div>
            )}
        </>
    );
}
