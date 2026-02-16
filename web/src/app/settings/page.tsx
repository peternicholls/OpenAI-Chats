"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import type { ExportFormatCode, UserSettings } from "@/types";
import { toast } from "sonner";

export default function SettingsPage() {
  const { data, isLoading } = useSettings();
  const updateSettings = useUpdateSettings();
  const { theme: currentTheme, setTheme } = useTheme();
  const [draft, setDraft] = useState<Partial<UserSettings>>({});

  const theme = draft.theme ?? currentTheme ?? "system";
  const defaultExportFormat = draft.default_export_format ?? data?.default_export_format ?? "md";
  const openaiApiKey = draft.openai_api_key ?? data?.openai_api_key ?? "";

  const handleThemeChange = (value: string) => {
    setDraft((current) => ({ ...current, theme: value as "light" | "dark" | "system" }));
    setTheme(value); // Apply theme immediately
  };

  const handleSave = async () => {
    try {
      await updateSettings.mutateAsync({
        theme,
        default_export_format: defaultExportFormat,
        openai_api_key: openaiApiKey,
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
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>General</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Theme</label>
            <Select
              value={theme}
              onValueChange={handleThemeChange}
            >
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
            <label className="text-sm font-medium">OpenAI API Key</label>
            <Input
              type="password"
              value={openaiApiKey}
              onChange={(event) =>
                setDraft((current) => ({ ...current, openai_api_key: event.target.value }))
              }
              placeholder="sk-..."
              autoComplete="off"
            />
          </div>

          <Button onClick={handleSave} disabled={updateSettings.isPending}>
            {updateSettings.isPending ? "Saving..." : "Save Settings"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
