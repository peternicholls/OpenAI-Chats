"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useConversations } from "@/hooks/useConversations";
import { useSettings } from "@/hooks/useSettings";
import { ConversationCard } from "@/components/conversations/ConversationCard";
import { VirtualizedConversationList } from "@/components/conversations/VirtualizedConversationList";
import { Pagination } from "@/components/common/Pagination";
import { ConversationListSkeleton } from "@/components/conversations/ConversationListSkeleton";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowUpDown, Download, MessagesSquare, Search, Sparkles, Upload, X, List } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/services/api";
import type { SortField, SortOrder, ExportFormatCode } from "@/types";

const VIRTUALIZATION_THRESHOLD = 100;
const DEFAULT_PAGE_SIZE = Number(process.env.NEXT_PUBLIC_PAGE_SIZE) || 20;

const EXPORT_FORMATS: { value: ExportFormatCode; label: string }[] = [
    { value: "md", label: "Markdown" },
    { value: "json", label: "JSON" },
    { value: "yaml", label: "YAML" },
    { value: "html", label: "HTML" },
    { value: "csv", label: "CSV" },
    { value: "xlsx", label: "Excel" },
];

function WelcomeScreen() {
    return (
        <section
            aria-labelledby="welcome-heading"
            className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center gap-6 text-center"
        >
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <MessagesSquare className="h-8 w-8" aria-hidden="true" />
            </div>
            <div className="space-y-2">
                <h1 id="welcome-heading" className="text-2xl font-semibold tracking-tight">
                    Pick up where you left off
                </h1>
                <p className="text-sm text-muted-foreground">
                    Choose a conversation from the sidebar, search across your archive, or
                    import a fresh ChatGPT export to get started.
                </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-2">
                <Link href="/search">
                    <Button variant="outline" size="sm">
                        <Search className="mr-2 h-4 w-4" aria-hidden="true" />
                        Search archive
                    </Button>
                </Link>
                <Link href="/favorites">
                    <Button variant="outline" size="sm">
                        <Sparkles className="mr-2 h-4 w-4" aria-hidden="true" />
                        Favourites
                    </Button>
                </Link>
                <Link href="/?manage=1">
                    <Button variant="outline" size="sm">
                        <Download className="mr-2 h-4 w-4" aria-hidden="true" />
                        Bulk export
                    </Button>
                </Link>
                <Link href="/import">
                    <Button variant="default" size="sm">
                        <Upload className="mr-2 h-4 w-4" aria-hidden="true" />
                        Import
                    </Button>
                </Link>
            </div>
        </section>
    );
}

