import type { Message } from "@/types";
import { User, Bot, Terminal } from "lucide-react";

function formatTime(timestamp: number | null): string {
    if (!timestamp) return "";
    return new Date(timestamp * 1000).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

const roleIcons = {
    user: User,
    assistant: Bot,
    system: Terminal,
    tool: Terminal,
};

const roleColors = {
    user: "bg-blue-50 dark:bg-blue-950/30",
    assistant: "bg-gray-50 dark:bg-gray-900/30",
    system: "bg-yellow-50 dark:bg-yellow-950/30",
    tool: "bg-purple-50 dark:bg-purple-950/30",
};

const roleLabels = {
    user: "You",
    assistant: "Assistant",
    system: "System",
    tool: "Tool",
};

export function MessageBubble({ message }: { message: Message }) {
    const Icon = roleIcons[message.role] || Terminal;
    const bgColor = roleColors[message.role] || roleColors.system;
    const label = roleLabels[message.role] || message.role;

    return (
        <div className={`flex gap-3 p-4 rounded-lg ${bgColor}`}>
            <div className="flex-shrink-0 mt-0.5">
                <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center">
                    <Icon className="h-4 w-4" />
                </div>
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold">{label}</span>
                    {message.create_time && (
                        <span className="text-xs text-muted-foreground">
                            {formatTime(message.create_time)}
                        </span>
                    )}
                </div>
                <div className="prose prose-sm max-w-none dark:prose-invert whitespace-pre-wrap break-words">
                    {message.content || <span className="text-muted-foreground italic">[No content]</span>}
                </div>
            </div>
        </div>
    );
}
