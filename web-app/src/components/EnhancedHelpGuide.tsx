"use client";

import React, { useState, useMemo } from "react";
import { 
  Search, 
  Play, 
  BookOpen, 
  Video, 
  FileText, 
  HelpCircle,
  X,
  ChevronRight,
  ChevronDown,
  Filter,
  Clock,
  User,
  Star,
} from "lucide-react";

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  type: "video" | "text" | "interactive";
  duration?: number;
  difficulty: "beginner" | "intermediate" | "advanced";
  category: string;
  tags: string[];
  content: React.ReactNode;
}

interface HelpGuideProps {
  isOpen: boolean;
  onClose: () => void;
}

const EnhancedHelpGuide: React.FC<HelpGuideProps> = ({ isOpen, onClose }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["getting-started"]));

  const tutorialSteps: TutorialStep[] = [
    {
      id: "getting-started",
      title: "はじめに",
      description: "J-Quants株価予測システムの基本的な使い方を学びます",
      type: "video",
      duration: 5,
      difficulty: "beginner",
      category: "基本操作",
      tags: ["基本", "入門", "チュートリアル"],
      content: (
        <div className="space-y-4">
          <div className="bg-themed-background-secondary p-4 rounded-lg">
            <h4 className="font-semibold text-themed-primary mb-2">システムの概要</h4>
            <p className="text-themed-text-secondary text-sm">
              J-Quants APIを使用した株価予測システムです。機械学習モデルを使用して、
              株価の動向を予測し、投資判断をサポートします。
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 bg-themed-success-light rounded-lg">
              <h5 className="font-medium text-themed-success mb-1">主な機能</h5>
              <ul className="text-sm text-themed-text-secondary space-y-1">
                <li>• リアルタイム株価データ取得</li>
                <li>• AI予測モデル</li>
                <li>• リスク分析</li>
                <li>• ポートフォリオ管理</li>
              </ul>
            </div>
            <div className="p-3 bg-themed-info-light rounded-lg">
              <h5 className="font-medium text-themed-info mb-1">対象ユーザー</h5>
              <ul className="text-sm text-themed-text-secondary space-y-1">
                <li>• 個人投資家</li>
                <li>• 投資初心者</li>
                <li>• データ分析者</li>
                <li>• 金融関係者</li>
              </ul>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "dashboard-overview",
      title: "ダッシュボードの使い方",
      description: "メインダッシュボードの各機能と操作方法を説明します",
      type: "interactive",
      duration: 10,
      difficulty: "beginner",
      category: "基本操作",
      tags: ["ダッシュボード", "基本操作", "ナビゲーション"],
      content: (
        <div className="space-y-4">
          <div className="bg-themed-background-secondary p-4 rounded-lg">
            <h4 className="font-semibold text-themed-primary mb-2">ダッシュボードの構成</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-themed-text-primary mb-2">左側パネル</h5>
                <ul className="text-sm text-themed-text-secondary space-y-1">
                  <li>• 今日のルーティン</li>
                  <li>• 重要アラート</li>
                  <li>• リスク状態</li>
                  <li>• 今日の推奨</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-themed-text-primary mb-2">右側パネル</h5>
                <ul className="text-sm text-themed-text-secondary space-y-1">
                  <li>• 詳細情報表示</li>
                  <li>• チャート分析</li>
                  <li>• 設定変更</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "analysis-execution",
      title: "分析の実行方法",
      description: "株価分析の実行手順と設定方法を詳しく説明します",
      type: "video",
      duration: 15,
      difficulty: "intermediate",
      category: "分析機能",
      tags: ["分析", "実行", "設定", "モデル"],
      content: (
        <div className="space-y-4">
          <div className="bg-themed-background-secondary p-4 rounded-lg">
            <h4 className="font-semibold text-themed-primary mb-2">分析実行の手順</h4>
            <ol className="text-sm text-themed-text-secondary space-y-2">
              <li>1. 分析したい銘柄を選択</li>
              <li>2. 分析期間を設定</li>
              <li>3. 使用するモデルを選択</li>
              <li>4. 分析を実行</li>
              <li>5. 結果を確認</li>
            </ol>
          </div>
        </div>
      ),
    },
    {
      id: "risk-management",
      title: "リスク管理の基礎",
      description: "投資リスクの理解と管理方法について学びます",
      type: "text",
      duration: 20,
      difficulty: "advanced",
      category: "リスク管理",
      tags: ["リスク", "管理", "投資", "安全"],
      content: (
        <div className="space-y-4">
          <div className="bg-themed-warning-light p-4 rounded-lg">
            <h4 className="font-semibold text-themed-warning mb-2">重要な注意事項</h4>
            <p className="text-themed-text-secondary text-sm">
              このシステムは投資判断の参考情報を提供するものです。
              投資は自己責任で行い、必ずリスクを理解した上で実行してください。
            </p>
          </div>
        </div>
      ),
    },
  ];

  const categories = [
    { id: "all", name: "すべて", count: tutorialSteps.length },
    { id: "基本操作", name: "基本操作", count: tutorialSteps.filter(s => s.category === "基本操作").length },
    { id: "分析機能", name: "分析機能", count: tutorialSteps.filter(s => s.category === "分析機能").length },
    { id: "リスク管理", name: "リスク管理", count: tutorialSteps.filter(s => s.category === "リスク管理").length },
  ];

  const difficulties = [
    { id: "all", name: "すべて", color: "text-themed-text-secondary" },
    { id: "beginner", name: "初級", color: "text-themed-success" },
    { id: "intermediate", name: "中級", color: "text-themed-warning" },
    { id: "advanced", name: "上級", color: "text-themed-error" },
  ];

  const filteredSteps = useMemo(() => {
    return tutorialSteps.filter(step => {
      const matchesSearch = step.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           step.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           step.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesCategory = selectedCategory === "all" || step.category === selectedCategory;
      const matchesDifficulty = selectedDifficulty === "all" || step.difficulty === selectedDifficulty;
      
      return matchesSearch && matchesCategory && matchesDifficulty;
    });
  }, [searchQuery, selectedCategory, selectedDifficulty]);

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case "beginner":
        return <Star className="h-4 w-4 text-themed-success" />;
      case "intermediate":
        return <Star className="h-4 w-4 text-themed-warning" />;
      case "advanced":
        return <Star className="h-4 w-4 text-themed-error" />;
      default:
        return <Star className="h-4 w-4 text-themed-text-secondary" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-4 w-4 text-themed-info" />;
      case "interactive":
        return <Play className="h-4 w-4 text-themed-primary" />;
      default:
        return <FileText className="h-4 w-4 text-themed-text-secondary" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-themed-surface rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-themed-border">
          <div className="flex items-center space-x-3">
            <BookOpen className="h-6 w-6 text-themed-primary" />
            <h2 className="text-xl font-bold text-themed-primary">使い方ガイド</h2>
          </div>
          <button
            onClick={onClose}
            className="text-themed-text-secondary hover:text-themed-text-primary transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex h-[calc(90vh-80px)]">
          {/* サイドバー */}
          <div className="w-80 border-r border-themed-border bg-themed-background-secondary">
            <div className="p-4">
              {/* 検索 */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-themed-text-tertiary" />
                <input
                  type="text"
                  placeholder="ガイドを検索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-themed-border rounded-lg bg-themed-surface text-themed-text-primary focus:outline-none focus:ring-2 focus:ring-themed-border-focus"
                />
              </div>

              {/* フィルター */}
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-themed-text-primary mb-2">カテゴリ</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-themed-border rounded-lg bg-themed-surface text-themed-text-primary focus:outline-none focus:ring-2 focus:ring-themed-border-focus"
                  >
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name} ({category.count})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-themed-text-primary mb-2">難易度</label>
                  <select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                    className="w-full px-3 py-2 border border-themed-border rounded-lg bg-themed-surface text-themed-text-primary focus:outline-none focus:ring-2 focus:ring-themed-border-focus"
                  >
                    {difficulties.map(difficulty => (
                      <option key={difficulty.id} value={difficulty.id}>
                        {difficulty.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* チュートリアル一覧 */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-4 space-y-2">
                {filteredSteps.map((step) => (
                  <button
                    key={step.id}
                    onClick={() => toggleSection(step.id)}
                    className="w-full text-left p-3 rounded-lg hover:bg-themed-background-tertiary transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getTypeIcon(step.type)}
                        <span className="font-medium text-themed-text-primary">{step.title}</span>
                      </div>
                      {expandedSections.has(step.id) ? (
                        <ChevronDown className="h-4 w-4 text-themed-text-secondary" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-themed-text-secondary" />
                      )}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      {getDifficultyIcon(step.difficulty)}
                      <span className="text-xs text-themed-text-secondary">{step.category}</span>
                      {step.duration && (
                        <span className="text-xs text-themed-text-tertiary flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {step.duration}分
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* メインコンテンツ */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              {filteredSteps.length === 0 ? (
                <div className="text-center py-12">
                  <Search className="h-12 w-12 text-themed-text-tertiary mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-themed-text-primary mb-2">検索結果が見つかりません</h3>
                  <p className="text-themed-text-secondary">別のキーワードで検索してみてください。</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {filteredSteps.map((step) => (
                    <div key={step.id} className="space-y-4">
                      {expandedSections.has(step.id) && (
                        <div className="bg-themed-background-secondary rounded-lg p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h3 className="text-lg font-semibold text-themed-primary">{step.title}</h3>
                              <p className="text-themed-text-secondary text-sm">{step.description}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                              {getTypeIcon(step.type)}
                              {getDifficultyIcon(step.difficulty)}
                            </div>
                          </div>
                          <div className="prose prose-sm max-w-none">
                            {step.content}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedHelpGuide;
