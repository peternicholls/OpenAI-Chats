import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { useState, useCallback, type ReactNode } from "react";
import { Check, Copy } from "lucide-react";

/**
 * Strip PUA citation tokens injected by ChatGPT's retrieval system.
 * Pattern: \uE200(file)?cite(\uE202turnNsearchM|\uE202turnNviewM|\uE202turnNfileM)+\uE201
 */
const CITATION_RE = /\uE200(?:file)?cite(?:\uE202turn\d+(?:search|view|file)\d+)+\uE201/g;

/**
 * Normalize ChatGPT's LaTeX delimiters to standard KaTeX-compatible ones.
 * \[...\] → $$...$$ (display math)   \(...\) → $...$ (inline math)
 * Must run before remark-math sees the text.
 */
function preprocess(text: string): string {
    let result = text.replace(CITATION_RE, "");

    // Display math: \[...\] → $$...$$
    result = result.replace(/\\\[([\s\S]*?)\\\]/g, (_match, inner) => `$$${inner}$$`);
    // Inline math: \(...\) → $...$
    result = result.replace(/\\\(([\s\S]*?)\\\)/g, (_match, inner) => `$${inner}$`);

    return result;
}

function CopyButton({ text }: { text: string }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = useCallback(() => {
        navigator.clipboard.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    }, [text]);

    return (
        <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1 rounded px-1.5 py-0.5 font-sans text-[10px] font-semibold uppercase tracking-widest text-slate-500 transition-colors hover:text-slate-300"
            aria-label={copied ? "Copied" : "Copy code"}
        >
            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            {copied ? "Copied" : "Copy"}
        </button>
    );
}

function extractTextContent(children: ReactNode): string {
    if (typeof children === "string") return children;
    if (Array.isArray(children)) return children.map(extractTextContent).join("");
    if (children && typeof children === "object" && "props" in children) {
        return extractTextContent((children as { props: { children?: ReactNode } }).props.children);
    }
    return String(children ?? "");
}

export function MarkdownRenderer({ text }: { text: string }) {
    const processed = preprocess(text);

    return (
        <div className="space-y-2 text-[14px] leading-[1.55] text-foreground" data-testid="markdown-renderer">
            <ReactMarkdown
                remarkPlugins={[remarkBreaks, remarkMath]}
                rehypePlugins={[[rehypeKatex, { throwOnError: false, errorColor: "var(--color-muted-foreground)" }]]}
                components={{
                    h1: ({ children }) => (
                        <h1 className="text-[17px] font-semibold leading-tight tracking-tight text-foreground">{children}</h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-[15px] font-semibold leading-tight tracking-tight text-foreground">{children}</h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-[14px] font-semibold leading-tight tracking-tight text-foreground">{children}</h3>
                    ),
                    p: ({ children }) => <p className="whitespace-pre-wrap">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc space-y-0.5 pl-4.5">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal space-y-0.5 pl-4.5">{children}</ol>,
                    li: ({ children }) => <li className="pl-0.5">{children}</li>,
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-2 border-border pl-3 italic text-muted-foreground">
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
                    pre: ({ children }) => {
                        const codeText = extractTextContent(children);
                        // Extract language from the child <code> element's className
                        let language: string | null = null;
                        if (children && typeof children === "object" && "props" in children) {
                            const codeClass = (children as { props: { className?: string } }).props.className;
                            if (codeClass) {
                                const match = codeClass.match(/language-(\w+)/);
                                if (match) language = match[1];
                            }
                        }

                        return (
                            <div className="group relative overflow-hidden rounded-lg bg-slate-950" data-testid="code-block">
                                <div className="flex items-center justify-between bg-slate-800 px-3.5 py-1">
                                    <span className="font-mono text-[11px] text-slate-400">
                                        {language || "text"}
                                    </span>
                                    <CopyButton text={codeText} />
                                </div>
                                <pre className="overflow-x-auto px-3.5 py-2.5 text-[12px] leading-[1.6] text-slate-200">
                                    <code className="font-mono">{codeText}</code>
                                </pre>
                            </div>
                        );
                    },
                    code: ({ children, className }) => (
                        <code
                            className={
                                className
                                    ? `${className} font-mono text-[13px]`
                                    : "rounded bg-muted px-1.5 py-0.5 font-mono text-[0.88em] text-foreground"
                            }
                        >
                            {children}
                        </code>
                    ),
                }}
            >
                {processed}
            </ReactMarkdown>
        </div>
    );
}