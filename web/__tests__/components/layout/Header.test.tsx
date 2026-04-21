import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Header } from "@/components/layout/Header";

vi.mock("next/link", () => ({
    default: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
        <a href={href} {...props}>
            {children}
        </a>
    ),
}));

vi.mock("@/components/ui/tooltip", () => ({
    Tooltip: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    TooltipContent: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const sidebarState = {
    setMobileOpen: vi.fn(),
};

vi.mock("@/components/layout/SidebarUiContext", () => ({
    useSidebarUi: () => sidebarState,
}));

describe("Header", () => {
    it("renders tooltip copy for the mobile banner link", () => {
        render(<Header />);

        expect(screen.getByRole("banner")).toHaveTextContent("Return to the conversation browser");
        expect(screen.getByRole("link", { name: "ChatGPT Archive" })).toHaveAttribute("href", "/");
    });
});
