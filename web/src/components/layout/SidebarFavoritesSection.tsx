"use client";

import { Star } from "lucide-react";
import { useFavorites } from "@/hooks/useFavorites";
import { CollapsibleSection } from "@/components/layout/CollapsibleSection";
import { SidebarConversationList } from "@/components/layout/SidebarConversationList";

export function SidebarFavoritesSection({ onNavigate }: { onNavigate?: () => void } = {}) {
    const { data } = useFavorites();
    const items = data?.items ?? [];

    if (items.length === 0) {
        return null;
    }

    return (
        <CollapsibleSection
            sectionId="favorites"
            title="Favourites"
            icon={<Star className="h-3.5 w-3.5 text-yellow-500" aria-hidden="true" />}
            count={items.length}
            defaultOpen={false}
        >
            <div className="max-h-60 overflow-y-auto">
                <SidebarConversationList
                    items={items}
                    hideOrderToggle
                    compact
                    ariaLabel="Favourite conversations"
                    emptyMessage="No favourites yet."
                    onNavigate={onNavigate}
                />
            </div>
        </CollapsibleSection>
    );
}
