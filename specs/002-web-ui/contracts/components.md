# Frontend Component Architecture

**Feature**: 002-web-ui  
**Date**: 2026-02-12  
**Framework**: Next.js 14+ with App Router, React Server Components

---

## Overview

This document defines the component architecture for the Web UI. Components are built using:
- **Next.js App Router**: File-based routing, Server Components by default
- **shadcn/ui + Tailwind CSS**: Consistent design system
- **TypeScript**: Type-safe component props
- **React Server Components**: Server-side rendering where possible, client components only when needed

---

## Component Hierarchy

```
App (Layout)
├── Header
│   ├── Logo
│   ├── SearchBar (client)
│   └── UserMenu
├── Sidebar
│   ├── Navigation
│   └── TagFilter (client)
└── PageContent
    ├── ConversationList (page)
    │   ├── ConversationCard (server)
    │   └── Pagination (client)
    ├── ConversationView (page)
    │   ├── ConversationHeader
    │   ├── MessageList
    │   │   └── MessageBubble (server)
    │   └── ExportDialog (client)
    ├── SearchPage (page)
    │   ├── SearchBar (client)
    │   ├── SearchFilters (client)
    │   └── SearchResults (server)
    ├── ImportPage (page)
    │   └── ImportDialog (client)
    └── SettingsPage (page)
        └── SettingsForm (client)
```

---

## Core Components

### Layout Components

#### `app/layout.tsx` (Root Layout)
**Type**: Server Component  
**Purpose**: Top-level layout with header, sidebar, and content area

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Header />
            <main className="flex-1 overflow-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
```

**Props**: N/A (layout wrapper)

---

#### `Header.tsx`
**Type**: Server Component (with client search bar)  
**Purpose**: Top navigation bar with logo, search, and user menu

**Props**:
```typescript
interface HeaderProps {
  // No props - uses server-side auth/context if added later
}
```

**Features**:
- Logo/branding
- Global search bar (client component)
- Settings/info menu

---

#### `Sidebar.tsx`
**Type**: Client Component (interactive navigation)  
**Purpose**: Side navigation with links and tag filters

**Props**:
```typescript
interface SidebarProps {
  defaultOpen?: boolean;
}
```

**Features**:
- Navigation links (Home, Search, Import, Settings)
- Tag list with counts (clickable filters)
- Collapse/expand toggle

**State**:
- `isOpen: boolean` (controlled via localStorage)

---

### Conversation Components

#### `ConversationList.tsx`
**Type**: Server Component  
**Purpose**: List of conversations with pagination

**Props**:
```typescript
interface ConversationListProps {
  searchParams: {
    sort_by?: string;
    order?: string;
    offset?: string;
    tag?: string;
  };
}
```

**Data Fetching**:
```typescript
const conversations = await fetchConversations(searchParams);
```

**Features**:
- Server-side data fetch
- Renders `ConversationCard` for each item
- Pagination controls (client component)

---

#### `ConversationCard.tsx`
**Type**: Server Component  
**Purpose**: Display conversation summary

**Props**:
```typescript
interface ConversationCardProps {
  conversation: ConversationSummary;
}
```

**Features**:
- Title, date, message count
- Tag badges
- Click to navigate to detail view

**Styling**:
```tsx
<Card className="hover:shadow-lg transition-shadow">
  <CardHeader>
    <CardTitle>{conversation.title || '[Untitled]'}</CardTitle>
    <CardDescription>
      {formatDate(conversation.create_time)} • {conversation.message_count} messages
    </CardDescription>
  </CardHeader>
  <CardContent>
    <div className="flex gap-2">
      {conversation.tags.map(tag => <Badge key={tag}>{tag}</Badge>)}
    </div>
  </CardContent>
</Card>
```

---

#### `ConversationView.tsx`
**Type**: Server Component (page)  
**Purpose**: Display full conversation with messages

**Props**:
```typescript
interface ConversationViewProps {
  params: {
    id: string;
  };
}
```

**Data Fetching**:
```typescript
const conversation = await fetchConversationById(params.id);
```

**Features**:
- Conversation header (title, date, model, tags)
- Message list (scrollable)
- Export button (opens dialog)
- Delete button (with confirmation)

---

#### `MessageBubble.tsx`
**Type**: Server Component  
**Purpose**: Display single message

**Props**:
```typescript
interface MessageBubbleProps {
  message: Message;
}
```

**Features**:
- Different styling for user/assistant/system
- Timestamp
- Content with code syntax highlighting (if applicable)

**Styling**:
```tsx
<div className={cn(
  "flex gap-3 p-4 rounded-lg",
  message.role === 'user' ? "bg-blue-50" : "bg-gray-50"
)}>
  <div className="flex-shrink-0">
    <Avatar role={message.role} />
  </div>
  <div className="flex-1">
    <div className="font-semibold">{message.role}</div>
    <div className="prose">{message.content}</div>
  </div>
</div>
```

---

### Search Components

#### `SearchBar.tsx`
**Type**: Client Component  
**Purpose**: Search input with debounce

**Props**:
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  defaultValue?: string;
}
```

**Features**:
- Debounced input (500ms)
- Loading indicator
- Clear button

**State**:
```typescript
const [query, setQuery] = useState(defaultValue || '');
const debouncedQuery = useDebounce(query, 500);

useEffect(() => {
  if (debouncedQuery) {
    onSearch(debouncedQuery);
  }
}, [debouncedQuery]);
```

---

#### `SearchFilters.tsx`
**Type**: Client Component  
**Purpose**: Advanced search filters (date range, search type)

**Props**:
```typescript
interface SearchFiltersProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
}
```

