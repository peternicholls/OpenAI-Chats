"use client";

import { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { api } from "@/services/api";
import { toast } from "sonner";
import { Download } from "lucide-react";
import type { ExportFormat } from "@/types";

interface ExportDialogProps {
    conversationId: string;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

const FORMATS: { value: ExportFormat; label: string }[] = [
    { value: "markdown", label: "Markdown (.md)" },
    { value: "json", label: "JSON (.json)" },
    { value: "html", label: "HTML (.html)" },
    { value: "csv", label: "CSV (.csv)" },
    { value: "yaml", label: "YAML (.yaml)" },
    { value: "xml", label: "XML (.xml)" },
    { value: "excel", label: "Excel (.xlsx)" },
];

export function ExportDialog({ conversationId, open, onOpenChange }: ExportDialogProps) {
    const [format, setFormat] = useState<ExportFormat>("markdown");
    const [isExporting, setIsExporting] = useState(false);

    const handleExport = async () => {
        setIsExporting(true);
        try {
            const blob = await api.exportConversation(conversationId, format);
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `conversation.${format === "excel" ? "xlsx" : format === "markdown" ? "md" : format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            toast.success("Export downloaded");
            onOpenChange(false);
        } catch {
            toast.error("Export failed");
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Export Conversation</DialogTitle>
                    <DialogDescription>
                        Choose a format to export this conversation.
                    </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                    <Select value={format} onValueChange={(v) => setFormat(v as ExportFormat)}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select format" />
                        </SelectTrigger>
                        <SelectContent>
                            {FORMATS.map((f) => (
                                <SelectItem key={f.value} value={f.value}>
                                    {f.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Cancel
                    </Button>
                    <Button onClick={handleExport} disabled={isExporting}>
                        <Download className="h-4 w-4 mr-2" />
                        {isExporting ? "Exporting..." : "Download"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
