"use client"

import { useState } from "react"
import { Copy, Volume2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { copyToClipboard, speakText } from "@/lib/utils"

interface TurnActionsProps {
    text: string
}

export function TurnActions({ text }: TurnActionsProps) {
    const [copied, setCopied] = useState(false)

    const handleCopy = async () => {
        await copyToClipboard(text)
        setCopied(true)
        window.setTimeout(() => setCopied(false), 2000)
    }

    const handleSpeak = () => {
        speakText(text)
    }

    return (
        <div className="flex items-center gap-2">
            <Button type="button" variant="outline" size="xs" onClick={handleCopy}>
                <Copy />
                {copied ? "Copied" : "Copy"}
            </Button>
            <Button type="button" variant="outline" size="xs" onClick={handleSpeak}>
                <Volume2 />
                Speak
            </Button>
        </div>
    )
}