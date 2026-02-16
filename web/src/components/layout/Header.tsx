"use client";

import Link from "next/link";
import { Search, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function Header() {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState("");

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        }
    };

    return (
        <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
            <div className="flex h-14 items-center gap-4 px-4 md:px-6">
                {/* Mobile menu button */}
                <Button variant="ghost" size="icon" className="md:hidden">
                    <Menu className="h-5 w-5" />
                </Button>

                {/* Mobile logo */}
                <Link href="/" className="md:hidden font-bold text-lg">
                    Archive
                </Link>

                {/* Search bar */}
                <form onSubmit={handleSearch} className="flex-1 max-w-lg">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Search conversations... (Ctrl+K)"
                            className="pl-8 bg-muted/50"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </form>
            </div>
        </header>
    );
}
