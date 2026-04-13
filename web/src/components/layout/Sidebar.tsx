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
        <aside className="hidden border-r bg-muted/30 md:flex md:w-64 md:flex-col">
            <div className="flex min-h-0 flex-1 flex-col">
                <div className="sticky top-0 z-10 bg-muted/30 pt-5">
                    <div className="mb-6 flex shrink-0 items-center px-4">
                        <Link href="/" className="flex items-center gap-2">
                            <MessageSquare className="h-6 w-6 text-primary" />
                            <span className="text-lg font-bold">ChatGPT Archive</span>
                        </Link>
                    </div>
                    <hr className="w-full border-border" />
                </div>
                <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
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
                <hr className="w-full border-border" />
                <div className="sticky bottom-0 mt-4 bg-muted/30 px-3 pt-4 pb-4">
                    <Suspense fallback={null}>
                        <TagList />
                    </Suspense>
                </div>
            </div>
        </aside>
    );
}
