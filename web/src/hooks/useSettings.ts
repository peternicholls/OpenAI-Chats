import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "./queryKeys";
import type { UserSettings } from "@/types";

export function useSettings() {
    return useQuery({
        queryKey: queryKeys.settings.all,
        queryFn: () => api.getSettings(),
    });
}

export function useUpdateSettings() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (settings: Partial<UserSettings>) => api.updateSettings(settings),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.settings.all });
        },
    });
}
