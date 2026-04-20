"use client"

import { useState } from "react"
import { Check, Copy, Volume2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { copyToClipboard, speakText } from "@/lib/utils"

interface TurnActionsProps {
    text: string
}

export function TurnActions({ text }: TurnActionsProps) {
    const [copied, setCopied] = useState(false)
    const hasText = text.trim().length > 0

    const handleCopy = async () => {
        if (!hasText) {
            return
        }

        await copyToClipboard(text)
        setCopied(true)
        window.setTimeout(() => setCopied(false), 2000)
    }

    const handleSpeak = () => {
        if (!hasText) {
            return
        }

        speakText(text)
    }

    return (
        <div className="flex items-center gap-2" data-testid="turn-actions">
            <Tooltip open={copied ? true : undefined}>
                <TooltipTrigger asChild>
                    <Button
                        type="button"
                        variant="outline"
                        size="icon-xs"
                        onClick={handleCopy}
                        disabled={!hasText}
                        aria-label="Copy turn"
                        data-testid="turn-copy-button"
                    >
                        {copied ? <Check className="text-green-600 dark:text-green-400" /> : <Copy />}
                    </Button>
                </TooltipTrigger>
                <TooltipContent>{copied ? "Copied" : "Copy turn"}</TooltipContent>
            </Tooltip>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Button
                        type="button"
                        variant="outline"
                        size="icon-xs"
                        onClick={handleSpeak}
                        disabled={!hasText}
                        aria-label="Speak turn"
                        data-testid="turn-speak-button"
                    >
                        <Volume2 />
                    </Button>
                </TooltipTrigger>
                <TooltipContent>Speak turn</TooltipContent>
            </Tooltip>
        </div>
    )
}