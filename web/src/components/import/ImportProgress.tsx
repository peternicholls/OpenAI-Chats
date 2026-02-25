"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ImportProgress as ImportProgressData } from "@/types";

interface ImportProgressProps {
  progress: ImportProgressData | null;
  fileName?: string | null;
  uploadPercent?: number;
  uploadError?: string | null;
  onRetry?: () => void;
}

function formatPercent(value: number): string {
  return `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
}

export function ImportProgress({
  progress,
  fileName,
  uploadPercent,
  uploadError,
  onRetry,
}: ImportProgressProps) {
  const hasUploadProgress =
    typeof uploadPercent === "number" && uploadPercent > 0 && uploadPercent < 100;
  const hasProcessingProgress =
    progress && progress.status !== "idle" && progress.status !== "pending";
  const hasError = Boolean(uploadError) || progress?.status === "error";
  const message = uploadError || progress?.message || "Preparing import...";

  if (!hasUploadProgress && !hasProcessingProgress && !hasError) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {fileName ? (
          <div className="text-sm text-muted-foreground">
            File: <span className="font-medium text-foreground">{fileName}</span>
          </div>
        ) : null}

        {hasUploadProgress ? (
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">Uploading archive</div>
            <div className="h-2 w-full rounded bg-muted overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${Math.max(0, Math.min(100, uploadPercent))}%` }}
              />
            </div>
            <div className="text-sm">{formatPercent(uploadPercent || 0)}</div>
          </div>
        ) : null}

        {hasProcessingProgress ? (
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">{message}</div>
            <div className="h-2 w-full rounded bg-muted overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${Math.max(0, Math.min(100, progress.percent))}%` }}
              />
            </div>
            <div className="text-sm">
              {progress.current} / {progress.total} ({formatPercent(progress.percent)})
            </div>
          </div>
        ) : null}

        {hasError ? (
          <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3 space-y-3">
            <p className="text-sm text-destructive">
              {message || "Import failed. Please try again."}
            </p>
            {onRetry ? (
              <Button variant="outline" size="sm" onClick={onRetry}>
                Retry Import
              </Button>
            ) : null}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
