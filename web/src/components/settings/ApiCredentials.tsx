"use client";

import { useState, useMemo } from "react";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { toast } from "sonner";
import { Eye, EyeOff, CheckCircle, XCircle, Loader2, ShieldCheck } from "lucide-react";

export function ApiCredentials() {
    const { data } = useSettings();
    const updateSettings = useUpdateSettings();
    const [apiKey, setApiKey] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [validationState, setValidationState] = useState<"idle" | "validating" | "valid" | "invalid">("idle");

    // Derive hasKey from data instead of using effect
    const hasKey = useMemo(() => Boolean(data?.openai_api_key), [data?.openai_api_key]);

    const validateApiKey = async (key: string) => {
        if (!key.startsWith("sk-")) {
            setValidationState("invalid");
            toast.error("Invalid API key format. OpenAI keys start with 'sk-'");
            return false;
        }

        setValidationState("validating");
        try {
            await api.validateEmbeddingsKey(key);
            setValidationState("valid");
            toast.success("API key is valid");
            return true;
        } catch (error) {
            setValidationState("invalid");
            toast.error(error instanceof Error ? error.message : "Failed to validate API key");
            return false;
        }
    };

    const handleTestConnection = async () => {
        if (apiKey) {
            await validateApiKey(apiKey);
        } else if (hasKey) {
            // Test the stored key
            setValidationState("validating");
            try {
                await api.validateEmbeddingsKey();
                setValidationState("valid");
                toast.success("Stored API key is valid");
            } catch (error) {
                setValidationState("invalid");
                toast.error(
                    error instanceof Error ? error.message : "Failed to validate stored API key"
                );
            }
        } else {
            toast.error("Please enter an API key first");
        }
    };

    const handleSave = async () => {
        if (!apiKey) {
            toast.error("Please enter an API key");
            return;
        }

        // Validate before saving
        const isValid = await validateApiKey(apiKey);
        if (!isValid) {
            return;
        }

        try {
            await updateSettings.mutateAsync({
                openai_api_key: apiKey,
            });
            setApiKey(""); // Clear input after save
            toast.success("API key saved securely");
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to save API key");
        }
    };

    const handleClear = async () => {
        try {
            await updateSettings.mutateAsync({
                openai_api_key: "",
            });
            setApiKey("");
            setValidationState("idle");
            toast.success("API key removed");
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to remove API key");
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>OpenAI API Key</CardTitle>
                <CardDescription>
                    Enter your OpenAI API key to enable embedding generation for semantic search.
                    Your key is encrypted before storage.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <ShieldCheck className="h-4 w-4 text-green-500" />
                    <span>API keys are encrypted at rest using industry-standard encryption</span>
                </div>

                {hasKey && !apiKey && (
                    <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm">API key is configured (••••••••)</span>
                    </div>
                )}

                <div className="space-y-2">
                    <label className="text-sm font-medium">
                        {hasKey ? "Update API Key" : "API Key"}
                    </label>
                    <div className="relative">
                        <Input
                            type={showKey ? "text" : "password"}
                            value={apiKey}
                            onChange={(e) => {
                                setApiKey(e.target.value);
                                setValidationState("idle");
                            }}
                            placeholder={hasKey ? "Enter new key to update" : "sk-..."}
                            className="pr-10"
                        />
                        <button
                            type="button"
                            onClick={() => setShowKey(!showKey)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                            {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {validationState === "validating" && (
                        <>
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">Validating...</span>
                        </>
                    )}
                    {validationState === "valid" && (
                        <>
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm text-green-500">Key is valid</span>
                        </>
                    )}
                    {validationState === "invalid" && (
                        <>
                            <XCircle className="h-4 w-4 text-destructive" />
                            <span className="text-sm text-destructive">Key is invalid</span>
                        </>
                    )}
                </div>

                <div className="flex flex-wrap gap-2">
                    <Button
                        variant="outline"
                        onClick={handleTestConnection}
                        disabled={validationState === "validating"}
                    >
                        {validationState === "validating" ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Testing...
                            </>
                        ) : (
                            "Test Connection"
                        )}
                    </Button>

                    <Button
                        onClick={handleSave}
                        disabled={!apiKey || updateSettings.isPending || validationState === "validating"}
                    >
                        {updateSettings.isPending ? "Saving..." : "Save Key"}
                    </Button>

                    {hasKey && (
                        <Button variant="destructive" onClick={handleClear}>
                            Remove Key
                        </Button>
                    )}
                </div>

                <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a
                        href="https://platform.openai.com/api-keys"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                    >
                        platform.openai.com/api-keys
                    </a>
                </p>
            </CardContent>
        </Card>
    );
}
