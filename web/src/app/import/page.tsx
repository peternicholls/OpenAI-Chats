"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useImportProgress } from "@/hooks/useSSE";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { toast } from "sonner";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [polling, setPolling] = useState(false);
  const progress = useImportProgress(polling);

  useEffect(() => {
    if (!progress) return;
    if (progress.status === "complete") {
      toast.success(progress.message || "Import complete");
      setPolling(false);
      setFile(null);
    }
    if (progress.status === "error") {
      toast.error(progress.message || "Import failed");
      setPolling(false);
    }
  }, [progress]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadArchive(file);
      setPolling(true);
      toast.success("Import started");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Import Archive</h1>

      <Card>
        <CardHeader>
          <CardTitle>Upload ChatGPT Export ZIP</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            type="file"
            accept=".zip"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="block w-full text-sm"
          />
          <Button onClick={handleUpload} disabled={!file || uploading || polling}>
            {uploading ? "Uploading..." : polling ? "Importing..." : "Start Import"}
          </Button>
        </CardContent>
      </Card>

      {polling && !progress && <LoadingSpinner className="py-8" />}

      {progress && (
        <Card>
          <CardHeader>
            <CardTitle>Import Progress</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm text-muted-foreground">{progress.message || "Working..."}</div>
            <div className="h-2 w-full bg-muted rounded overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${Math.max(0, Math.min(100, progress.percent))}%` }}
              />
            </div>
            <div className="text-sm">
              {progress.current} / {progress.total} ({progress.percent.toFixed(1)}%)
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
