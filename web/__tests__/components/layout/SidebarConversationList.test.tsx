import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SidebarConversationList } from "@/components/layout/SidebarConversationList";
import type { Conversation } from "@/types";

const useInfiniteConversationsMock = vi.fn();
const useParamsMock = vi.fn();
const useSearchParamsMock = vi.fn();
const observeMock = vi.fn();
const disconnectMock = vi.fn();
let intersectionCallback: ((entries: Array<{ isIntersecting: boolean }>) => void) | null = null;

vi.mock("next/link", () => ({
    default: ({ children, href, onClick, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
        <a
            href={href}
            onClick={(event) => {
                event.preventDefault();
                onClick?.(event);
            }}
            {...props}
        >
            {children}
        </a>
    ),
}));

vi.mock("next/navigation", () => ({
    useParams: () => useParamsMock(),
    useSearchParams: () => useSearchParamsMock(),
}));

vi.mock("@/hooks/useConversations", () => ({
    useInfiniteConversations: (filters: unknown) => useInfiniteConversationsMock(filters),
}));

vi.mock("@/components/ui/tooltip", () => ({
    Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipContent: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const mockConversation: Conversation = {
    id: "conv-1",
    title: "Sidebar Item",
    create_time: 1700000000,
    update_time: 1700000100,
    message_count: 12,
    model: "gpt-4",
    tags: [],
    is_favorite: false,
};

describe("SidebarConversationList", () => {
    beforeEach(() => {
        intersectionCallback = null;
        useParamsMock.mockReset();
        useSearchParamsMock.mockReset();
        useInfiniteConversationsMock.mockReset();
        observeMock.mockReset();
        disconnectMock.mockReset();

        vi.stubGlobal(
            "IntersectionObserver",
            vi.fn((callback: typeof intersectionCallback) => {
                intersectionCallback = callback;
                return {
                    observe: observeMock,
                    disconnect: disconnectMock,
                    unobserve: vi.fn(),
                    takeRecords: vi.fn(),
                    root: null,
                    rootMargin: "",
                    thresholds: [],
                };
            })
        );

        useParamsMock.mockReturnValue({ id: "conv-1" });
        useSearchParamsMock.mockReturnValue({ get: vi.fn().mockReturnValue(null) });
        useInfiniteConversationsMock.mockReturnValue({
            data: { pages: [{ items: [mockConversation], total: 1, offset: 0, limit: 100 }] },
            isLoading: false,
            isFetchingNextPage: false,
            hasNextPage: false,
            fetchNextPage: vi.fn(),
        });
    });

    it("requests conversations with an API-safe limit", () => {
        render(<SidebarConversationList />);

        expect(useInfiniteConversationsMock).toHaveBeenCalledWith({
            sortBy: "date",
            order: "desc",
            limit: 100,
            tag: undefined,
        });
    });

    it("toggles ordering for the sidebar list", () => {
        render(<SidebarConversationList />);

        fireEvent.click(screen.getByRole("button", { name: "Sorted newest first" }));

        expect(useInfiniteConversationsMock).toHaveBeenLastCalledWith({
            sortBy: "date",
            order: "asc",
            limit: 100,
            tag: undefined,
        });
    });

    it("calls onNavigate when a conversation link is activated", () => {
        const onNavigate = vi.fn();

        render(<SidebarConversationList onNavigate={onNavigate} />);

        fireEvent.click(screen.getByRole("link", { name: /sidebar item/i }));

        expect(onNavigate).toHaveBeenCalledTimes(1);
    });

    it("renders custom hover details for conversation items instead of a native title tooltip", () => {
        render(<SidebarConversationList />);

        const link = screen.getByRole("link", { name: /sidebar item/i });

        expect(link).not.toHaveAttribute("title");
        expect(screen.getAllByText(/Nov 14, 2023/)).toHaveLength(2);
        expect(
            screen.getByText((_, element) => element?.textContent === "Nov 14, 2023 · 12 messages")
        ).toBeInTheDocument();
        expect(
            screen.getByText((_, element) => element?.textContent === "Model: gpt-4")
        ).toBeInTheDocument();
    });

    it("fetches the next page when the load-more sentinel reaches the bottom of the sidebar", async () => {
        const fetchNextPage = vi.fn().mockResolvedValue(undefined);

        useInfiniteConversationsMock.mockReturnValue({
            data: { pages: [{ items: [mockConversation], total: 2, offset: 0, limit: 100 }] },
            isLoading: false,
            isFetchingNextPage: false,
            hasNextPage: true,
            fetchNextPage,
        });

        render(<SidebarConversationList />);

        expect(screen.getByTestId("sidebar-load-more-sentinel")).toBeInTheDocument();
        expect(observeMock).toHaveBeenCalled();

        intersectionCallback?.([{ isIntersecting: true }]);

        await waitFor(() => {
            expect(fetchNextPage).toHaveBeenCalledTimes(1);
        });
    });
});