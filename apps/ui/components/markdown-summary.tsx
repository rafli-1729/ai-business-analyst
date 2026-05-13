import { ReactNode } from "react";

type Props = {
  content: string;
};

function normalizeMarkdown(content: string) {
  return content
    .replace(/\s+(#{1,6}\s)/g, "\n\n$1")
    .replace(/\s+\|(?=\s*(?:[-:]{3,}|\d+|[A-Za-z]))/g, "\n|")
    .replace(/\s+-\s+(?=(?:\*\*)?[A-Z])/g, "\n- ");
}

function splitTableRow(line: string) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function isTableSeparator(line: string) {
  return /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(line.trim());
}

function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    return part;
  });
}

export function MarkdownSummary({ content }: Props) {
  const lines = normalizeMarkdown(content)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const blocks: ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];

    if (line.startsWith("### ")) {
      blocks.push(<h3 key={index}>{renderInline(line.slice(4))}</h3>);
      index += 1;
      continue;
    }

    if (line.startsWith("## ")) {
      blocks.push(<h2 key={index}>{renderInline(line.slice(3))}</h2>);
      index += 1;
      continue;
    }

    if (line.startsWith("# ")) {
      blocks.push(<h2 key={index}>{renderInline(line.slice(2))}</h2>);
      index += 1;
      continue;
    }

    if (line.startsWith("- ")) {
      const items: string[] = [];
      while (index < lines.length && lines[index].startsWith("- ")) {
        items.push(lines[index].slice(2));
        index += 1;
      }
      blocks.push(
        <ul key={index}>
          {items.map((item, itemIndex) => (
            <li key={itemIndex}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      continue;
    }

    if (line.startsWith("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
      const headers = splitTableRow(line);
      index += 2;
      const rows: string[][] = [];

      while (index < lines.length && lines[index].startsWith("|")) {
        rows.push(splitTableRow(lines[index]));
        index += 1;
      }

      blocks.push(
        <div className="markdownTableShell" key={index}>
          <table>
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header}>{renderInline(header)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {headers.map((_, cellIndex) => (
                    <td key={cellIndex}>{renderInline(row[cellIndex] ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    blocks.push(<p key={index}>{renderInline(line)}</p>);
    index += 1;
  }

  return <div className="markdownSummary">{blocks}</div>;
}
