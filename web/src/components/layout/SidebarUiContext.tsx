"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";

interface SidebarUiContextValue {
    /** Desktop collapsed-to-icons state (persisted via settings). */
    isCollapsed: boolean;
    toggleCollapsed: () => void;
    /** Mobile drawer open state (transient). */
    isMobileOpen: boolean;
    setMobileOpen: (open: boolean) => void;
}

const SidebarUiContext = createContext<SidebarUiContextValue | null>(null);

export function SidebarUiProvider({ children }: { children: ReactNode }) {
    const { data: settings } = useSettings();
    const { mutate: updateSettings } = useUpdateSettings();

    const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
    const [isMobileOpen, setMobileOpen] = useState(false);

    // Hydrate from server-side settings once they arrive.
    useEffect(() => {
        if (typeof settings?.sidebar_collapsed === "boolean") {
            setIsCollapsed(settings.sidebar_collapsed);
        }
    }, [settings?.sidebar_collapsed]);

    const toggleCollapsed = useCallback(() => {
        setIsCollapsed((prev) => {
            const next = !prev;
            updateSettings({ sidebar_collapsed: next });
            return next;
        });
    }, [updateSettings]);

    const value = useMemo<SidebarUiContextValue>(
        () => ({ isCollapsed, toggleCollapsed, isMobileOpen, setMobileOpen }),
        [isCollapsed, toggleCollapsed, isMobileOpen]
    );

    return <SidebarUiContext.Provider value={value}>{children}</SidebarUiContext.Provider>;
}

export function useSidebarUi(): SidebarUiContextValue {
    const ctx = useContext(SidebarUiContext);
    if (!ctx) {
        throw new Error("useSidebarUi must be used within a SidebarUiProvider");
    }
    return ctx;
}
