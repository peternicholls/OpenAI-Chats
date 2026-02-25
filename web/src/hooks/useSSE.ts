"use client";

import { useState, useEffect, useRef } from "react";
import { api } from "@/services/api";
import type { ImportProgress } from "@/types";

export function useSSE(url?: string) {
    const [progress, setProgress] = useState<ImportProgress | null>(null);
    const [error, setError] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    function openConnection() {
        if (!url) return;

        if (reconnectTimerRef.current) {
            clearTimeout(reconnectTimerRef.current);
            reconnectTimerRef.current = null;
        }

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;
        setError(null);

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
            eventSourceRef.current = null;
            // Auto-reconnect after 3 seconds
            reconnectTimerRef.current = setTimeout(() => {
                openConnection();
            }, 3000);
        };
    }

    const connect = () => {
        openConnection();
    };

    const disconnect = () => {
        eventSourceRef.current?.close();
        eventSourceRef.current = null;
        if (reconnectTimerRef.current) {
            clearTimeout(reconnectTimerRef.current);
            reconnectTimerRef.current = null;
        }
    };

    useEffect(() => {
        return () => {
            eventSourceRef.current?.close();
            eventSourceRef.current = null;
            if (reconnectTimerRef.current) {
                clearTimeout(reconnectTimerRef.current);
                reconnectTimerRef.current = null;
            }
        };
    }, []);

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
