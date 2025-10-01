"use client";

import React, { useState } from "react";
import { useTheme } from "@/contexts/ThemeContext";
import { useAccessibility } from "./AccessibilityProvider";
import ThemeSelector from "./ThemeSelector";
import AccessibilitySettings from "./AccessibilitySettings";
import EnhancedHelpGuide from "./EnhancedHelpGuide";
import { 
  Palette, 
  Settings, 
  HelpCircle, 
  Eye, 
  Type, 
  Move,
  Droplets,
  Speaker,
  X,
} from "lucide-react";

const UIUXIntegration: React.FC = () => {
  const [showThemeSelector, setShowThemeSelector] = useState(false);
  const [showAccessibilitySettings, setShowAccessibilitySettings] = useState(false);
  const [showHelpGuide, setShowHelpGuide] = useState(false);

  const { theme } = useTheme();
  const { highContrast, largeText, reducedMotion, colorBlindMode, screenReader } = useAccessibility();

  return (
    <>
      {/* UI/UX設定ボタン */}
      <div className="fixed bottom-4 right-4 z-40">
        <div className="flex flex-col space-y-2">
          {/* テーマ設定 */}
          <button
            onClick={() => setShowThemeSelector(true)}
            className="p-3 bg-themed-primary text-themed-text-inverse rounded-full shadow-lg hover:bg-themed-primary-hover transition-colors"
            title="テーマ設定"
            aria-label="テーマ設定を開く"
          >
            <Palette className="h-5 w-5" />
          </button>

          {/* アクセシビリティ設定 */}
          <button
            onClick={() => setShowAccessibilitySettings(true)}
            className="p-3 bg-themed-secondary text-themed-text-inverse rounded-full shadow-lg hover:bg-themed-secondary-hover transition-colors"
            title="アクセシビリティ設定"
            aria-label="アクセシビリティ設定を開く"
          >
            <Settings className="h-5 w-5" />
          </button>

          {/* ヘルプガイド */}
          <button
            onClick={() => setShowHelpGuide(true)}
            className="p-3 bg-themed-accent text-themed-text-inverse rounded-full shadow-lg hover:bg-themed-accent-hover transition-colors"
            title="使い方ガイド"
            aria-label="使い方ガイドを開く"
          >
            <HelpCircle className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* アクセシビリティ状態インジケーター */}
      {(highContrast || largeText || reducedMotion || colorBlindMode || screenReader) && (
        <div className="fixed top-4 right-4 z-30">
          <div className="bg-themed-background-secondary border border-themed-border rounded-lg p-2 shadow-lg">
            <div className="flex items-center space-x-2 text-themed-text-secondary text-sm">
              <Eye className="h-4 w-4" />
              <span>アクセシビリティ設定が有効</span>
            </div>
          </div>
        </div>
      )}

      {/* テーマセレクターモーダル */}
      {showThemeSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-themed-surface rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-themed-border">
              <h2 className="text-xl font-bold text-themed-primary">テーマ設定</h2>
              <button
                onClick={() => setShowThemeSelector(false)}
                className="text-themed-text-secondary hover:text-themed-text-primary transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="p-6">
              <ThemeSelector />
            </div>
          </div>
        </div>
      )}

      {/* アクセシビリティ設定モーダル */}
      {showAccessibilitySettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-themed-surface rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-themed-border">
              <h2 className="text-xl font-bold text-themed-primary">アクセシビリティ設定</h2>
              <button
                onClick={() => setShowAccessibilitySettings(false)}
                className="text-themed-text-secondary hover:text-themed-text-primary transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="p-6">
              <AccessibilitySettings />
            </div>
          </div>
        </div>
      )}

      {/* ヘルプガイドモーダル */}
      <EnhancedHelpGuide
        isOpen={showHelpGuide}
        onClose={() => setShowHelpGuide(false)}
      />
    </>
  );
};

export default UIUXIntegration;
