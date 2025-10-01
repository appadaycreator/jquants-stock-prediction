"use client";

import React from "react";
import { useAccessibility } from "./AccessibilityProvider";
import { 
  Eye, 
  Type, 
  Zap, 
  Palette, 
  Volume2, 
  Settings,
  Contrast,
  Text,
  Move,
  Droplets,
  Speaker,
} from "lucide-react";

const AccessibilitySettings: React.FC = () => {
  const {
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
  } = useAccessibility();

  const fontSizeOptions = [
    { value: 14, label: "小" },
    { value: 16, label: "標準" },
    { value: 18, label: "大" },
    { value: 20, label: "特大" },
    { value: 22, label: "最大" },
  ];

  return (
    <div className="accessibility-settings">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-themed-primary">アクセシビリティ設定</h3>
        <Settings className="h-5 w-5 text-themed-secondary" />
      </div>
      
      <div className="space-y-6">
        {/* 視覚設定 */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-themed-primary flex items-center">
            <Eye className="h-4 w-4 mr-2" />
            視覚設定
          </h4>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3">
                <Contrast className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">高コントラストモード</div>
                  <div className="text-sm text-themed-text-secondary">文字と背景のコントラストを高めます</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={highContrast}
                onChange={(e) => setHighContrast(e.target.checked)}
                className="w-4 h-4 text-themed-primary bg-themed-surface border-themed-border rounded focus:ring-themed-border-focus"
              />
            </label>

            <label className="flex items-center justify-between p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3">
                <Text className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">大きなテキスト</div>
                  <div className="text-sm text-themed-text-secondary">テキストサイズを大きくします</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={largeText}
                onChange={(e) => setLargeText(e.target.checked)}
                className="w-4 h-4 text-themed-primary bg-themed-surface border-themed-border rounded focus:ring-themed-border-focus"
              />
            </label>

            <div className="p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3 mb-3">
                <Type className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">フォントサイズ</div>
                  <div className="text-sm text-themed-text-secondary">テキストのサイズを調整します</div>
                </div>
              </div>
              <div className="flex space-x-2">
                {fontSizeOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setFontSize(option.value)}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      fontSize === option.value
                        ? "bg-themed-primary text-themed-text-inverse"
                        : "bg-themed-surface text-themed-text-secondary hover:bg-themed-background-tertiary"
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 動作設定 */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-themed-primary flex items-center">
            <Move className="h-4 w-4 mr-2" />
            動作設定
          </h4>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3">
                <Zap className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">アニメーション削減</div>
                  <div className="text-sm text-themed-text-secondary">アニメーションを最小限に抑えます</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={reducedMotion}
                onChange={(e) => setReducedMotion(e.target.checked)}
                className="w-4 h-4 text-themed-primary bg-themed-surface border-themed-border rounded focus:ring-themed-border-focus"
              />
            </label>
          </div>
        </div>

        {/* 色覚設定 */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-themed-primary flex items-center">
            <Palette className="h-4 w-4 mr-2" />
            色覚設定
          </h4>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3">
                <Droplets className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">色覚障害対応モード</div>
                  <div className="text-sm text-themed-text-secondary">色だけでなくパターンでも区別します</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={colorBlindMode}
                onChange={(e) => setColorBlindMode(e.target.checked)}
                className="w-4 h-4 text-themed-primary bg-themed-surface border-themed-border rounded focus:ring-themed-border-focus"
              />
            </label>
          </div>
        </div>

        {/* 音声設定 */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-themed-primary flex items-center">
            <Speaker className="h-4 w-4 mr-2" />
            音声設定
          </h4>
          
          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 bg-themed-background-secondary rounded-lg">
              <div className="flex items-center space-x-3">
                <Volume2 className="h-4 w-4 text-themed-secondary" />
                <div>
                  <div className="font-medium text-themed-primary">スクリーンリーダー対応</div>
                  <div className="text-sm text-themed-text-secondary">音声読み上げソフトに対応します</div>
                </div>
              </div>
              <input
                type="checkbox"
                checked={screenReader}
                onChange={(e) => setScreenReader(e.target.checked)}
                className="w-4 h-4 text-themed-primary bg-themed-surface border-themed-border rounded focus:ring-themed-border-focus"
              />
            </label>
          </div>
        </div>

        {/* 設定のリセット */}
        <div className="pt-4 border-t border-themed-border">
          <button
            onClick={() => {
              setHighContrast(false);
              setLargeText(false);
              setReducedMotion(false);
              setColorBlindMode(false);
              setFontSize(16);
              setScreenReader(false);
            }}
            className="w-full px-4 py-2 text-themed-text-secondary hover:text-themed-text-primary transition-colors"
          >
            設定をリセット
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccessibilitySettings;
