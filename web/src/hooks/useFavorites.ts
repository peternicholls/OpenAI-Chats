import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "./queryKeys";

export function useFavorites() {
    return useQuery({
        queryKey: queryKeys.favorites.all,
        queryFn: () => api.listFavorites(),
    });
}

export function useToggleFavorite() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: string) => api.toggleFavorite(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.favorites.all });
            queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all });
        },
    });
}
