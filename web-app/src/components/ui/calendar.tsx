/**
 * カレンダーコンポーネント
 */

import React from "react";

interface CalendarProps {
  mode?: "single" | "multiple" | "range";
  selected?: Date;
  onSelect?: (date: Date | undefined) => void;
  locale?: any;
  className?: string;
}

export function Calendar({ 
  mode = "single", 
  selected, 
  onSelect, 
  locale,
  className = "", 
}: CalendarProps) {
  return (
    <div className={`calendar ${className}`}>
      <div className="calendar-header">
        <button type="button">←</button>
        <span>2024年1月</span>
        <button type="button">→</button>
      </div>
      <div className="calendar-grid">
        <div className="calendar-weekdays">
          <div>日</div>
          <div>月</div>
          <div>火</div>
          <div>水</div>
          <div>木</div>
          <div>金</div>
          <div>土</div>
        </div>
        <div className="calendar-days">
          {/* 簡易的なカレンダー実装 */}
          {Array.from({ length: 31 }, (_, i) => i + 1).map(day => (
            <button
              key={day}
              type="button"
              className={`calendar-day ${selected?.getDate() === day ? "selected" : ""}`}
              onClick={() => onSelect?.(new Date(2024, 0, day))}
            >
              {day}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
