import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { SidebarConversationList } from "@/components/layout/SidebarConversationList";
import type { Conversation } from "@/types";

const useConversationsMock = vi.fn();
const useParamsMock = vi.fn();
const useSearchParamsMock = vi.fn();

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
    useConversations: (filters: unknown) => useConversationsMock(filters),
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
        useParamsMock.mockReset();
        useSearchParamsMock.mockReset();
        useConversationsMock.mockReset();

        useParamsMock.mockReturnValue({ id: "conv-1" });
        useSearchParamsMock.mockReturnValue({ get: vi.fn().mockReturnValue(null) });
        useConversationsMock.mockReturnValue({
            data: { items: [mockConversation], total: 1, offset: 0, limit: 100 },
            isLoading: false,
        });
    });

    it("requests conversations with an API-safe limit", () => {
        render(<SidebarConversationList />);

        expect(useConversationsMock).toHaveBeenCalledWith({
            sortBy: "date",
            order: "desc",
            limit: 100,
            tag: undefined,
        });
    });

    it("toggles ordering for the sidebar list", () => {
        render(<SidebarConversationList />);

        fireEvent.click(screen.getByRole("button", { name: "Sort oldest first" }));

        expect(useConversationsMock).toHaveBeenLastCalledWith({
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
});