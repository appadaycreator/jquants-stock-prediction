"use client";

import React from "react";
import { useTheme } from "@/contexts/ThemeContext";

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme() as any;
  const label = theme === "dark" ? "ダーク" : theme === "auto" ? "自動" : "ライト";
  const icon = theme === "dark" ? "🌙" : theme === "auto" ? "🔄" : "☀️";
  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">テーマ:</span>
      <button
        onClick={() => toggleTheme?.()}
        className="flex items-center space-x-2 px-3 py-1.5 rounded-md text-sm font-medium bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
        title="テーマを切り替え"
      >
        <span className="text-base">{icon}</span>
        <span>{label}</span>
      </button>
    </div>
  );
};

export default ThemeToggle;
