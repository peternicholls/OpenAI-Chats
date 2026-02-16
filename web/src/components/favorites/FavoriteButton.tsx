"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToggleFavorite } from "@/hooks/useFavorites";
import { cn } from "@/lib/utils";

interface FavoriteButtonProps {
    conversationId: string;
    isFavorite: boolean;
    onToggle?: (newState: boolean) => void;
    size?: "sm" | "default" | "icon";
    className?: string;
}

export function FavoriteButton({
    conversationId,
    isFavorite,
    onToggle,
    size = "icon",
    className,
}: FavoriteButtonProps) {
    const [optimisticFavorite, setOptimisticFavorite] = useState(isFavorite);
    const { mutateAsync: toggleFavorite, isPending: isToggling } = useToggleFavorite();

    // Sync with prop when it changes
    if (isFavorite !== optimisticFavorite && !isToggling) {
        setOptimisticFavorite(isFavorite);
    }

    const handleClick = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        // Optimistic update
        const newState = !optimisticFavorite;
        setOptimisticFavorite(newState);

        try {
            await toggleFavorite(conversationId);
            onToggle?.(newState);
        } catch {
            // Rollback on error
            setOptimisticFavorite(!newState);
        }
    };

    return (
        <Button
            variant="ghost"
            size={size}
            onClick={handleClick}
            disabled={isToggling}
            className={cn("shrink-0", className)}
            aria-label={optimisticFavorite ? "Remove from favorites" : "Add to favorites"}
        >
            <Star
                className={cn(
                    "h-4 w-4 transition-colors",
                    optimisticFavorite
                        ? "text-yellow-500 fill-yellow-500"
                        : "text-muted-foreground"
                )}
            />
        </Button>
    );
}
