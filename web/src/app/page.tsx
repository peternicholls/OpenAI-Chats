"use client";

import { useState } from "react";
import Link from "next/link";
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
import { ArrowUpDown } from "lucide-react";
import type { SortField, SortOrder } from "@/types";

const PAGE_SIZE = 20;

export default function ConversationsPage() {
  const [sortBy, setSortBy] = useState<SortField>("date");
  const [order, setOrder] = useState<SortOrder>("desc");
  const [offset, setOffset] = useState(0);

  const { data, isLoading, error, refetch } = useConversations({
    sortBy,
    order,
    limit: PAGE_SIZE,
    offset,
  });

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

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Conversations</h1>
        <div className="flex items-center gap-2">
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
