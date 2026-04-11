const dateFormatter = new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
});

export function DateSeparator({ date }: { date: Date }) {
    return (
        <div
            className="flex items-center gap-3 py-3"
            data-testid="date-separator"
            role="separator"
            aria-label={dateFormatter.format(date)}
        >
            <div className="h-px flex-1 bg-border/60" />
            <span className="shrink-0 text-[11px] font-medium tracking-wide text-muted-foreground/70">
                {dateFormatter.format(date)}
            </span>
            <div className="h-px flex-1 bg-border/60" />
        </div>
    );
}
