"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
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

    const [collapsedOverride, setCollapsedOverride] = useState<boolean | null>(null);
    const [isMobileOpen, setMobileOpen] = useState(false);
    const isCollapsed = collapsedOverride ?? settings?.sidebar_collapsed ?? false;

    const toggleCollapsed = useCallback(() => {
        setCollapsedOverride((prev) => {
            const current = prev ?? settings?.sidebar_collapsed ?? false;
            const next = !current;
            updateSettings({ sidebar_collapsed: next });
            return next;
        });
    }, [settings?.sidebar_collapsed, updateSettings]);

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
