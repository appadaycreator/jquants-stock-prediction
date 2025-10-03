"use client";

import React, { useState } from "react";
import { 
  AlertCircle, 
  X, 
  Settings, 
  BarChart3, 
  Database,
  Wifi,
  Clock,
  HelpCircle,
  ArrowRight,
  ExternalLink,
  BookOpen,
} from "lucide-react";
import Link from "next/link";

interface TroubleshootingItem {
  id: string;
  title: string;
  description: string;
  symptoms: string[];
  solutions: Array<{
    step: string;
    description: string;
    action?: () => void;
  }>;
  severity: "low" | "medium" | "high" | "critical";
  category: "data" | "analysis" | "display" | "performance" | "connection";
}

export default function TroubleshootingPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const troubleshootingItems: TroubleshootingItem[] = [
    {
      id: "no-data-display",
      title: "データが表示されない（N/A表示）",
      description: "ダッシュボードで「N/A」や空欄が表示される問題",
      symptoms: [
        "ダッシュボードに「N/A」が表示される",
        "チャートが空の状態で表示される",
        "予測結果が表示されない",
        "メトリクスが「-」で表示される",
      ],
      solutions: [
        {
          step: "1",
          description: "分析を実行してください",
          action: () => window.location.href = "/",
        },
        {
          step: "2",
          description: "5分ルーティンに従って操作を進めてください",
          action: () => window.location.href = "/five-min-routine",
        },
        {
          step: "3",
          description: "データの更新を試してください",
        },
      ],
      severity: "medium",
      category: "data",
    },
    {
      id: "analysis-fails",
      title: "分析が実行できない",
      description: "分析ボタンを押しても分析が開始されない問題",
      symptoms: [
        "分析ボタンを押しても反応がない",
        "分析が途中で止まる",
        "エラーメッセージが表示される",
        "分析結果が取得できない",
      ],
      solutions: [
        {
          step: "1",
          description: "ページを再読み込みしてください",
        },
        {
          step: "2",
          description: "ブラウザのキャッシュをクリアしてください",
        },
        {
          step: "3",
          description: "別のブラウザで試してください",
        },
        {
          step: "4",
          description: "設定を確認してください",
          action: () => window.location.href = "/settings",
        },
      ],
      severity: "high",
      category: "analysis",
    },
    {
      id: "slow-performance",
      title: "動作が遅い",
      description: "ページの読み込みや操作が遅い問題",
      symptoms: [
        "ページの読み込みが遅い",
        "ボタンの反応が遅い",
        "チャートの描画が遅い",
        "データの更新が遅い",
      ],
      solutions: [
        {
          step: "1",
          description: "インターネット接続を確認してください",
        },
        {
          step: "2",
          description: "ブラウザを最新版に更新してください",
        },
        {
          step: "3",
          description: "他のタブを閉じてください",
        },
        {
          step: "4",
          description: "デバイスの再起動を試してください",
        },
      ],
      severity: "low",
      category: "performance",
    },
    {
      id: "connection-issues",
      title: "接続エラー",
      description: "サーバーとの接続に問題がある場合",
      symptoms: [
        "「接続エラー」が表示される",
        "データが取得できない",
        "APIエラーが発生する",
        "タイムアウトエラーが表示される",
      ],
      solutions: [
        {
          step: "1",
          description: "インターネット接続を確認してください",
        },
        {
          step: "2",
          description: "しばらく待ってから再試行してください",
        },
        {
          step: "3",
          description: "ページを再読み込みしてください",
        },
        {
          step: "4",
          description: "システム管理者に連絡してください",
        },
      ],
      severity: "critical",
      category: "connection",
    },
    {
      id: "display-issues",
      title: "表示が正しくない",
      description: "レイアウトや表示に問題がある場合",
      symptoms: [
        "レイアウトが崩れている",
        "文字が正しく表示されない",
        "ボタンが押せない",
        "チャートが表示されない",
      ],
      solutions: [
        {
          step: "1",
          description: "ブラウザのズームを100%に設定してください",
        },
        {
          step: "2",
          description: "ブラウザのキャッシュをクリアしてください",
        },
        {
          step: "3",
          description: "別のブラウザで試してください",
        },
        {
          step: "4",
          description: "デバイスの解像度を確認してください",
        },
      ],
      severity: "medium",
      category: "display",
    },
  ];

  const categories = [
    { id: "all", label: "すべて", icon: HelpCircle },
    { id: "data", label: "データ", icon: Database },
    { id: "analysis", label: "分析", icon: BarChart3 },
    { id: "display", label: "表示", icon: Settings },
    { id: "performance", label: "パフォーマンス", icon: Clock },
    { id: "connection", label: "接続", icon: Wifi },
  ];

  const filteredItems = selectedCategory === "all" 
    ? troubleshootingItems 
    : troubleshootingItems.filter(item => item.category === selectedCategory);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low": return "text-green-600 bg-green-100";
      case "medium": return "text-yellow-600 bg-yellow-100";
      case "high": return "text-orange-600 bg-orange-100";
      case "critical": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case "low": return "軽微";
      case "medium": return "中程度";
      case "high": return "重要";
      case "critical": return "緊急";
      default: return "不明";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link
                href="/"
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowRight className="h-5 w-5 mr-2 rotate-180" />
                ダッシュボードに戻る
              </Link>
              <div className="h-6 w-px bg-gray-300" />
              <h1 className="text-2xl font-bold text-gray-900">トラブルシューティング</h1>
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* 概要 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <AlertCircle className="h-6 w-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">問題解決ガイド</h2>
            </div>
            <p className="text-gray-600 mb-4">
              システムで問題が発生した場合の解決方法をまとめています。
              まずは該当する問題を選択し、解決手順に従って操作してください。
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                よくある問題
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                段階的解決
              </span>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                詳細説明
              </span>
            </div>
          </div>

          {/* カテゴリフィルター */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">問題のカテゴリ</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {categories.map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                      selectedCategory === category.id
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{category.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 問題一覧 */}
          <div className="space-y-4">
            {filteredItems.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow">
                <button
                  onClick={() => setExpandedItem(expandedItem === item.id ? null : item.id)}
                  className="w-full p-6 text-left hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(item.severity)}`}>
                        {getSeverityLabel(item.severity)}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
                        <p className="text-sm text-gray-600">{item.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">
                        {item.symptoms.length} 症状
                      </span>
                      <X className={`h-5 w-5 text-gray-400 transition-transform ${
                        expandedItem === item.id ? "rotate-45" : ""
                      }`} />
                    </div>
                  </div>
                </button>

                {expandedItem === item.id && (
                  <div className="px-6 pb-6 border-t border-gray-200">
                    <div className="space-y-6">
                      {/* 症状 */}
                      <div>
                        <h4 className="text-md font-semibold text-gray-900 mb-3">症状</h4>
                        <ul className="space-y-2">
                          {item.symptoms.map((symptom, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm text-gray-700">{symptom}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* 解決方法 */}
                      <div>
                        <h4 className="text-md font-semibold text-gray-900 mb-3">解決方法</h4>
                        <div className="space-y-4">
                          {item.solutions.map((solution, index) => (
                            <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                                {solution.step}
                              </div>
                              <div className="flex-1">
                                <p className="text-sm text-gray-700 mb-2">{solution.description}</p>
                                {solution.action && (
                                  <button
                                    onClick={solution.action}
                                    className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
                                  >
                                    <ExternalLink className="h-3 w-3 mr-1" />
                                    実行
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* 追加サポート */}
          <div className="bg-blue-50 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <HelpCircle className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-blue-900">追加サポート</h3>
            </div>
            <p className="text-blue-800 mb-4">
              上記の解決方法で問題が解決しない場合は、以下の方法でサポートを受けることができます。
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link
                href="/usage"
                className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors"
              >
                <BookOpen className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="font-medium text-gray-900">使い方ガイド</div>
                  <div className="text-sm text-gray-600">詳細な使用方法を確認</div>
                </div>
              </Link>
              <Link
                href="/five-min-routine"
                className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Clock className="h-5 w-5 text-green-600" />
                <div>
                  <div className="font-medium text-gray-900">5分ルーティン</div>
                  <div className="text-sm text-gray-600">正しい操作手順を確認</div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
