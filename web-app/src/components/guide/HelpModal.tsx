"use client";

import React, { useState, useEffect, useRef } from 'react';
import { HelpCircle, X, Search, BookOpen, Settings, BarChart3, TrendingUp, Shield } from 'lucide-react';
import { useGuide } from './TourProvider';

interface HelpSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  content: string;
  links: { label: string; href: string }[];
}

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPage?: string;
}

const HELP_SECTIONS: HelpSection[] = [
  {
    id: 'getting-started',
    title: 'はじめに',
    icon: <BookOpen size={20} />,
    content: 'J-Quants株価予測システムの基本的な使い方を説明します。初回利用時は自動ガイドが表示されます。',
    links: [
      { label: 'ダッシュボード', href: '/' },
      { label: '使い方ガイド', href: '/usage' }
    ]
  },
  {
    id: 'dashboard',
    title: 'ダッシュボード',
    icon: <BarChart3 size={20} />,
    content: '今日の投資指示と主要KPIを確認できます。MAE、R²、予測精度などの指標を理解しましょう。',
    links: [
      { label: 'ダッシュボード', href: '/' },
      { label: '予測結果', href: '/predictions' }
    ]
  },
  {
    id: 'models',
    title: 'モデル比較',
    icon: <TrendingUp size={20} />,
    content: '複数の機械学習モデルの性能を比較できます。総合評価から詳細指標まで確認しましょう。',
    links: [
      { label: 'モデル比較', href: '/models' },
      { label: '分析', href: '/analysis' }
    ]
  },
  {
    id: 'risk',
    title: 'リスク管理',
    icon: <Shield size={20} />,
    content: '投資リスクの評価と管理機能。損切り・利確の設定、ボラティリティ分析が可能です。',
    links: [
      { label: 'リスク', href: '/risk' },
      { label: '設定', href: '/settings' }
    ]
  }
];

const FAQ_ITEMS = [
  {
    question: 'MAEとR²の違いは何ですか？',
    answer: 'MAE（平均絶対誤差）は予測の精度を、R²（決定係数）はモデルの説明力を示します。低いMAEと高いR²が理想的です。',
    category: '指標'
  },
  {
    question: '予測精度が低い場合はどうすれば？',
    answer: 'モデル比較で他のモデルを試すか、分析タブで特徴量重要度を確認し、データの質を見直してください。',
    category: 'トラブル'
  },
  {
    question: '通知設定はどこで変更できますか？',
    answer: '設定ページの通知設定から、メールアドレスや通知条件を変更できます。',
    category: '設定'
  },
  {
    question: 'データが更新されない場合は？',
    answer: '最新結果を再取得ボタンをクリックするか、設定で更新間隔を確認してください。',
    category: 'トラブル'
  }
];

export default function HelpModal({ 
  isOpen, 
  onClose, 
  currentPage = '/' 
}: HelpModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSection, setSelectedSection] = useState<string>('getting-started');
  const [selectedFAQ, setSelectedFAQ] = useState<number | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const { startTour } = useGuide();

  const filteredSections = HELP_SECTIONS.filter(section =>
    section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    section.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredFAQs = FAQ_ITEMS.filter(faq =>
    faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            <HelpCircle size={24} className="text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">クイックヘルプ</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="ヘルプを閉じる"
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
                  placeholder="ヘルプを検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* ナビゲーション */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-3">主要機能</h3>
                <div className="space-y-1">
                  {filteredSections.map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setSelectedSection(section.id)}
                      className={`w-full text-left p-3 rounded-md transition-colors ${
                        selectedSection === section.id
                          ? 'bg-blue-100 text-blue-800'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {section.icon}
                        <span className="font-medium">{section.title}</span>
                      </div>
                    </button>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">よくある質問</h3>
                  <div className="space-y-1">
                    {filteredFAQs.map((faq, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedFAQ(selectedFAQ === index ? null : index)}
                        className={`w-full text-left p-2 rounded-md transition-colors ${
                          selectedFAQ === index
                            ? 'bg-blue-100 text-blue-800'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        <div className="text-sm font-medium">{faq.question}</div>
                        <div className="text-xs text-gray-500">{faq.category}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* メインコンテンツ */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {selectedFAQ !== null ? (
              /* FAQ詳細 */
              <div className="flex-1 p-6 overflow-y-auto">
                <div className="mb-4">
                  <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium inline-block mb-3">
                    {FAQ_ITEMS[selectedFAQ].category}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {FAQ_ITEMS[selectedFAQ].question}
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {FAQ_ITEMS[selectedFAQ].answer}
                  </p>
                </div>
              </div>
            ) : (
              /* セクション詳細 */
              <>
                {(() => {
                  const section = HELP_SECTIONS.find(s => s.id === selectedSection);
                  if (!section) return null;

                  return (
                    <>
                      <div className="p-6 border-b border-gray-200">
                        <div className="flex items-center gap-3 mb-2">
                          {section.icon}
                          <h3 className="text-2xl font-bold text-gray-900">{section.title}</h3>
                        </div>
                        <p className="text-gray-600">{section.content}</p>
                      </div>

                      <div className="flex-1 p-6 overflow-y-auto">
                        <div className="space-y-6">
                          {/* 関連リンク */}
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900 mb-3">関連ページ</h4>
                            <div className="grid grid-cols-1 gap-3">
                              {section.links.map((link) => (
                                <a
                                  key={link.href}
                                  href={link.href}
                                  className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                  <span className="font-medium">{link.label}</span>
                                  <span className="text-sm text-gray-500">→</span>
                                </a>
                              ))}
                            </div>
                          </div>

                          {/* クイックアクション */}
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900 mb-3">クイックアクション</h4>
                            <div className="grid grid-cols-1 gap-3">
                              <button
                                onClick={() => {
                                  onClose();
                                  startTour();
                                }}
                                className="flex items-center gap-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left"
                              >
                                <BookOpen size={20} className="text-blue-600" />
                                <div>
                                  <div className="font-medium text-blue-900">ガイドツアーを開始</div>
                                  <div className="text-sm text-blue-700">主要機能を順番に案内します</div>
                                </div>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </>
            )}
          </div>
        </div>

        {/* フッター */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-4">
              <span>💡 ヒント: F1キーでヘルプを開く</span>
              <span>⌨️ キーボードショートカット対応</span>
            </div>
            <div className="flex items-center gap-2">
              <span>サポートが必要な場合は</span>
              <a href="/usage" className="text-blue-600 hover:text-blue-800 font-medium">
                使い方ガイド
              </a>
              <span>をご確認ください</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
