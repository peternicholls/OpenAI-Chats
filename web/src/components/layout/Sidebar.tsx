"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense } from "react";
import { Search, MessageSquare, Upload, Star, Settings } from "lucide-react";
import { TagList } from "@/components/tags/TagList";

const navigation = [
    { name: "Conversations", href: "/", icon: MessageSquare },
    { name: "Search", href: "/search", icon: Search },
    { name: "Import", href: "/import", icon: Upload },
    { name: "Favorites", href: "/favorites", icon: Star },
    { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="hidden md:flex md:w-64 md:flex-col border-r bg-muted/30">
            <div className="flex flex-col flex-1 overflow-y-auto pt-5 pb-4">
                <div className="flex items-center shrink-0 px-4 mb-6">
                    <Link href="/" className="flex items-center gap-2">
                        <MessageSquare className="h-6 w-6 text-primary" />
                        <span className="text-lg font-bold">ChatGPT Archive</span>
                    </Link>
                </div>
                <nav className="flex-1 space-y-1 px-3">
                    {navigation.map((item) => {
                        const isActive =
                            item.href === "/"
                                ? pathname === "/"
                                : pathname.startsWith(item.href);
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${isActive
                                    ? "bg-primary/10 text-primary"
                                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                    }`}
                            >
                                <item.icon className="h-4 w-4" />
                                {item.name}
                            </Link>
                        );
                    })}
                </nav>
                <div className="mt-4 px-3 border-t pt-4">
                    <Suspense fallback={null}>
                        <TagList />
                    </Suspense>
                </div>
            </div>
        </aside>
    );
}
