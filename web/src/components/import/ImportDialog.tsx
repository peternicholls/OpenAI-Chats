"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/services/api";
import { useImportProgress } from "@/hooks/useSSE";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ImportProgress } from "@/components/import/ImportProgress";
import { toast } from "sonner";

const MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024;

function validateZipFile(file: File | null): string | null {
  if (!file) return "Please choose an archive file.";
  const fileName = file.name.toLowerCase();
  const isZipType =
    fileName.endsWith(".zip") ||
    file.type.includes("zip") ||
    file.type === "application/x-zip-compressed";

  if (!isZipType) return "Only .zip files are supported.";
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return "File is too large. Maximum supported size is 500MB.";
  }

  return null;
}

function mapImportError(error: unknown): string {
  const base = error instanceof Error ? error.message : "Import failed";
  const normalized = base.toLowerCase();

  if (normalized.includes("zip") && (normalized.includes("corrupt") || normalized.includes("invalid"))) {
    return "The ZIP appears corrupted or invalid. Export the archive again and retry.";
  }
  if (normalized.includes("413") || normalized.includes("too large")) {
    return "Upload failed because the archive is larger than the allowed limit.";
  }
  if (normalized.includes("network")) {
    return "Network error while uploading. Check connection and retry.";
  }

  return base;
}

interface ImportDialogProps {
  triggerLabel?: string;
}

export function ImportDialog({ triggerLabel = "Import Archive" }: ImportDialogProps) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadPercent, setUploadPercent] = useState(0);
  const [polling, setPolling] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const progress = useImportProgress(polling);
  const lastProgressStatus = useRef<string | null>(null);

  const fileValidationError = useMemo(() => validateZipFile(file), [file]);

  useEffect(() => {
    if (!progress) return;
    if (progress.status === lastProgressStatus.current) return;
    lastProgressStatus.current = progress.status;

    if (progress.status === "complete") {
      toast.success(progress.message || "Import complete");
    } else if (progress.status === "error") {
      toast.error(progress.message || "Import failed");
    }
  }, [progress]);

  const resetDialogState = () => {
    setFile(null);
    setUploading(false);
    setUploadPercent(0);
    setPolling(false);
    setUploadError(null);
  };

  const runImport = async () => {
    const validationError = validateZipFile(file);
    if (validationError) {
      setUploadError(validationError);
      return;
    }

    setUploadError(null);
    setPolling(false);
    setUploading(true);
    setUploadPercent(0);
    try {
      await api.uploadArchiveWithProgress(file as File, setUploadPercent);
      setUploading(false);
      setUploadPercent(100);
      setPolling(true);
      toast.success("Import started");
    } catch (error) {
      setUploading(false);
      setPolling(false);
      setUploadError(mapImportError(error));
    }
  };

  const isTerminalProgress =
    progress?.status === "complete" ||
    progress?.status === "error" ||
    progress?.status === "idle";
  const isProcessing = polling && !isTerminalProgress;
  const effectiveUploadError =
    uploadError || (progress?.status === "error" ? progress.message : null);

  return (
    <Dialog
      open={open}
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen);
        if (!nextOpen) {
          resetDialogState();
        }
      }}
    >
      <DialogTrigger asChild>
        <Button>{triggerLabel}</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Import ChatGPT Archive</DialogTitle>
          <DialogDescription>
            Upload your ChatGPT export ZIP file. Maximum file size is 500MB.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <Input
            type="file"
            accept=".zip,application/zip,application/x-zip-compressed"
            disabled={uploading || isProcessing}
            onChange={(event) => {
              setUploadError(null);
              setUploadPercent(0);
              lastProgressStatus.current = null;
              setFile(event.target.files?.[0] || null);
            }}
          />
          {fileValidationError && file ? (
            <p className="text-sm text-destructive">{fileValidationError}</p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Accepted file type: `.zip`, max 500MB.
            </p>
          )}
        </div>

        <ImportProgress
          progress={progress}
          fileName={file?.name}
          uploadPercent={uploadPercent}
          uploadError={effectiveUploadError}
          onRetry={runImport}
        />

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              resetDialogState();
            }}
            disabled={uploading}
          >
            Reset
          </Button>
          <Button
            onClick={runImport}
            disabled={Boolean(fileValidationError) || !file || uploading || isProcessing}
          >
            {uploading ? "Uploading..." : isProcessing ? "Importing..." : "Start Import"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
