"use client";

import React, { useEffect, useRef, useState } from "react";

type HoverTarget = HTMLElement | null;

interface TooltipState {
  visible: boolean;
  content: string;
  top: number;
  left: number;
}

function getAssociatedLabelText(el: HTMLElement): string | null {
  // 1) ラベルで囲まれているケース: <label>...<input/></label>
  const closestLabel = el.closest("label");
  if (closestLabel && closestLabel.textContent) {
    const txt = closestLabel.textContent.trim();
    if (txt) return txt;
  }
  // 2) for属性で関連付けられているケース: <label for="id">テキスト</label>
  const id = el.getAttribute("id");
  if (id) {
    const byFor = document.querySelector(`label[for="${CSS.escape(id)}"]`);
    if (byFor && byFor.textContent) {
      const txt = byFor.textContent.trim();
      if (txt) return txt;
    }
  }
  return null;
}

function getByAriaRefs(el: HTMLElement, attr: string): string | null {
  const ref = el.getAttribute(attr);
  if (!ref) return null;
  const ids = ref.split(/\s+/).filter(Boolean);
  const parts: string[] = [];
  for (const refId of ids) {
    const node = document.getElementById(refId);
    if (node && node.textContent) {
      const txt = node.textContent.trim();
      if (txt) parts.push(txt);
    }
  }
  if (parts.length > 0) return parts.join(" \u00B7 ");
  return null;
}

function getHelpText(element: HTMLElement | null): string | null {
  let current: HTMLElement | null = element;
  while (current) {
    // 優先: data-help / data-tooltip
    const fromData =
      current.getAttribute("data-help") || current.getAttribute("data-tooltip");
    if (fromData && fromData.trim()) return fromData.trim();

    // ARIA: aria-label（既存）/ aria-description / aria-labelledby / aria-describedby
    const ariaLabel = current.getAttribute("aria-label");
    if (ariaLabel && ariaLabel.trim()) return ariaLabel.trim();

    const ariaDescription =
      current.getAttribute("aria-description") ||
      current.getAttribute("aria-description" as any);
    if (ariaDescription && ariaDescription.trim()) return ariaDescription.trim();

    const viaLabelledby = getByAriaRefs(current, "aria-labelledby");
    if (viaLabelledby) return viaLabelledby;
    const viaDescribedby = getByAriaRefs(current, "aria-describedby");
    if (viaDescribedby) return viaDescribedby;

    // placeholder（入力系）
    const placeholder = current.getAttribute("placeholder");
    if (placeholder && placeholder.trim()) return placeholder.trim();

    // alt（画像/アイコン）
    const alt = current.getAttribute("alt");
    if (alt && alt.trim()) return alt.trim();

    // 関連ラベル（label要素）
    const labelText = getAssociatedLabelText(current);
    if (labelText) return labelText;

    // title（最後のフォールバック: ネイティブtitleツールチップ重複の可能性あり）
    const title = current.getAttribute("title");
    if (title && title.trim()) return title.trim();

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


