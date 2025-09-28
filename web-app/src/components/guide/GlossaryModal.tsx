"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, BookOpen, ExternalLink } from 'lucide-react';

interface GlossaryItem {
  term: string;
  short: string;
  detail: string;
  category: string;
  links?: string[];
}

interface GlossaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  items?: GlossaryItem[];
}

const DEFAULT_GLOSSARY_ITEMS: GlossaryItem[] = [
  {
    term: 'MAE',
    short: '平均絶対誤差',
    detail: 'Mean Absolute Error。予測値と実際値の差の絶対値の平均。値が小さいほど予測精度が高い。',
    category: '指標',
    links: ['/models', '/analysis']
  },
  {
    term: 'RMSE',
    short: '二乗平均平方根誤差',
    detail: 'Root Mean Square Error。予測値と実際値の差の二乗平均の平方根。MAEより大きな誤差に敏感。',
    category: '指標',
    links: ['/models', '/analysis']
  },
  {
    term: 'R²',
    short: '決定係数',
    detail: 'Coefficient of Determination。モデルがデータの変動を説明できる割合。1に近いほど良い。',
    category: '指標',
    links: ['/models', '/analysis']
  },
  {
    term: '予測精度',
    short: '予測の正確性',
    detail: '直近テスト期間での予測と実際の一致度。過去データへの過適合に注意が必要。',
    category: '指標',
    links: ['/predictions', '/analysis']
  },
  {
    term: 'シャープレシオ',
    short: 'リスク調整後リターン',
    detail: 'Sharpe Ratio。リスク1単位あたりのリターン。高いほど効率的な投資。',
    category: '指標',
    links: ['/risk', '/reports']
  },
  {
    term: '損切り',
    short: '損失を限定する売却',
    detail: 'Stop Loss。損失が一定水準に達した時の自動売却。リスク管理の基本。',
    category: '取引',
    links: ['/risk', '/settings']
  },
  {
    term: '利確',
    short: '利益を確定する売却',
    detail: 'Take Profit。利益が一定水準に達した時の自動売却。利益の確保。',
    category: '取引',
    links: ['/risk', '/settings']
  },
  {
    term: 'ボラティリティ',
    short: '価格変動の激しさ',
    detail: 'Volatility。価格の変動幅。高いほどリスクが大きい。',
    category: 'リスク',
    links: ['/risk', '/analysis']
  },
  {
    term: '過学習',
    short: '過去データに過度に適合',
    detail: 'Overfitting。過去データに特化しすぎて将来予測ができない状態。',
    category: 'モデル',
    links: ['/models', '/analysis']
  },
  {
    term: '特徴量重要度',
    short: '予測に影響する要因の重み',
    detail: 'Feature Importance。どの要因が予測に最も影響するかの指標。',
    category: '分析',
    links: ['/analysis']
  },
  {
    term: '残差分析',
    short: '予測誤差の分析',
    detail: 'Residual Analysis。予測値と実際値の差のパターンを分析。',
    category: '分析',
    links: ['/analysis']
  },
  {
    term: '相関分析',
    short: '要因間の関係性分析',
    detail: 'Correlation Analysis。複数の要因がどの程度関連するかの分析。',
    category: '分析',
    links: ['/analysis']
  }
];

export default function GlossaryModal({ 
  isOpen, 
  onClose, 
  items = DEFAULT_GLOSSARY_ITEMS 
}: GlossaryModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('すべて');
  const [selectedItem, setSelectedItem] = useState<GlossaryItem | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const categories = ['すべて', ...Array.from(new Set(items.map(item => item.category)))];

  const filteredItems = items.filter(item => {
    const matchesSearch = item.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.short.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.detail.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'すべて' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <BookOpen size={24} className="text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">用語集</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="用語集を閉じる"
          >
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* サイドバー */}
          <div className="w-1/3 border-r border-gray-200 flex flex-col">
            {/* 検索 */}
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="用語を検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* カテゴリフィルター */}
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-900 mb-2">カテゴリ</h3>
              <div className="space-y-1">
                {categories.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`w-full text-left px-3 py-1.5 text-sm rounded-md transition-colors ${
                      selectedCategory === category
                        ? 'bg-blue-100 text-blue-800'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* 用語リスト */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-3">
                  用語一覧 ({filteredItems.length})
                </h3>
                <div className="space-y-1">
                  {filteredItems.map((item) => (
                    <button
                      key={item.term}
                      onClick={() => setSelectedItem(item)}
                      className={`w-full text-left p-3 rounded-md transition-colors ${
                        selectedItem?.term === item.term
                          ? 'bg-blue-100 text-blue-800'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="font-medium">{item.term}</div>
                      <div className="text-sm text-gray-600">{item.short}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* メインコンテンツ */}
          <div className="flex-1 flex flex-col">
            {selectedItem ? (
              <>
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">{selectedItem.term}</h3>
                      <p className="text-lg text-gray-600 mt-1">{selectedItem.short}</p>
                    </div>
                    <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                      {selectedItem.category}
                    </div>
                  </div>
                </div>

                <div className="flex-1 p-6 overflow-y-auto">
                  <div className="prose max-w-none">
                    <p className="text-gray-700 leading-relaxed">{selectedItem.detail}</p>
                  </div>

                  {selectedItem.links && selectedItem.links.length > 0 && (
                    <div className="mt-6 pt-6 border-t border-gray-200">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">関連ページ</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedItem.links.map((link) => (
                          <a
                            key={link}
                            href={link}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm transition-colors"
                          >
                            {link === '/' ? 'ダッシュボード' : 
                             link === '/predictions' ? '予測結果' :
                             link === '/models' ? 'モデル比較' :
                             link === '/analysis' ? '分析' :
                             link === '/reports' ? 'レポート' :
                             link === '/settings' ? '設定' :
                             link === '/risk' ? 'リスク' : link}
                            <ExternalLink size={12} />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <BookOpen size={48} className="mx-auto mb-4 text-gray-300" />
                  <p>用語を選択してください</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
