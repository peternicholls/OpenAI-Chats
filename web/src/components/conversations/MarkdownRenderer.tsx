import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useState, useCallback, useRef, Fragment, type ReactNode, type CSSProperties } from "react";
import { Check, Copy } from "lucide-react";

type SyntaxStylesheet = Record<string, CSSProperties>;

/**
 * Strip PUA citation tokens injected by ChatGPT's retrieval system.
 * Pattern: \uE200(file)?cite(\uE202turnNsearchM|\uE202turnNviewM|\uE202turnNfileM)+\uE201
 */
const CITATION_RE = /\uE200(?:file)?cite(?:\uE202turn\d+(?:search|view|file|news)\d+)+\uE201/g;

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

function getCodeLanguage(children: ReactNode): string | null {
    if (!children || typeof children !== "object" || !("props" in children)) {
        return null;
    }

    const codeClass = (children as { props: { className?: string } }).props.className;
    return codeClass?.match(/language-(\w+)/)?.[1] ?? null;
}

function stripTrailingCodeFenceNewline(text: string): string {
    return text.endsWith("\n") ? text.slice(0, -1) : text;
}

function getInlineCodeClassName(className?: string): string {
    return className
        ? `${className} font-mono text-[13px]`
        : "rounded bg-muted px-1.5 py-0.5 font-mono text-[0.88em] text-foreground";
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

function TableBlock({ children }: { children: ReactNode }) {
    const tableRef = useRef<HTMLTableElement>(null);
    const [copied, setCopied] = useState(false);

    const handleCopy = useCallback(() => {
        const text = tableRef.current?.innerText ?? extractTextContent(children);
        navigator.clipboard.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    }, [children]);

    return (
        <div className="group/table relative my-6" data-testid="table-block">
            <div className="overflow-x-auto">
                <table ref={tableRef} className="w-full border-collapse text-sm">
                    {children}
                </table>
            </div>
            <button
                type="button"
                onClick={handleCopy}
                className="absolute right-1 top-1 flex items-center gap-1 rounded px-1.5 py-0.5 font-sans text-[10px] font-semibold uppercase tracking-widest text-muted-foreground opacity-0 transition-opacity group-hover/table:opacity-100 hover:text-foreground"
                aria-label={copied ? "Copied" : "Copy table"}
            >
                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                {copied ? "Copied" : "Copy"}
            </button>
        </div>
    );
}

// Token node shape emitted by react-syntax-highlighter's internal renderer API.
// All token elements in Prism output are <span> tags, so tagName is always "span".
// value is string | number to match RSH's rendererNode type exactly.
interface SyntaxToken {
    type: "element" | "text";
    value?: string | number;
    tagName?: string;
    properties?: { className?: string[];[key: string]: unknown };
    children?: SyntaxToken[];
}

// Recursively render an RSH token tree to React elements, resolving inline
// styles from the theme stylesheet keyed by CSS class name.
function renderTokens(
    nodes: SyntaxToken[],
    stylesheet: SyntaxStylesheet
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
                remarkPlugins={[remarkGfm, remarkBreaks, remarkMath]}
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
                    ul: ({ children }) => <ul className="list-disc space-y-1.5 pl-4.5">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal space-y-1.5 pl-4.5">{children}</ol>,
                    li: ({ children }) => <li className="markdown-list-item pl-0.5">{children}</li>,
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
                    table: ({ children }) => <TableBlock>{children}</TableBlock>,
                    th: ({ children }) => (
                        <th className="border-b-2 border-border px-3 py-2 text-left text-xs font-semibold text-foreground">
                            {children}
                        </th>
                    ),
                    td: ({ children }) => (
                        <td className="border-b border-border/80 px-3 py-2.5 text-foreground">
                            {children}
                        </td>
                    ),
                    hr: () => (
                        <hr className="my-4 border-t border-border" />
                    ),
                    pre: ({ children }) => {
                        const codeText = extractTextContent(children);
                        const language = getCodeLanguage(children) ?? "text";
                        const codeForHighlighter = stripTrailingCodeFenceNewline(codeText);

                        return (
                            <div className="group relative mt-4 overflow-hidden rounded-lg bg-slate-950" data-testid="code-block">
                                <div className="flex items-center justify-between bg-slate-800 px-3.5 pb-1 pt-2">
                                    <span className="font-mono text-[11px] text-slate-400">
                                        {language}
                                    </span>
                                    <CopyButton text={codeText} />
                                </div>
                                <SyntaxHighlighter
                                    language={language}
                                    style={oneDark}
                                    PreTag="div"
                                    showLineNumbers={false}
                                    className=""
                                    customStyle={{ margin: 0, padding: 0, borderRadius: 0, background: "transparent" }}
                                    codeTagProps={{ className: "code-block-code", style: { display: "block" } }}
                                    renderer={(props) => {
                                        const rows = props.rows as SyntaxToken[];
                                        const stylesheet = props.stylesheet as SyntaxStylesheet;
                                        const total = rows.length;
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
                                                        <div
                                                            aria-hidden="true"
                                                            style={{
                                                                backgroundColor: "#1a2332",
                                                                color: "#4b5a6e",
                                                                fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                                                                fontSize: "11px",
                                                                lineHeight: "22.75px",
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
                        <code className={getInlineCodeClassName(className)}>
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