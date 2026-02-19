"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useSettings } from "@/hooks/useSettings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { toast } from "sonner";
import { AlertCircle, CheckCircle, Loader2, Play, Square, DollarSign, Sparkles } from "lucide-react";
import type { ImportProgress } from "@/types";

export function EmbeddingSettings() {
    const { data: settings } = useSettings();
    const [isGenerating, setIsGenerating] = useState(false);
    const [progress, setProgress] = useState<ImportProgress | null>(null);
    const [maxCost, setMaxCost] = useState("5.00");
    const [embeddingStats, setEmbeddingStats] = useState<{
        total: number;
        withEmbeddings: number;
    } | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    const hasApiKey = Boolean(settings?.openai_api_key);

    const fetchStats = useCallback(async () => {
        try {
            const data = await api.getEmbeddingStats();
            setEmbeddingStats(data);
        } catch {
            // Silently fail - stats are optional
        }
    }, []);

    // Fetch embedding stats on mount
    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    const startProgressStream = useCallback(() => {
        eventSourceRef.current?.close();
        eventSourceRef.current = new EventSource(api.getEmbeddingsProgressStreamUrl());

        eventSourceRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data) as ImportProgress;
            setProgress(data);

            if (["complete", "error", "cancelled", "idle"].includes(data.status)) {
                setIsGenerating(false);
                eventSourceRef.current?.close();
                eventSourceRef.current = null;

                if (data.status === "complete") {
                    toast.success(data.message ?? `Generated embeddings for ${data.current} messages`);
                    void fetchStats();
                } else if (data.status === "cancelled") {
                    toast.info(data.message ?? "Embedding generation cancelled");
                    void fetchStats();
                } else if (data.status === "error") {
                    toast.error(data.message ?? "Embedding generation failed");
                }
            }
        };

        eventSourceRef.current.onerror = () => {
            if (isGenerating) {
                setIsGenerating(false);
                toast.error("Embedding progress stream disconnected");
            }
            eventSourceRef.current?.close();
            eventSourceRef.current = null;
        };
    }, [fetchStats, isGenerating]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            eventSourceRef.current?.close();
        };
    }, []);

    const handleStartGeneration = async () => {
        if (!hasApiKey) {
            toast.error("Please configure your OpenAI API key first");
            return;
        }

        const costLimit = parseFloat(maxCost);
        if (isNaN(costLimit) || costLimit <= 0) {
            toast.error("Please enter a valid cost limit");
            return;
        }

        setIsGenerating(true);
        setProgress({
            current: 0,
            total: 0,
            percent: 0,
            status: "pending",
            message: "Starting embedding generation...",
        });

        // Start listening for progress
        startProgressStream();

        try {
            await api.generateEmbeddings({ maxCost: costLimit });
        } catch (error) {
            setIsGenerating(false);
            eventSourceRef.current?.close();
            eventSourceRef.current = null;
            toast.error(error instanceof Error ? error.message : "Failed to generate embeddings");
        }
    };

    const handleCancel = async () => {
        try {
            await api.cancelEmbeddingGeneration();
            toast.info("Cancelling embedding generation...");
        } catch {
            toast.error("Failed to cancel generation");
        }
    };

    const progressPercent = progress?.percent ?? 0;

    const estimatedCost = embeddingStats
        ? ((embeddingStats.total - embeddingStats.withEmbeddings) * 0.0001).toFixed(4)
        : null;

    const hasPendingEmbeddings = embeddingStats && embeddingStats.withEmbeddings > 0 &&
        embeddingStats.withEmbeddings < embeddingStats.total;
    const allComplete = embeddingStats?.total === embeddingStats?.withEmbeddings;

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Embedding Generation
                </CardTitle>
                <CardDescription>
                    Generate embeddings for your conversations to enable semantic search.
                    This uses the OpenAI API and incurs a small cost.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                {!hasApiKey && (
                    <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-md">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">Please configure your OpenAI API key in the API tab first</span>
                    </div>
                )}

                {embeddingStats && (
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-muted rounded-md">
                            <div className="text-2xl font-bold">{embeddingStats.withEmbeddings}</div>
                            <div className="text-sm text-muted-foreground">Conversations with embeddings</div>
                        </div>
                        <div className="p-3 bg-muted rounded-md">
                            <div className="text-2xl font-bold">{embeddingStats.total - embeddingStats.withEmbeddings}</div>
                            <div className="text-sm text-muted-foreground">Conversations pending</div>
                        </div>
                    </div>
                )}

                {hasPendingEmbeddings && (
                    <div className="flex items-center gap-2 p-3 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 rounded-md">
                        <AlertCircle className="h-4 w-4" />
                        <span className="text-sm">
                            Some conversations have embeddings. Click Resume to continue from where you left off.
                        </span>
                    </div>
                )}

                {allComplete && embeddingStats && embeddingStats.total > 0 && (
                    <div className="flex items-center gap-2 p-3 bg-green-500/10 text-green-600 dark:text-green-400 rounded-md">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm">All conversations have embeddings!</span>
                    </div>
                )}

                <div className="space-y-2">
                    <label className="text-sm font-medium flex items-center gap-2">
                        <DollarSign className="h-4 w-4" />
                        Maximum Cost Limit (USD)
                    </label>
                    <div className="flex items-center gap-2">
                        <Input
                            type="number"
                            min="0.01"
                            max="100"
                            step="0.01"
                            value={maxCost}
                            onChange={(e) => setMaxCost(e.target.value)}
                            className="w-32"
                            disabled={isGenerating}
                        />
                        {estimatedCost && (
                            <span className="text-sm text-muted-foreground">
                                Estimated cost: ~${estimatedCost}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Generation will stop if the cost exceeds this limit. Uses text-embedding-3-small at ~$0.0001 per conversation.
                    </p>
                </div>

                {isGenerating && progress && (
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                            <span>{progress.message ?? progress.status}</span>
                            <span>{progress.current} / {progress.total}</span>
                        </div>
                        <Progress value={progressPercent} className="h-2" />
                    </div>
                )}

                <div className="flex gap-2">
                    {!isGenerating ? (
                        <Button
                            onClick={handleStartGeneration}
                            disabled={!hasApiKey || allComplete}
                        >
                            <Play className="mr-2 h-4 w-4" />
                            {hasPendingEmbeddings ? "Resume Generation" : "Generate Embeddings"}
                        </Button>
                    ) : (
                        <Button variant="destructive" onClick={handleCancel}>
                            <Square className="mr-2 h-4 w-4" />
                            Cancel
                        </Button>
                    )}

                    {isGenerating && (
                        <div className="flex items-center text-sm text-muted-foreground">
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
