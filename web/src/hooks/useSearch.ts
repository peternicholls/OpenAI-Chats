import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { queryKeys } from "./queryKeys";
import type { SearchFilters } from "@/types";

export function useSearch(filters: SearchFilters & { enabled?: boolean }) {
    const { enabled = true, ...searchFilters } = filters;
    return useQuery({
        queryKey: queryKeys.search.results(searchFilters),
        queryFn: () => api.search({
            query: searchFilters.query,
            fromDate: searchFilters.fromDate,
            toDate: searchFilters.toDate,
            limit: searchFilters.limit,
            offset: searchFilters.offset,
            searchType: searchFilters.searchType,
        }),
        enabled: enabled && !!searchFilters.query,
        staleTime: 30_000,
    });
}