function ConversationsManagement() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const tagFilter = searchParams.get("tag") || undefined;

    const { data: settings } = useSettings();
    const pageSize = settings?.items_per_page ?? DEFAULT_PAGE_SIZE;

    const [sortBy, setSortBy] = useState<SortField>("date");
    const [order, setOrder] = useState<SortOrder>("desc");
    const [offset, setOffset] = useState(0);
    const [selectMode, setSelectMode] = useState(false);
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const [isExporting, setIsExporting] = useState(false);
    const [viewAllMode, setViewAllMode] = useState(false);

    const effectiveLimit = viewAllMode ? 10000 : pageSize;
    const effectiveOffset = viewAllMode ? 0 : offset;

    const { data, isLoading, error, refetch } = useConversations({
        sortBy,
        order,
        limit: effectiveLimit,
        offset: effectiveOffset,
        tag: tagFilter,
    });

    const handleSelectChange = (id: string, selected: boolean) => {
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (selected) next.add(id);
            else next.delete(id);
            return next;
        });
    };

    const handleSelectAll = () => {
        if (!data) return;
        const allIds = data.items.map((c) => c.id);
        const allSelected = allIds.every((id) => selectedIds.has(id));
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (allSelected) allIds.forEach((id) => next.delete(id));
            else allIds.forEach((id) => next.add(id));
            return next;
        });
    };

    const handleCancelSelect = () => {
        setSelectMode(false);
        setSelectedIds(new Set());
    };

    const handleBatchExport = async (format: ExportFormatCode) => {
        if (selectedIds.size === 0) return;
        setIsExporting(true);
        try {
            const blob = await api.exportBatch(Array.from(selectedIds), format);
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `export_${selectedIds.size}_conversations.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            toast.success(`Exported ${selectedIds.size} conversations`);
            handleCancelSelect();
        } catch (err) {
            const message = err instanceof Error ? err.message : "Export failed";
            toast.error(message);
        } finally {
            setIsExporting(false);
        }
    };

    if (error) {
        const message = (error as Error).message;
        const isNetworkError =
            message.toLowerCase().includes("fetch") ||
            message.toLowerCase().includes("network");

        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
                <p className="text-destructive">
                    {isNetworkError
                        ? "Network error while loading conversations"
                        : "Failed to load conversations"}
                </p>
                <p className="text-sm text-muted-foreground text-center max-w-md">{message}</p>
                <Button onClick={() => refetch()} variant="outline">
                    Retry
                </Button>
            </div>
        );
    }

    const allOnPageSelected = data?.items.every((c) => selectedIds.has(c.id)) ?? false;

    return (
        <div>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
                <div>
                    <h1 className="text-2xl font-bold">
                        {tagFilter ? `Tagged: ${tagFilter}` : "All conversations"}
                    </h1>
                    {tagFilter && (
                        <button
                            type="button"
                            onClick={() => router.push("/?manage=1")}
                            className="mt-1 inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                        >
                            <X className="h-3 w-3" aria-hidden="true" /> Clear tag filter
                        </button>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {selectMode ? (
                        <>
                            <div className="mr-2 flex items-center gap-2">
                                <Checkbox
                                    checked={allOnPageSelected && data && data.items.length > 0}
                                    onCheckedChange={() => handleSelectAll()}
                                    aria-label="Select all on page"
                                />
                                <span className="text-sm text-muted-foreground">
                                    {selectedIds.size} selected
                                </span>
                            </div>
                            <Select
                                value=""
                                onValueChange={(v) => handleBatchExport(v as ExportFormatCode)}
                                disabled={selectedIds.size === 0 || isExporting}
                            >
                                <SelectTrigger className="w-35">
                                    <Download className="mr-2 h-4 w-4" aria-hidden="true" />
                                    <SelectValue placeholder="Export" />
                                </SelectTrigger>
                                <SelectContent>
                                    {EXPORT_FORMATS.map((f) => (
                                        <SelectItem key={f.value} value={f.value}>
                                            {f.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <Button variant="ghost" size="icon" onClick={handleCancelSelect} aria-label="Cancel selection">
                                <X className="h-4 w-4" />
                            </Button>
                        </>
                    ) : (
                        <>
                            {data && data.total > VIRTUALIZATION_THRESHOLD && (
                                <Button
                                    variant={viewAllMode ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => {
                                        setViewAllMode(!viewAllMode);
                                        setOffset(0);
                                    }}
                                    title={viewAllMode ? "Switch to paginated view" : "View all (virtualized)"}
                                >
                                    <List className="mr-1 h-4 w-4" aria-hidden="true" />
                                    {viewAllMode ? "Pages" : "All"}
                                </Button>
                            )}
                            <Button variant="outline" size="sm" onClick={() => setSelectMode(true)}>
                                Select
                            </Button>
                            <Select value={sortBy} onValueChange={(v) => { setSortBy(v as SortField); setOffset(0); }}>
                                <SelectTrigger className="w-35">
                                    <SelectValue placeholder="Sort by" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="date">Date</SelectItem>
                                    <SelectItem value="title">Title</SelectItem>
                                    <SelectItem value="messages">Messages</SelectItem>
                                </SelectContent>
                            </Select>
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={() => setOrder(order === "desc" ? "asc" : "desc")}
                                aria-label={`Sort ${order === "desc" ? "ascending" : "descending"}`}
                            >
                                <ArrowUpDown className="h-4 w-4" />
                            </Button>
                        </>
                    )}
                </div>
            </div>

            {isLoading ? (
                <ConversationListSkeleton />
            ) : data && data.items.length > 0 ? (
                <>
                    {viewAllMode && data.items.length > VIRTUALIZATION_THRESHOLD ? (
                        <VirtualizedConversationList
                            conversations={data.items}
                            selectable={selectMode}
                            selectedIds={selectedIds}
                            onSelectChange={handleSelectChange}
                        />
                    ) : (
                        <>
                            <div className="grid gap-3">
                                {data.items.map((conversation) => (
                                    <ConversationCard
                                        key={conversation.id}
                                        conversation={conversation}
                                        selectable={selectMode}
                                        isSelected={selectedIds.has(conversation.id)}
                                        onSelectChange={handleSelectChange}
                                    />
                                ))}
                            </div>
                            {!viewAllMode && (
                                <Pagination
                                    total={data.total}
                                    offset={data.offset}
                                    limit={data.limit}
                                    onPageChange={setOffset}
                                />
                            )}
                        </>
                    )}
                </>
            ) : (
                <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 text-center">
                    <p className="text-lg text-muted-foreground">No conversations yet</p>
                    <p className="text-sm text-muted-foreground">
                        Import a ChatGPT archive to get started
                    </p>
                    <Link href="/import">
                        <Button>Import archive</Button>
                    </Link>
                </div>
            )}
        </div>
    );
}

function HomeContent() {
    const searchParams = useSearchParams();
    const showManagement =
        searchParams.get("manage") === "1" || Boolean(searchParams.get("tag"));

    if (showManagement) {
        return <ConversationsManagement />;
    }

    return <WelcomeScreen />;
}

export default function ConversationsPage() {
    return (
        <Suspense fallback={<ConversationListSkeleton />}>
            <HomeContent />
        </Suspense>
    );
}
