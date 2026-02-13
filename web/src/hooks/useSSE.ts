"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "@/services/api";
import type { ImportProgress } from "@/types";

export function useSSE(url?: string) {
    const [progress, setProgress] = useState<ImportProgress | null>(null);
    const [error, setError] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    const connect = useCallback(() => {
        if (!url) return;

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setProgress(data);
                if (data.status === "complete" || data.status === "error") {
                    eventSource.close();
                }
            } catch {
                setError("Failed to parse progress data");
            }
        };

        eventSource.onerror = () => {
            setError("Connection lost, retrying...");
            eventSource.close();
            // Auto-reconnect after 3 seconds
            setTimeout(connect, 3000);
        };
    }, [url]);

    const disconnect = useCallback(() => {
        eventSourceRef.current?.close();
        eventSourceRef.current = null;
    }, []);

    useEffect(() => {
        return () => disconnect();
    }, [disconnect]);

    return { progress, error, connect, disconnect };
}

export function useImportProgress(polling: boolean = false) {
    const [progress, setProgress] = useState<ImportProgress | null>(null);

    useEffect(() => {
        if (!polling) return;

        const interval = setInterval(async () => {
            try {
                const data = await api.getImportProgress();
                setProgress(data);
                if (data.status === "complete" || data.status === "error" || data.status === "idle") {
                    clearInterval(interval);
                }
            } catch {
                // Ignore polling errors
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [polling]);

    return progress;
}
