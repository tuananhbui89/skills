import React from "react";

import { parseMarkdownTree } from "../lib/markdown";

interface MarkdownRendererProps {
  markdown: string;
}

export function MarkdownRenderer(props: MarkdownRendererProps) {
  const tree = parseMarkdownTree(props.markdown);
  return <div className="markdown-body">{renderNode(tree, "root")}</div>;
}

function renderNode(node: any, key: string): any {
  switch (node.type) {
    case "root":
      return <>{renderChildren(node.children, key)}</>;
    case "heading": {
      const level = Math.min(Math.max(Number(node.depth ?? 1), 1), 6);
      const TagName = `h${level}` as "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
      return <TagName key={key}>{renderChildren(node.children, key)}</TagName>;
    }
    case "paragraph":
      return <p key={key}>{renderChildren(node.children, key)}</p>;
    case "text":
      return node.value;
    case "strong":
      return <strong key={key}>{renderChildren(node.children, key)}</strong>;
    case "emphasis":
      return <em key={key}>{renderChildren(node.children, key)}</em>;
    case "delete":
      return <del key={key}>{renderChildren(node.children, key)}</del>;
    case "blockquote":
      return <blockquote key={key}>{renderChildren(node.children, key)}</blockquote>;
    case "list": {
      const ListTag = node.ordered ? "ol" : "ul";
      return <ListTag key={key}>{renderChildren(node.children, key)}</ListTag>;
    }
    case "listItem":
      return <li key={key}>{renderChildren(node.children, key)}</li>;
    case "inlineCode":
      return <code key={key}>{node.value}</code>;
    case "code":
      return (
        <pre key={key}>
          <code>{node.value}</code>
        </pre>
      );
    case "link":
      return (
        <a key={key} href={node.url} target="_blank" rel="noreferrer">
          {renderChildren(node.children, key)}
        </a>
      );
    case "image":
      return <img key={key} src={node.url} alt={node.alt ?? ""} loading="lazy" />;
    case "thematicBreak":
      return <hr key={key} />;
    case "break":
      return <br key={key} />;
    case "table": {
      const rows = Array.isArray(node.children) ? node.children : [];
      const header = rows[0];
      const body = rows.slice(1);
      return (
        <div key={key} className="table-wrap">
          <table>
            {header ? <thead>{renderTableRow(header, `${key}-head`, true)}</thead> : null}
            {body.length ? <tbody>{body.map((row: any, index: number) => renderTableRow(row, `${key}-body-${index}`))}</tbody> : null}
          </table>
        </div>
      );
    }
    case "html":
      return null;
    default:
      return Array.isArray(node.children) ? <React.Fragment key={key}>{renderChildren(node.children, key)}</React.Fragment> : null;
  }
}

function renderChildren(children: any[] | undefined, keyPrefix: string): any[] {
  return (children ?? []).map((child, index) => renderNode(child, `${keyPrefix}-${index}`));
}

function renderTableRow(row: any, key: string, isHeader = false): any {
  const CellTag = isHeader ? "th" : "td";
  return (
    <tr key={key}>
      {(row.children ?? []).map((cell: any, index: number) => (
        <CellTag key={`${key}-${index}`}>{renderChildren(cell.children, `${key}-${index}`)}</CellTag>
      ))}
    </tr>
  );
}