**Features**:
- Date range picker
- Search type selector (keyword/semantic/hybrid)
- Tag multi-select

---

#### `SearchResults.tsx`
**Type**: Server Component  
**Purpose**: Display search results

**Props**:
```typescript
interface SearchResultsProps {
  results: SearchResult[];
  total: number;
}
```

**Features**:
- Result cards with preview snippets
- Highlighting of matched terms
- Click to view full conversation

---

### Import/Export Components

#### `ImportDialog.tsx`
**Type**: Client Component  
**Purpose**: File upload for archive import

**Props**: None (modal/dialog)

**Features**:
- File input (ZIP or directory selection in Docker context)
- Upload progress bar
- Status messages

**State**:
```typescript
const [isUploading, setIsUploading] = useState(false);
const [progress, setProgress] = useState<ImportProgress | null>(null);

// Poll /api/import/progress while importing
useEffect(() => {
  if (isUploading) {
    const interval = setInterval(async () => {
      const progress = await fetchImportProgress();
      setProgress(progress);
      if (progress.status === 'complete' || progress.status === 'error') {
        setIsUploading(false);
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }
}, [isUploading]);
```

---

#### `ExportDialog.tsx`
**Type**: Client Component  
**Purpose**: Export format selection and download

**Props**:
```typescript
interface ExportDialogProps {
  conversationId: string;
}
```

**Features**:
- Format selector (dropdown)
- Export button
- Triggers file download

**Implementation**:
```typescript
const handleExport = async (format: ExportFormat) => {
  const url = `/api/conversations/${conversationId}/export?format=${format}`;
  // Trigger browser download
  window.location.href = url;
};
```

---

### Tag Components

#### `TagList.tsx`
**Type**: Server Component  
**Purpose**: Display all tags with counts

**Props**: None (fetches data server-side)

**Features**:
- Tag badges with counts
- Click to filter conversations

---

#### `TagEditor.tsx`
**Type**: Client Component  
**Purpose**: Add/remove tags on a conversation

**Props**:
```typescript
interface TagEditorProps {
  conversationId: string;
  existingTags: string[];
  allTags: string[];  // For autocomplete
}
```

**Features**:
- Tag input with autocomplete
- Remove tag button (X on badge)
- Optimistic updates

---

### Common/Shared Components

All common components use **shadcn/ui** primitives:

#### `Button.tsx` (shadcn)
- Variants: default, destructive, outline, ghost, link
- Sizes: sm, md, lg

#### `Card.tsx` (shadcn)
- `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`

#### `Dialog.tsx` (shadcn)
- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`

#### `Input.tsx` (shadcn)
- Text input with validation states

#### `Badge.tsx` (shadcn)
- Tag/label badges

#### `LoadingSpinner.tsx` (custom)
- Centered loading indicator

#### `Pagination.tsx` (shadcn + custom)
- Previous/Next buttons, page numbers

---

## Server vs Client Components

### Server Components (default)
Use for:
- Data fetching
- Static content
- Layout components
- No user interaction

**Benefits**:
- Smaller client bundle
- Direct database/API access
- SEO-friendly

### Client Components
Use `'use client'` directive for:
- Event handlers (onClick, onChange)
- State (useState, useReducer)
- Effects (useEffect)
- Browser APIs

**Examples**:
- SearchBar (debounced input)
- Sidebar (collapse state)
- ImportDialog (upload progress)
- ExportDialog (format selection)

---

## Data Fetching Patterns

### Server Components
```typescript
// app/page.tsx
export default async function ConversationsPage({ searchParams }) {
  const conversations = await fetchConversations(searchParams);
  
  return <ConversationList conversations={conversations} />;
}
```

### Client Components with React Query
```typescript
// components/SearchBar.tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function SearchResults({ query }) {
  const { data, isLoading } = useQuery({
    queryKey: ['search', query],
    queryFn: () => searchConversations(query),
  });
  
  if (isLoading) return <LoadingSpinner />;
  return <div>{/* results */}</div>;
}
```

---

## Styling Conventions

### Tailwind Utilities
- Spacing: `p-4`, `m-2`, `gap-3`
- Layout: `flex`, `grid`, `flex-col`
- Responsive: `md:flex-row`, `lg:grid-cols-3`
- Colors: Use theme colors (`bg-primary`, `text-muted-foreground`)

### shadcn/ui Theming
Configure in `tailwind.config.ts`:
```typescript
theme: {
  extend: {
    colors: {
      border: "hsl(var(--border))",
      background: "hsl(var(--background))",
      foreground: "hsl(var(--foreground))",
      // ... shadcn color palette
    },
  },
}
```

---

## Accessibility

All components follow WCAG 2.1 AA standards:
- **Keyboard navigation**: All interactive elements focusable
- **ARIA labels**: Descriptive labels for screen readers
- **Color contrast**: Minimum 4.5:1 ratio
- **Focus indicators**: Visible focus styles

**Example**:
```tsx
<button
  aria-label="Export conversation"
  className="focus:ring-2 focus:ring-offset-2"
>
  Export
</button>
```

---

## Error Handling

Use React Error Boundaries for graceful error handling:

```tsx
// app/error.tsx (Next.js convention)
'use client';

export default function Error({ error, reset }) {
  return (
    <div className="p-4">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

## Summary

- **Server-first**: Use Server Components by default, Client only when needed
- **shadcn/ui**: Provides consistent, accessible component library
- **Tailwind CSS**: Utility-first styling for rapid development
- **Type-safe**: All props defined with TypeScript interfaces
- **Accessible**: WCAG 2.1 AA compliance throughout
- **Responsive**: Mobile-first design with Tailwind breakpoints
