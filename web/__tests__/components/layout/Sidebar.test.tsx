import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { Sidebar } from "@/components/layout/Sidebar";

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

vi.mock("@/components/ui/tooltip", () => ({
    Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipContent: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/components/layout/SidebarSearch", () => ({
    SidebarSearch: ({ onNavigate }: { onNavigate?: () => void }) => (
        <input aria-label="Search conversations" onSubmit={onNavigate as never} />
    ),
}));

vi.mock("@/components/layout/SidebarTagsSection", () => ({
    SidebarTagsSection: ({ onNavigate }: { onNavigate?: () => void }) => (
        <button type="button" onClick={onNavigate}>Tag navigation</button>
    ),
}));

vi.mock("@/components/layout/SidebarFavoritesSection", () => ({
    SidebarFavoritesSection: ({ onNavigate }: { onNavigate?: () => void }) => (
        <button type="button" onClick={onNavigate}>Favourite navigation</button>
    ),
}));

vi.mock("@/components/layout/SidebarConversationList", () => ({
    SidebarConversationList: ({ onNavigate }: { onNavigate?: () => void }) => (
        <button type="button" onClick={onNavigate}>Conversation item</button>
    ),
}));

const sidebarState = {
    isCollapsed: false,
    toggleCollapsed: vi.fn(),
    isMobileOpen: false,
    setMobileOpen: vi.fn(),
};

vi.mock("@/components/layout/SidebarUiContext", () => ({
    useSidebarUi: () => sidebarState,
}));

describe("Sidebar", () => {
    beforeEach(() => {
        sidebarState.isCollapsed = false;
        sidebarState.isMobileOpen = false;
        sidebarState.toggleCollapsed.mockReset();
        sidebarState.setMobileOpen.mockReset();
    });

    it("renders the mobile drawer even when the desktop sidebar is collapsed", () => {
        sidebarState.isCollapsed = true;
        sidebarState.isMobileOpen = true;

        render(<Sidebar />);

        expect(screen.getByRole("dialog", { name: "Navigation" })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Expand sidebar" })).toBeInTheDocument();
    });

    it("does not close the mobile drawer when interacting with non-navigation controls", () => {
        sidebarState.isMobileOpen = true;

        render(<Sidebar />);

        const dialog = screen.getByRole("dialog", { name: "Navigation" });
        fireEvent.click(within(dialog).getByLabelText("Search conversations"));

        expect(sidebarState.setMobileOpen).not.toHaveBeenCalled();
    });

    it("closes the mobile drawer when a navigation link is activated", () => {
        sidebarState.isMobileOpen = true;

        render(<Sidebar />);

        const dialog = screen.getByRole("dialog", { name: "Navigation" });
        fireEvent.click(within(dialog).getByText("Settings"));

        expect(sidebarState.setMobileOpen).toHaveBeenCalledWith(false);
    });

    it("renders tooltip copy for the banner and footer utility links", () => {
        render(<Sidebar />);

        expect(screen.getByLabelText("Primary")).toHaveTextContent("Return to the conversation browser");
        expect(screen.getByLabelText("Utilities")).toHaveTextContent("Adjust archive preferences");
        expect(screen.getByLabelText("Utilities")).toHaveTextContent("Import a ChatGPT archive ZIP");
        expect(screen.getByLabelText("Utilities")).toHaveTextContent("Open export and management tools");
        expect(screen.getByLabelText("Utilities")).toHaveTextContent("Open the project guide and docs");
    });
});