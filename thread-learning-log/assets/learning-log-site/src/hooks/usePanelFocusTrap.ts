import { useEffect } from "react";

const focusableSelector = [
  "button:not([disabled])",
  "[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(", ");

interface UsePanelFocusTrapOptions {
  active: boolean;
  containerRef: { current: HTMLElement | null };
  returnFocusRef?: { current: HTMLElement | null };
  onClose: () => void;
}

export function usePanelFocusTrap(options: UsePanelFocusTrapOptions) {
  const { active, containerRef, returnFocusRef, onClose } = options;

  useEffect(() => {
    if (!active) {
      return;
    }

    const container = containerRef.current;
    if (!container) {
      return;
    }

    const getFocusable = () =>
      [...container.querySelectorAll<HTMLElement>(focusableSelector)].filter((element) => !element.hasAttribute("hidden"));

    const focusableElements = getFocusable();
    const initialTarget = container.querySelector<HTMLElement>("[data-autofocus]") ?? focusableElements[0] ?? container;
    initialTarget.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== "Tab") {
        return;
      }

      const targets = getFocusable();
      if (targets.length === 0) {
        event.preventDefault();
        container.focus();
        return;
      }

      const currentIndex = targets.findIndex((element) => element === document.activeElement);
      const first = targets[0];
      const last = targets[targets.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === first || currentIndex === -1) {
          event.preventDefault();
          last.focus();
        }
        return;
      }

      if (document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      returnFocusRef?.current?.focus?.();
    };
  }, [active, containerRef, onClose, returnFocusRef]);
}
