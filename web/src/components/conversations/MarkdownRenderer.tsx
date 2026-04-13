import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useState, useCallback, Fragment, type ReactNode, type CSSProperties } from "react";
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

// Token node shape emitted by react-syntax-highlighter's internal renderer API.
// All token elements in Prism output are <span> tags, so tagName is always "span".
// value is string | number to match RSH's rendererNode type exactly.
interface SyntaxToken {
    type: "element" | "text";
    value?: string | number;
    tagName?: string;
    properties?: { className?: string[]; [key: string]: unknown };
    children?: SyntaxToken[];
}

// Recursively render an RSH token tree to React elements, resolving inline
// styles from the theme stylesheet keyed by CSS class name.
function renderTokens(
    nodes: SyntaxToken[],
    stylesheet: Record<string, CSSProperties>
): ReactNode {
    return nodes.map((node, i) => {
        if (node.type === "text") return node.value ?? null;
        const style = (node.properties?.className ?? []).reduce<CSSProperties>(
            (acc, cls) => ({ ...acc, ...(stylesheet[cls] ?? {}) }),
            {}
        );
        return (
            <span key={i} style={Object.keys(style).length ? style : undefined}>
                {node.children ? renderTokens(node.children, stylesheet) : null}
            </span>
        );
    });
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

                        // Strip the trailing newline that fenced code blocks produce so RSH
                        // does not emit a spurious empty final row in the renderer.
                        const codeForHighlighter = codeText.endsWith("\n")
                            ? codeText.slice(0, -1)
                            : codeText;

                        return (
                            <div className="group relative mt-4 overflow-hidden rounded-lg bg-slate-950" data-testid="code-block">
                                <div className="flex items-center justify-between bg-slate-800 px-3.5 pb-1 pt-2">
                                    <span className="font-mono text-[11px] text-slate-400">
                                        {language || "text"}
                                    </span>
                                    <CopyButton text={codeText} />
                                </div>
                                <SyntaxHighlighter
                                    language={language || "text"}
                                    style={oneDark}
                                    PreTag="div"
                                    showLineNumbers={false}
                                    className=""
                                    // customStyle must stay inline: RSH injects inline styles on the PreTag.
                                    // padding: 0 — the renderer's grid cells own all spacing.
                                    customStyle={{ margin: 0, padding: 0, borderRadius: 0, background: "transparent" }}
                                    // code-block-code sets font-family, font-size: 13px, line-height: 1.75.
                                    // display: block makes the <code> element a block-level grid container.
                                    codeTagProps={{ className: "code-block-code", style: { display: "block" } }}
                                    // Custom renderer: one CSS grid row per logical code line.
                                    // Grid row height expands automatically for wrapped lines; the gutter
                                    // cell stretches (align-self: stretch is CSS grid's default) so the
                                    // #1a2332 background always fills the full height of the row — no gaps.
                                    // The line number is positioned at the top of each cell via flex-start.
                                    renderer={(props) => {
                                        const rows = props.rows as SyntaxToken[];
                                        const stylesheet = props.stylesheet as Record<string, CSSProperties>;
                                        const total = rows.length;
                                        // Widen the gutter column once line numbers reach 3 digits
                                        const gutterW = total >= 100 ? "3.5em" : "2.5em";
                                        return (
                                            <div
                                                data-testid="line-number-gutter"
                                                style={{
                                                    display: "grid",
                                                    gridTemplateColumns: `${gutterW} 1fr`,
                                                }}
                                            >
                                                {rows.map((row, i) => (
                                                    <Fragment key={i}>
                                                        {/* Gutter cell: stretches to full row height via CSS grid default */}
                                                        <div
                                                            aria-hidden="true"
                                                            style={{
                                                                backgroundColor: "#1a2332",
                                                                color: "#4b5a6e",
                                                                fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                                                                fontSize: "11px",
                                                                // Fixed-px line-height = 13px × 1.75 so numbers
                                                                // align with the first visual row of each code line.
                                                                lineHeight: "22.75px",
                                                                // Top/bottom padding only on the first/last rows so
                                                                // the gutter background fills flush to the block edges.
                                                                paddingTop: i === 0 ? "10px" : undefined,
                                                                paddingBottom: i === total - 1 ? "10px" : undefined,
                                                                paddingLeft: "8px",
                                                                paddingRight: "10px",
                                                                display: "flex",
                                                                alignItems: "flex-start",
                                                                justifyContent: "flex-end",
                                                                userSelect: "none",
                                                            }}
                                                        >
                                                            {i + 1}
                                                        </div>
                                                        {/* Code cell: inherits font/size/leading from .code-block-code */}
                                                        <div
                                                            style={{
                                                                paddingTop: i === 0 ? "10px" : undefined,
                                                                paddingBottom: i === total - 1 ? "10px" : undefined,
                                                                paddingLeft: "14px",
                                                                paddingRight: "14px",
                                                                whiteSpace: "pre-wrap",
                                                                overflowWrap: "break-word",
                                                            }}
                                                        >
                                                            {row.children
                                                                ? renderTokens(row.children, stylesheet)
                                                                : null}
                                                        </div>
                                                    </Fragment>
                                                ))}
                                            </div>
                                        );
                                    }}
                                >
                                    {codeForHighlighter}
                                </SyntaxHighlighter>
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