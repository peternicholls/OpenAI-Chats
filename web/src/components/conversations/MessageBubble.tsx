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

const roleLabels = {
    user: "You",
    assistant: "Assistant",
    system: "System",
    tool: "Tool",
};

type RoleClasses = {
    outer: string;
    iconBg: string;
    header: string;
    content: string;
};

function getRoleClasses(role: string): RoleClasses {
    switch (role) {
        case "user":
            return {
                outer: "flex-row-reverse ml-auto max-w-[75%] bg-blue-100 text-blue-950 dark:bg-blue-900/60 dark:text-blue-50",
                iconBg: "bg-blue-200 dark:bg-blue-800",
                header: "flex items-center gap-2 mb-1 flex-row-reverse",
                content: "text-right",
            };
        case "assistant":
            return {
                outer: "mr-auto max-w-[75%] bg-zinc-100 text-zinc-900 dark:bg-zinc-800/60 dark:text-zinc-100",
                iconBg: "bg-zinc-200 dark:bg-zinc-700",
                header: "flex items-center gap-2 mb-1",
                content: "",
            };
        case "system":
            return {
                outer: "w-full bg-amber-50 text-amber-900 dark:bg-amber-950/30 dark:text-amber-100",
                iconBg: "bg-amber-100 dark:bg-amber-900/50",
                header: "flex items-center gap-2 mb-1",
                content: "",
            };
        case "tool":
            return {
                outer: "w-full bg-purple-50 text-purple-900 dark:bg-purple-950/30 dark:text-purple-100",
                iconBg: "bg-purple-100 dark:bg-purple-900/50",
                header: "flex items-center gap-2 mb-1",
                content: "",
            };
        default:
            return {
                outer: "w-full bg-muted text-muted-foreground",
                iconBg: "bg-muted-foreground/20",
                header: "flex items-center gap-2 mb-1",
                content: "",
            };
    }
}

export function MessageBubble({ message }: { message: Message }) {
    const Icon = roleIcons[message.role as keyof typeof roleIcons] || Terminal;
    const label = roleLabels[message.role as keyof typeof roleLabels] || message.role;
    const classes = getRoleClasses(message.role);

    return (
        <div className={`flex gap-3 p-4 rounded-lg ${classes.outer}`}>
            <div className="flex-shrink-0 mt-0.5">
                <div className={`h-7 w-7 rounded-full flex items-center justify-center ${classes.iconBg}`}>
                    <Icon className="h-4 w-4" />
                </div>
            </div>
            <div className="flex-1 min-w-0">
                <div className={classes.header}>
                    <span className="text-sm font-semibold">{label}</span>
                    {message.create_time && (
                        <span className="text-xs opacity-60">
                            {formatTime(message.create_time)}
                        </span>
                    )}
                </div>
                <div className={`prose prose-sm max-w-none dark:prose-invert whitespace-pre-wrap break-words ${classes.content}`}>
                    {message.content || <span className="opacity-60 italic">[No content]</span>}
                </div>
            </div>
        </div>
    );
}
