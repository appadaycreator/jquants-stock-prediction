"use client";

import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { Palette, Sun, Moon, Droplets, Leaf, Sparkles } from 'lucide-react';

const ThemeSelector: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const themes = [
    { id: 'light', name: 'ライト', icon: Sun, description: '明るく清潔なデザイン' },
    { id: 'dark', name: 'ダーク', icon: Moon, description: '目に優しい暗いテーマ' },
    { id: 'blue', name: 'ブルー', icon: Droplets, description: '信頼感のある青系テーマ' },
    { id: 'green', name: 'グリーン', icon: Leaf, description: '自然で落ち着いた緑系テーマ' },
    { id: 'purple', name: 'パープル', icon: Sparkles, description: '創造性を感じる紫系テーマ' },
  ] as const;

  return (
    <div className="theme-selector">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-themed-primary">テーマ設定</h3>
        <Palette className="h-5 w-5 text-themed-secondary" />
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {themes.map(({ id, name, icon: Icon, description }) => (
          <button
            key={id}
            onClick={() => setTheme(id as any)}
            className={`
              relative p-4 rounded-lg border-2 transition-all duration-200
              ${theme === id 
                ? 'border-themed-primary bg-themed-primary-light' 
                : 'border-themed-border hover:border-themed-border-hover bg-themed-surface'
              }
            `}
            aria-pressed={theme === id}
            aria-label={`${name}テーマを選択`}
          >
            <div className="flex items-center space-x-3">
              <div className={`
                p-2 rounded-lg
                ${theme === id 
                  ? 'bg-themed-primary text-themed-text-inverse' 
                  : 'bg-themed-background-secondary text-themed-text-secondary'
                }
              `}>
                <Icon className="h-4 w-4" />
              </div>
              
              <div className="text-left flex-1">
                <div className="font-medium text-themed-primary">{name}</div>
                <div className="text-sm text-themed-text-secondary">{description}</div>
              </div>
              
              {theme === id && (
                <div className="absolute top-2 right-2">
                  <div className="w-2 h-2 bg-themed-primary rounded-full"></div>
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-themed-background-secondary rounded-lg">
        <div className="text-sm text-themed-text-secondary">
          <strong>現在のテーマ:</strong> {themes.find(t => t.id === theme)?.name}
        </div>
        <div className="text-xs text-themed-text-tertiary mt-1">
          テーマは自動的に保存され、次回アクセス時にも適用されます。
        </div>
      </div>
    </div>
  );
};

export default ThemeSelector;
