interface MetadataListProps {
  metadata: Record<string, unknown>;
}

export function MetadataList(props: MetadataListProps) {
  const entries = Object.entries(props.metadata);

  if (!entries.length) {
    return null;
  }

  return (
    <dl className="metadata-list">
      {entries.map(([key, value]) => (
        <div key={key} className="metadata-row">
          <dt>{humanizeLabel(key)}</dt>
          <dd>{renderMetadataValue(value, `${key}-value`)}</dd>
        </div>
      ))}
    </dl>
  );
}

function renderMetadataValue(value: unknown, keyPrefix: string): any {
  if (Array.isArray(value)) {
    return (
      <ul className="metadata-value-list">
        {value.map((item, index) => (
          <li key={`${keyPrefix}-${index}`}>{renderMetadataValue(item, `${keyPrefix}-${index}`)}</li>
        ))}
      </ul>
    );
  }

  if (typeof value === "string") {
    if (/^https?:\/\//.test(value)) {
      return (
        <a href={value} target="_blank" rel="noreferrer">
          {value}
        </a>
      );
    }

    if (value.startsWith("/")) {
      return <code>{value}</code>;
    }

    return value;
  }

  if (value && typeof value === "object") {
    return <code>{JSON.stringify(value)}</code>;
  }

  return String(value);
}

function humanizeLabel(label: string): string {
  return label.replace(/_/g, " ");
}
