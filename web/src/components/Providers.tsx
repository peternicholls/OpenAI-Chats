"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { getQueryClient } from "@/lib/react-query";
import { Toaster } from "@/components/ui/sonner";

export function Providers({ children }: { children: React.ReactNode }) {
    const queryClient = getQueryClient();

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider
                attribute="class"
                defaultTheme="system"
                enableSystem
                disableTransitionOnChange
            >
                {children}
                <Toaster />
            </ThemeProvider>
        </QueryClientProvider>
    );
}
