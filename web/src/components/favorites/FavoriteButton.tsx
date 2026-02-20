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
    const [optimisticFavorite, setOptimisticFavorite] = useState<boolean | null>(null);
    const { mutateAsync: toggleFavorite, isPending: isToggling } = useToggleFavorite();
    const effectiveFavorite = optimisticFavorite ?? isFavorite;

    const handleClick = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        // Optimistic update
        const newState = !effectiveFavorite;
        setOptimisticFavorite(newState);

        try {
            await toggleFavorite(conversationId);
            onToggle?.(newState);
            setOptimisticFavorite(null);
        } catch {
            setOptimisticFavorite(null);
        }
    };

    return (
        <Button
            variant="ghost"
            size={size}
            onClick={handleClick}
            disabled={isToggling}
            className={cn("shrink-0", className)}
            aria-label={effectiveFavorite ? "Remove from favorites" : "Add to favorites"}
        >
            <Star
                className={cn(
                    "h-4 w-4 transition-colors",
                    effectiveFavorite
                        ? "text-yellow-500 fill-yellow-500"
                        : "text-muted-foreground"
                )}
            />
        </Button>
    );
}
