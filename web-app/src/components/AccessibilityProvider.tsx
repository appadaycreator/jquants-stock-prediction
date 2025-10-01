"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

interface AccessibilityContextType {
  highContrast: boolean;
  setHighContrast: (value: boolean) => void;
  largeText: boolean;
  setLargeText: (value: boolean) => void;
  reducedMotion: boolean;
  setReducedMotion: (value: boolean) => void;
  colorBlindMode: boolean;
  setColorBlindMode: (value: boolean) => void;
  fontSize: number;
  setFontSize: (value: number) => void;
  screenReader: boolean;
  setScreenReader: (value: boolean) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error("useAccessibility must be used within an AccessibilityProvider");
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [colorBlindMode, setColorBlindMode] = useState(false);
  const [fontSize, setFontSize] = useState(16);
  const [screenReader, setScreenReader] = useState(false);

  // ローカルストレージから設定を読み込み
  useEffect(() => {
    const savedSettings = localStorage.getItem("accessibility-settings");
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        setHighContrast(settings.highContrast || false);
        setLargeText(settings.largeText || false);
        setReducedMotion(settings.reducedMotion || false);
        setColorBlindMode(settings.colorBlindMode || false);
        setFontSize(settings.fontSize || 16);
        setScreenReader(settings.screenReader || false);
      } catch (error) {
        console.warn("Failed to load accessibility settings:", error);
      }
    }

    // システム設定を確認
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReducedMotion(prefersReducedMotion);
  }, []);

  // 設定変更時にローカルストレージに保存
  useEffect(() => {
    const settings = {
      highContrast,
      largeText,
      reducedMotion,
      colorBlindMode,
      fontSize,
      screenReader,
    };
    localStorage.setItem("accessibility-settings", JSON.stringify(settings));
  }, [highContrast, largeText, reducedMotion, colorBlindMode, fontSize, screenReader]);

  // アクセシビリティ設定をHTMLに適用
  useEffect(() => {
    const root = document.documentElement;
    
    // 高コントラストモード
    if (highContrast) {
      root.classList.add("high-contrast-mode");
    } else {
      root.classList.remove("high-contrast-mode");
    }

    // 大きなテキスト
    if (largeText) {
      root.classList.add("large-text-mode");
    } else {
      root.classList.remove("large-text-mode");
    }

    // アニメーション削減
    if (reducedMotion) {
      root.classList.add("reduced-motion-mode");
    } else {
      root.classList.remove("reduced-motion-mode");
    }

    // 色覚障害モード
    if (colorBlindMode) {
      root.classList.add("colorblind-mode");
    } else {
      root.classList.remove("colorblind-mode");
    }

    // フォントサイズ
    root.style.fontSize = `${fontSize}px`;

    // スクリーンリーダー
    if (screenReader) {
      root.classList.add("screen-reader-mode");
    } else {
      root.classList.remove("screen-reader-mode");
    }
  }, [highContrast, largeText, reducedMotion, colorBlindMode, fontSize, screenReader]);

  return (
    <AccessibilityContext.Provider
      value={{
        highContrast,
        setHighContrast,
        largeText,
        setLargeText,
        reducedMotion,
        setReducedMotion,
        colorBlindMode,
        setColorBlindMode,
        fontSize,
        setFontSize,
        screenReader,
        setScreenReader,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};
