"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useConversations } from "@/hooks/useConversations";
import { ConversationCard } from "@/components/conversations/ConversationCard";
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
import { ArrowUpDown, Download, X } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/services/api";
import type { SortField, SortOrder, ExportFormat } from "@/types";

const PAGE_SIZE = 20;

const EXPORT_FORMATS: { value: ExportFormat; label: string }[] = [
  { value: "md", label: "Markdown" },
  { value: "json", label: "JSON" },
  { value: "yaml", label: "YAML" },
  { value: "html", label: "HTML" },
  { value: "csv", label: "CSV" },
  { value: "xlsx", label: "Excel" },
];

export default function ConversationsPage() {
  const searchParams = useSearchParams();
  const tagFilter = searchParams.get("tag") || undefined;

  const [sortBy, setSortBy] = useState<SortField>("date");
  const [order, setOrder] = useState<SortOrder>("desc");
  const [offset, setOffset] = useState(0);
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isExporting, setIsExporting] = useState(false);

  const { data, isLoading, error, refetch } = useConversations({
    sortBy,
    order,
    limit: PAGE_SIZE,
    offset,
    tag: tagFilter,
  });

  const handleSelectChange = (id: string, selected: boolean) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (selected) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (!data) return;
    const allIds = data.items.map((c) => c.id);
    const allSelected = allIds.every((id) => selectedIds.has(id));
    if (allSelected) {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        allIds.forEach((id) => next.delete(id));
        return next;
      });
    } else {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        allIds.forEach((id) => next.add(id));
        return next;
      });
    }
  };

  const handleCancelSelect = () => {
    setSelectMode(false);
    setSelectedIds(new Set());
  };

  const handleBatchExport = async (format: ExportFormat) => {
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Conversations</h1>
        <div className="flex items-center gap-2">
          {selectMode ? (
            <>
              <div className="flex items-center gap-2 mr-2">
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
                onValueChange={(v) => handleBatchExport(v as ExportFormat)}
                disabled={selectedIds.size === 0 || isExporting}
              >
                <SelectTrigger className="w-[140px]">
                  <Download className="h-4 w-4 mr-2" />
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
              <Button variant="ghost" size="icon" onClick={handleCancelSelect}>
                <X className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectMode(true)}
              >
                Select
              </Button>
              <Select value={sortBy} onValueChange={(v) => { setSortBy(v as SortField); setOffset(0); }}>
                <SelectTrigger className="w-[140px]">
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
                title={`Sort ${order === "desc" ? "ascending" : "descending"}`}
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
          <Pagination
            total={data.total}
            offset={data.offset}
            limit={data.limit}
            onPageChange={setOffset}
          />
        </>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4 text-center">
          <p className="text-lg text-muted-foreground">No conversations yet</p>
          <p className="text-sm text-muted-foreground">
            Import a ChatGPT archive to get started
          </p>
          <Link href="/import">
            <Button>Import Archive</Button>
          </Link>
        </div>
      )}
    </div>
  );
}
