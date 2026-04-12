"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ApiCredentials } from "@/components/settings/ApiCredentials";
import { EmbeddingSettings } from "@/components/settings/EmbeddingSettings";
import { toast } from "sonner";
import type { ExportFormatCode, UserSettings } from "@/types";
import { Settings, Key, Sparkles } from "lucide-react";

export function SettingsForm() {
    const { data, isLoading } = useSettings();
    const updateSettings = useUpdateSettings();
    const { theme: currentTheme, setTheme } = useTheme();
    const [draft, setDraft] = useState<Partial<UserSettings>>({});

    const theme = draft.theme ?? currentTheme ?? "system";
    const defaultExportFormat = draft.default_export_format ?? data?.default_export_format ?? "md";
    const archiveMediaDir = draft.archive_media_dir ?? data?.archive_media_dir ?? "";
    const codeLineNumbers = draft.code_line_numbers ?? data?.code_line_numbers ?? false;
    const longPromptTruncation = draft.long_prompt_truncation ?? data?.long_prompt_truncation ?? true;

    const handleThemeChange = (value: string) => {
        setDraft((current) => ({ ...current, theme: value as "light" | "dark" | "system" }));
        setTheme(value);
    };

    const handleSaveGeneral = async () => {
        try {
            await updateSettings.mutateAsync({
                theme: theme as "light" | "dark" | "system",
                default_export_format: defaultExportFormat,
                archive_media_dir: archiveMediaDir,
                code_line_numbers: codeLineNumbers,
                long_prompt_truncation: longPromptTruncation,
            });
            toast.success("Settings saved");
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to save settings");
        }
    };

    if (isLoading) {
        return <LoadingSpinner className="min-h-[40vh]" />;
    }

    return (
        <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="general" className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    <span className="hidden sm:inline">General</span>
                </TabsTrigger>
                <TabsTrigger value="api" className="flex items-center gap-2">
                    <Key className="h-4 w-4" />
                    <span className="hidden sm:inline">API</span>
                </TabsTrigger>
                <TabsTrigger value="embeddings" className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    <span className="hidden sm:inline">Embeddings</span>
                </TabsTrigger>
            </TabsList>

            <TabsContent value="general">
                <Card>
                    <CardHeader>
                        <CardTitle>General Settings</CardTitle>
                        <CardDescription>
                            Configure your display preferences and default options.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Theme</label>
                            <Select value={theme} onValueChange={handleThemeChange}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="light">Light</SelectItem>
                                    <SelectItem value="dark">Dark</SelectItem>
                                    <SelectItem value="system">System</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Default Export Format</label>
                            <Select
                                value={defaultExportFormat}
                                onValueChange={(value) =>
                                    setDraft((current) => ({ ...current, default_export_format: value as ExportFormatCode }))
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="md">Markdown (.md)</SelectItem>
                                    <SelectItem value="json">JSON (.json)</SelectItem>
                                    <SelectItem value="yaml">YAML (.yaml)</SelectItem>
                                    <SelectItem value="html">HTML (.html)</SelectItem>
                                    <SelectItem value="xml">XML (.xml)</SelectItem>
                                    <SelectItem value="csv">CSV (.csv)</SelectItem>
                                    <SelectItem value="xlsx">Excel (.xlsx)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Archive Media Directory</label>
                            <Input
                                value={archiveMediaDir}
                                onChange={(event) =>
                                    setDraft((current) => ({ ...current, archive_media_dir: event.target.value }))
                                }
                                placeholder="/path/to/extracted/archive"
                            />
                            <p className="text-sm text-muted-foreground">
                                Optional path to an extracted archive used for inline media lookup.
                            </p>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <label className="text-sm font-medium">Code Line Numbers</label>
                                <p className="text-sm text-muted-foreground">Show line numbers in code blocks.</p>
                            </div>
                            <input
                                type="checkbox"
                                checked={codeLineNumbers}
                                onChange={(e) =>
                                    setDraft((current) => ({ ...current, code_line_numbers: e.target.checked }))
                                }
                                className="h-4 w-4"
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <label className="text-sm font-medium">Truncate Long Prompts</label>
                                <p className="text-sm text-muted-foreground">Collapse user prompts longer than 500 characters with a "Read more" toggle.</p>
                            </div>
                            <input
                                type="checkbox"
                                checked={longPromptTruncation}
                                onChange={(e) =>
                                    setDraft((current) => ({ ...current, long_prompt_truncation: e.target.checked }))
                                }
                                className="h-4 w-4"
                            />
                        </div>

                        <Button onClick={handleSaveGeneral} disabled={updateSettings.isPending}>
                            {updateSettings.isPending ? "Saving..." : "Save Settings"}
                        </Button>
                    </CardContent>
                </Card>
            </TabsContent>

            <TabsContent value="api">
                <ApiCredentials />
            </TabsContent>

            <TabsContent value="embeddings">
                <EmbeddingSettings />
            </TabsContent>
        </Tabs>
    );
}
