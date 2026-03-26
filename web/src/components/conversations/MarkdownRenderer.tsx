import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";

export function MarkdownRenderer({ text }: { text: string }) {
    return (
        <div className="space-y-3 text-sm leading-7 text-foreground" data-testid="markdown-renderer">
            <ReactMarkdown
                remarkPlugins={[remarkBreaks]}
                components={{
                    h1: ({ children }) => (
                        <h1 className="text-xl font-semibold tracking-tight text-foreground">{children}</h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-lg font-semibold tracking-tight text-foreground">{children}</h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-base font-semibold tracking-tight text-foreground">{children}</h3>
                    ),
                    p: ({ children }) => <p className="whitespace-pre-wrap">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc space-y-1 pl-6">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal space-y-1 pl-6">{children}</ol>,
                    li: ({ children }) => <li className="pl-1">{children}</li>,
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-2 border-border pl-4 italic text-muted-foreground">
                            {children}
                        </blockquote>
                    ),
                    a: ({ children, href }) => (
                        <a
                            className="font-medium text-sky-700 underline decoration-sky-300 underline-offset-2 hover:text-sky-800 dark:text-sky-300 dark:decoration-sky-700 dark:hover:text-sky-200"
                            href={href}
                            target="_blank"
                            rel="noreferrer"
                        >
                            {children}
                        </a>
                    ),
                    pre: ({ children }) => (
                        <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-50">
                            {children}
                        </pre>
                    ),
                    code: ({ children, className }) => (
                        <code
                            className={
                                className
                                    ? `${className} font-mono text-sm`
                                    : "rounded bg-muted px-1.5 py-0.5 font-mono text-[0.9em] text-foreground"
                            }
                        >
                            {children}
                        </code>
                    ),
                }}
            >
                {text}
            </ReactMarkdown>
        </div>
    );
}