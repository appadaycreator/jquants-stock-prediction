"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type Theme = "light" | "dark" | "auto" | "blue" | "green" | "purple";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
  effectiveTheme: "light" | "dark";
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>("auto");
  const [systemPrefersDark, setSystemPrefersDark] = useState(false);

  // システム設定の変更を監視
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    setSystemPrefersDark(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setSystemPrefersDark(e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  // ローカルストレージからテーマを読み込み
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as Theme;
    if (savedTheme && ["light", "dark", "auto", "blue", "green", "purple"].includes(savedTheme)) {
      setThemeState(savedTheme);
    } else {
      setThemeState("auto");
    }
  }, []);

  // テーマ変更時にローカルストレージに保存
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem("theme", newTheme);
  };

  // ダークモードの切り替え
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : theme === "dark" ? "auto" : "light";
    setTheme(newTheme);
  };

  // 実際に適用されるテーマを計算
  const effectiveTheme = theme === "auto" 
    ? (systemPrefersDark ? "dark" : "light")
    : theme === "blue" || theme === "green" || theme === "purple"
    ? "light" // カラーテーマはライトベース
    : theme as "light" | "dark";

  const isDark = effectiveTheme === "dark";

  // テーマが変更されたときにHTMLクラスを更新
  useEffect(() => {
    const root = document.documentElement;
    
    // 既存のテーマクラスを削除
    root.classList.remove("theme-light", "theme-dark", "theme-blue", "theme-green", "theme-purple");
    
    // 新しいテーマクラスを追加
    root.classList.add(`theme-${theme}`);
    
    // データ属性も設定
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-effective-theme", effectiveTheme);
  }, [theme, effectiveTheme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, isDark, effectiveTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
