export function FallbackBlock({ label, text }: { label: string; text: string }) {
    return (
        <div
            className="rounded-lg border border-amber-200 bg-amber-50/80 p-4 text-sm text-amber-950 dark:border-amber-950/50 dark:bg-amber-950/20 dark:text-amber-100"
            data-testid="fallback-block"
        >
            <div className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-amber-800/80 dark:text-amber-200/80">
                {label}
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap wrap-break-word font-mono text-xs leading-6">
                {text}
            </pre>
        </div>
    );
}