import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import { unified } from "unified";
import { visit } from "unist-util-visit";

export function parseMarkdownTree(markdown: string): any {
  const processor = unified().use(remarkParse).use(remarkGfm);
  const tree = processor.parse(markdown);
  return processor.runSync(tree);
}

export function markdownToPlainText(markdown: string): string {
  const tree = parseMarkdownTree(markdown);
  const parts: string[] = [];

  visit(tree, (node: any) => {
    if (node.type === "text" || node.type === "inlineCode" || node.type === "code") {
      parts.push(String(node.value ?? ""));
    }
  });

  return parts.join(" ").replace(/\s+/g, " ").trim();
}

export function firstParagraphText(markdown: string): string {
  const tree = parseMarkdownTree(markdown);
  const paragraph = Array.isArray(tree.children)
    ? tree.children.find((node: any) => node.type === "paragraph")
    : null;

  if (!paragraph) {
    return markdownToPlainText(markdown);
  }

  return markdownToPlainText(stringifyNode(paragraph));
}

export function extractSectionMarkdown(markdown: string, sectionTitle: string): string | null {
  const lines = markdown.split(/\r?\n/);
  const heading = `### ${sectionTitle}`.toLowerCase();
  let startIndex = -1;

  for (let index = 0; index < lines.length; index += 1) {
    if ((lines[index] ?? "").trim().toLowerCase() === heading) {
      startIndex = index + 1;
      break;
    }
  }

  if (startIndex < 0) {
    return null;
  }

  let endIndex = lines.length;
  for (let index = startIndex; index < lines.length; index += 1) {
    if ((lines[index] ?? "").startsWith("### ")) {
      endIndex = index;
      break;
    }
  }

  return lines.slice(startIndex, endIndex).join("\n").trim();
}

function stringifyNode(node: any): string {
  if (typeof node.value === "string") {
    return node.value;
  }

  if (!Array.isArray(node.children)) {
    return "";
  }

  return node.children.map((child: any) => stringifyNode(child)).join("");
}
