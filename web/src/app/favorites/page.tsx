"use client";

import { useFavorites } from "@/hooks/useFavorites";
import { ConversationCard } from "@/components/conversations/ConversationCard";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export default function FavoritesPage() {
  const { data, isLoading, error } = useFavorites();

  if (isLoading) {
    return <LoadingSpinner className="min-h-[40vh]" />;
  }

  if (error) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <p className="text-destructive">Failed to load favorites</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Favorites</h1>
      {data && data.items.length > 0 ? (
        <div className="grid gap-3">
          {data.items.map((conversation) => (
            <ConversationCard key={conversation.id} conversation={conversation} />
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">No favorites yet.</p>
      )}
    </div>
  );
}
