# Code Review Fix Plan: Spec 002 Web UI

**Date**: 2026-02-13  
**Scope**: Critical bugs and API mismatches in completed tasks  
**Priority**: Must fix before continuing implementation

---

## Summary

Code review identified **5 critical issues** that will cause runtime failures:
- 1 corrupted file (syntax errors)
- 4 API method name mismatches between hooks and API client

These issues affect tasks marked as completed and must be fixed before proceeding.

---

## Issue Details

### Issue 1: Corrupted queryKeys.ts

**File**: `web/src/hooks/queryKeys.ts`  
**Severity**: Critical (TypeScript won't compile)  
**Task Affected**: T020

**Problem**: Lines 26-33 contain duplicate/corrupted content appended after the object closes:
```typescript
// After line 25 (correct closing), there's garbage:
all: ["settings"] as const,
  },
embeddings: {
    estimate: (model?: string) => ["embeddings", "estimate", model] as const,
  },
} as const ;
```

**Fix**: Remove lines 26-33, keeping only the valid object (lines 1-25).

---

### Issue 2: useSearch hook calls wrong API method

**File**: `web/src/hooks/useSearch.ts`  
**Severity**: Critical (runtime error)  
**Task Affected**: T074

**Problem**: Hook calls `api.searchConversations()` but API client has `api.search()`.

**Current** (line 10):
```typescript
queryFn: () => api.searchConversations(searchFilters),
```

**Fix**: Change to:
```typescript
queryFn: () => api.search({
    query: searchFilters.query,
    fromDate: searchFilters.fromDate,
    toDate: searchFilters.toDate,
    limit: searchFilters.limit,
    searchType: searchFilters.searchType,
}),
```

---

### Issue 3: useFavorites hooks call non-existent methods

**File**: `web/src/hooks/useFavorites.ts`  
**Severity**: Critical (runtime error)  
**Tasks Affected**: T113

**Problem**: Hook calls `api.addFavorite()` and `api.removeFavorite()` but API client only has `api.toggleFavorite()`.

**Current**:
```typescript
// Line 15
mutationFn: (id: string) => api.addFavorite(id),
// Line 25
mutationFn: (id: string) => api.removeFavorite(id),
```

**Fix**: Replace `useAddFavorite` and `useRemoveFavorite` with single `useToggleFavorite`:
```typescript
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
```

---

### Issue 4: ExportDialog calls non-existent API method

**File**: `web/src/components/export/ExportDialog.tsx`  
**Severity**: Critical (runtime error)  
**Task Affected**: T091

**Problem**: Component calls `api.exportConversation()` but API client only has `api.getExportUrl()` which returns a URL string.

**Current** (line 48):
```typescript
const blob = await api.exportConversation(conversationId, format);
```

**Fix Options**:

**Option A** - Use direct link download (simpler):
```typescript
const handleExport = () => {
    const formatMap: Record<ExportFormat, string> = {
        markdown: "md", json: "json", html: "html",
        csv: "csv", yaml: "yaml", xml: "xml", excel: "xlsx"
    };
    const url = api.getExportUrl(conversationId, formatMap[format] as ExportFormat);
    window.open(url, "_blank");
    toast.success("Export started");
    onOpenChange(false);
};
```

**Option B** - Add exportConversation method to API client:
```typescript
async exportConversation(conversationId: string, format: string): Promise<Blob> {
    const res = await fetch(this.getExportUrl(conversationId, format as ExportFormat));
    if (!res.ok) throw new Error(`Export failed: ${res.status}`);
    return res.blob();
}
```

**Recommendation**: Option B maintains better UX with proper filename handling.

---

### Issue 5: useSettings hooks call non-existent API methods

**File**: `web/src/hooks/useSettings.ts`  
**Severity**: Critical (runtime error)  
**Task Affected**: T136, T137

**Problem**: Hook calls `api.getSettings()` and `api.updateSettings()` which don't exist in API client.

**Fix**: Add missing methods to `web/src/services/api.ts`:
```typescript
// Settings
async getSettings(): Promise<UserSettings> {
    return this.request("/api/settings");
}

async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    return this.request("/api/settings", {
        method: "PUT",
        body: JSON.stringify(settings),
    });
}
```

**Note**: Also requires settings endpoint in backend API (check if `api/routers/settings.py` exists).

---

## Fix Tasks

| ID | Priority | File | Description |
|----|----------|------|-------------|
| FIX-001 | P0 | `web/src/hooks/queryKeys.ts` | Remove corrupted duplicate lines 26-33 |
| FIX-002 | P0 | `web/src/hooks/useSearch.ts` | Change `searchConversations` to `search` with correct params |
| FIX-003 | P0 | `web/src/hooks/useFavorites.ts` | Replace add/remove hooks with single `useToggleFavorite` |
| FIX-004 | P0 | `web/src/components/export/ExportDialog.tsx` | Fix export to use URL or add API method |
| FIX-005 | P0 | `web/src/services/api.ts` | Add `exportConversation` method returning Blob |
| FIX-006 | P1 | `web/src/services/api.ts` | Add `getSettings` and `updateSettings` methods |
| FIX-007 | P1 | `api/routers/` | Verify settings router exists or create it |

---

## Minor Issues (Non-Blocking)

| File | Line | Issue | Suggestion |
|------|------|-------|------------|
| `web/src/app/search/page.tsx` | 74 | Tailwind lint: `w-[140px]` | Change to `w-35` |
| `web/src/app/page.tsx` | 48 | Tailwind lint: `w-[140px]` | Change to `w-35` |
| `web/src/app/search/page.tsx` | 109 | Implicit `any` type on result | Add type annotation |
| `web/src/hooks/useSSE.ts` | 60 | Type comparison never true | Update ProgressStatus type |

---

## Execution Order

1. **FIX-001**: Fix queryKeys.ts first (blocks all React Query usage)
2. **FIX-002**: Fix useSearch.ts (search page breaks)
3. **FIX-003**: Fix useFavorites.ts (favorites feature breaks)
4. **FIX-004 + FIX-005**: Fix export (export feature breaks)
5. **FIX-006 + FIX-007**: Add settings API (settings page breaks)

---

## Verification

After fixes, run:
```bash
cd web && npm run build
```

All TypeScript errors should resolve. Then test:
1. Conversation list loads
2. Search works
3. Export downloads file
4. Favorites toggle works
