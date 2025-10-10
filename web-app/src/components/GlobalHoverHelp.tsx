"use client";

import React, { useEffect, useRef, useState } from "react";

type HoverTarget = HTMLElement | null;

interface TooltipState {
  visible: boolean;
  content: string;
  top: number;
  left: number;
}

function getHelpText(element: HTMLElement | null): string | null {
  let current: HTMLElement | null = element;
  while (current) {
    const help =
      current.getAttribute("data-help") ||
      current.getAttribute("data-tooltip") ||
      current.getAttribute("aria-label") ||
      current.getAttribute("title");
    if (help && help.trim().length > 0) return help.trim();
    current = current.parentElement;
  }
  return null;
}

export default function GlobalHoverHelp() {
  const [state, setState] = useState<TooltipState>({
    visible: false,
    content: "",
    top: 0,
    left: 0,
  });
  const targetRef = useRef<HoverTarget>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!targetRef.current) return;
      const viewportPadding = 8;
      const offset = 14;
      let nextTop = e.clientY + offset;
      let nextLeft = e.clientX + offset;

      // 画面端のはみ出しを簡易回避（右下基準）
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      if (nextLeft > vw - viewportPadding) nextLeft = vw - viewportPadding;
      if (nextTop > vh - viewportPadding) nextTop = vh - viewportPadding;

      setState((prev) => ({ ...prev, top: nextTop, left: nextLeft }));
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const helpText = getHelpText(target);
      if (!helpText) return;

      targetRef.current = target;
      if (timerRef.current) window.clearTimeout(timerRef.current);
      timerRef.current = window.setTimeout(() => {
        setState((prev) => ({ ...prev, visible: true, content: helpText }));
      }, 250);
    };

    const handleMouseOut = (e: MouseEvent) => {
      const related = e.relatedTarget as Node | null;
      const current = e.target as HTMLElement;
      // ツールチップ対象から完全に離れた場合のみ閉じる
      if (current && related && current.contains(related)) return;
      if (timerRef.current) window.clearTimeout(timerRef.current);
      timerRef.current = null;
      targetRef.current = null;
      setState((prev) => ({ ...prev, visible: false }));
    };

    const handleFocusIn = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      const helpText = getHelpText(target);
      if (!helpText) return;
      targetRef.current = target;
      setState((prev) => ({ ...prev, visible: true, content: helpText }));
    };

    const handleFocusOut = () => {
      targetRef.current = null;
      setState((prev) => ({ ...prev, visible: false }));
    };

    document.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.addEventListener("mouseover", handleMouseOver, { passive: true });
    document.addEventListener("mouseout", handleMouseOut, { passive: true });
    document.addEventListener("focusin", handleFocusIn);
    document.addEventListener("focusout", handleFocusOut);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove as any);
      document.removeEventListener("mouseover", handleMouseOver as any);
      document.removeEventListener("mouseout", handleMouseOut as any);
      document.removeEventListener("focusin", handleFocusIn as any);
      document.removeEventListener("focusout", handleFocusOut as any);
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div
      // fixed配置で全ページ共通に重ねる
      className={`pointer-events-none fixed z-[9999] transition-opacity duration-100 ${
        state.visible ? "opacity-100" : "opacity-0"
      }`}
      style={{ top: state.top, left: state.left }}
      aria-hidden={!state.visible}
    >
      {state.visible && (
        <div className="max-w-[320px] rounded-md border border-border bg-popover px-3 py-2 text-sm text-popover-foreground shadow-md">
          <div className="whitespace-pre-wrap leading-relaxed">{state.content}</div>
        </div>
      )}
    </div>
  );
}


