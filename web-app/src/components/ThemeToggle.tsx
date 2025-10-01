"use client";

import React from "react";
import { useTheme } from "@/contexts/ThemeContext";

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, effectiveTheme } = useTheme();

  const themes = [
    { value: "light", label: "ライト", icon: "☀️" },
    { value: "dark", label: "ダーク", icon: "🌙" },
    { value: "auto", label: "自動", icon: "🔄" },
  ] as const;

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        テーマ:
      </span>
      <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {themes.map(({ value, label, icon }) => (
          <button
            key={value}
            onClick={() => setTheme(value as any)}
            className={`
              flex items-center space-x-1 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200
              ${
                theme === value
                  ? "bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              }
            `}
            title={`${label}テーマに切り替え`}
          >
            <span className="text-base">{icon}</span>
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
      {theme === "auto" && (
        <span className="text-xs text-gray-500 dark:text-gray-400">
          ({effectiveTheme === "dark" ? "ダーク" : "ライト"})
        </span>
      )}
    </div>
  );
};

export default ThemeToggle;
