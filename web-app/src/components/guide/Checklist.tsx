"use client";

import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, X } from 'lucide-react';
import { accessibilityUtils } from '../../lib/guide/accessibility';

interface ChecklistItem {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}

interface ChecklistProps {
  items: ChecklistItem[];
  onItemComplete: (itemId: string) => void;
  onItemReset: (itemId: string) => void;
  onComplete: () => void;
  className?: string;
}

export default function Checklist({ 
  items, 
  onItemComplete, 
  onItemReset, 
  onComplete, 
  className = '' 
}: ChecklistProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [completedCount, setCompletedCount] = useState(0);

  useEffect(() => {
    const completed = items.filter(item => item.completed).length;
    setCompletedCount(completed);
    
    // 全て完了した場合は自動で非表示
    if (completed === items.length) {
      setTimeout(() => {
        setIsVisible(false);
        onComplete();
      }, 2000);
    }
  }, [items, onComplete]);

  const handleItemClick = (item: ChecklistItem) => {
    if (item.completed) {
      onItemReset(item.id);
      accessibilityUtils.screenReader.announceChecklistItem(item.title, false);
    } else {
      onItemComplete(item.id);
      accessibilityUtils.screenReader.announceChecklistItem(item.title, true);
    }
  };

  if (!isVisible) return null;

  return (
    <div 
      className={`bg-white rounded-lg shadow-lg border border-gray-200 p-4 ${className}`}
      {...accessibilityUtils.generateAriaAttributes('checklist')}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-900">初回チェックリスト</h3>
          <div className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            {completedCount} / {items.length}
          </div>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
          aria-label="チェックリストを閉じる"
        >
          <X size={16} />
        </button>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.id}
            className={`flex items-start gap-3 p-2 rounded-md cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              item.completed 
                ? 'bg-green-50 hover:bg-green-100' 
                : 'bg-gray-50 hover:bg-gray-100'
            }`}
            onClick={() => handleItemClick(item)}
            role="listitem"
            tabIndex={0}
            aria-checked={item.completed}
            aria-label={`${item.title}: ${item.description}`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleItemClick(item);
              }
            }}
          >
            <div className="flex-shrink-0 mt-0.5">
              {item.completed ? (
                <CheckCircle size={16} className="text-green-600" />
              ) : (
                <Circle size={16} className="text-gray-400" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${
                item.completed ? 'text-green-800 line-through' : 'text-gray-900'
              }`}>
                {item.title}
              </p>
              <p className={`text-xs ${
                item.completed ? 'text-green-600' : 'text-gray-600'
              }`}>
                {item.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {completedCount === items.length && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle size={16} />
            <span className="text-sm font-medium">お疲れ様でした！</span>
          </div>
          <p className="text-xs text-green-600 mt-1">
            主要機能を理解できました。明日からは自動案内しません。
          </p>
        </div>
      )}
    </div>
  );
}

// 進捗バッジ（ヘッダー用）
export function ChecklistBadge({ 
  completedCount, 
  totalCount, 
  onClick 
}: { 
  completedCount: number; 
  totalCount: number; 
  onClick: () => void;
}) {
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
  const isCompleted = completedCount === totalCount;

  if (isCompleted) return null;

  return (
    <button
      onClick={onClick}
      className="relative flex items-center gap-2 px-3 py-1.5 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-full text-xs font-medium transition-colors"
      aria-label={`チェックリスト: ${completedCount}/${totalCount} 完了`}
    >
      <div className="flex items-center gap-1">
        <CheckCircle size={14} />
        <span>{completedCount}/{totalCount}</span>
      </div>
      
      {/* プログレスバー */}
      <div className="w-12 h-1 bg-blue-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-blue-600 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </button>
  );
}

// デフォルトチェックリスト項目
export const DEFAULT_CHECKLIST_ITEMS: ChecklistItem[] = [
  {
    id: 'dashboard-overview',
    title: 'ダッシュボードを1分で把握する',
    description: '今日の投資指示と主要KPIを確認',
    completed: false
  },
  {
    id: 'kpi-understanding',
    title: 'KPIの意味を理解する',
    description: 'MAE、R²、予測精度の解釈を習得',
    completed: false
  },
  {
    id: 'candidate-exploration',
    title: '銘柄カードから詳細に入る',
    description: '推奨銘柄の詳細分析を実行',
    completed: false
  },
  {
    id: 'settings-configuration',
    title: '通知先を設定する',
    description: '分析結果の通知設定を完了',
    completed: false
  }
];
