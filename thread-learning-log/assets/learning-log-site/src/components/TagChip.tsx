interface TagChipProps {
  tag: string;
  onClick: (tag: string) => void;
  isActive?: boolean;
}

export function TagChip(props: TagChipProps) {
  const { tag, onClick, isActive = false } = props;

  return (
    <button
      type="button"
      className="tag-chip"
      data-active={isActive ? "true" : "false"}
      onClick={() => onClick(tag)}
      aria-pressed={isActive}
    >
      {tag}
    </button>
  );
}
