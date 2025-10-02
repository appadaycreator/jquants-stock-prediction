"use client";

import { useState, useEffect } from "react";

// 動的レンダリングを強制
export const dynamic = "force-dynamic";
import Link from "next/link";
import { 
  Target, 
  BarChart3, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  ArrowRight,
  Play,
  Settings,
  BookOpen,
  Shield,
  List,
} from "lucide-react";

export default function LandingPage() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">J-Quants 株価予測システム</h1>
                <p className="text-sm text-gray-600">機械学習による投資判断支援</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/today"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <Play className="h-4 w-4" />
                <span>今すぐ開始</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* ヒーローセクション */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            5分で完了する投資判断
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            機械学習とリアルタイムデータ分析により、効率的な投資判断をサポートします。
            複雑な分析は自動化し、あなたは重要な判断に集中できます。
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/today"
              className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2 text-lg font-semibold"
            >
              <Target className="h-5 w-5" />
              <span>今日のタスクを開始</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/dashboard"
              className="bg-white text-gray-700 px-8 py-4 rounded-lg border border-gray-300 hover:bg-gray-50 flex items-center justify-center space-x-2 text-lg font-semibold"
            >
              <BarChart3 className="h-5 w-5" />
              <span>詳細分析を見る</span>
            </Link>
          </div>
        </div>

        {/* 機能紹介 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-xl shadow-sm border p-6 text-center">
            <div className="bg-green-100 p-3 rounded-lg w-fit mx-auto mb-4">
              <Clock className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">5分ルーティン</h3>
            <p className="text-gray-600">
              毎日の投資判断を5分で完了。データ更新、候補銘柄の確認、保有銘柄の判断を効率的に実行。
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6 text-center">
            <div className="bg-blue-100 p-3 rounded-lg w-fit mx-auto mb-4">
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">詳細分析</h3>
            <p className="text-gray-600">
              機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供。
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6 text-center">
            <div className="bg-purple-100 p-3 rounded-lg w-fit mx-auto mb-4">
              <Shield className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">リスク管理</h3>
            <p className="text-gray-600">
              リスク評価、ポートフォリオ監視、自動アラート機能で投資を安全にサポート。
            </p>
          </div>
        </div>

        {/* クイックアクセス */}
        <div className="bg-white rounded-xl shadow-sm border p-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">クイックアクセス</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              href="/today"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <Target className="h-6 w-6 text-blue-600" />
              <div>
                <div className="font-medium text-gray-900">今日のタスク</div>
                <div className="text-sm text-gray-600">5分ルーティン</div>
              </div>
            </Link>

            <Link
              href="/dashboard"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <BarChart3 className="h-6 w-6 text-green-600" />
              <div>
                <div className="font-medium text-gray-900">詳細分析</div>
                <div className="text-sm text-gray-600">ダッシュボード</div>
              </div>
            </Link>

            <Link
              href="/listed-data"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <List className="h-6 w-6 text-purple-600" />
              <div>
                <div className="font-medium text-gray-900">銘柄一覧</div>
                <div className="text-sm text-gray-600">上場銘柄検索</div>
              </div>
            </Link>

            <Link
              href="/risk"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <Shield className="h-6 w-6 text-red-600" />
              <div>
                <div className="font-medium text-gray-900">リスク管理</div>
                <div className="text-sm text-gray-600">ポートフォリオ監視</div>
              </div>
            </Link>

            <Link
              href="/settings"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <Settings className="h-6 w-6 text-gray-600" />
              <div>
                <div className="font-medium text-gray-900">設定</div>
                <div className="text-sm text-gray-600">システム設定</div>
              </div>
            </Link>
          </div>
        </div>

        {/* システム状況 */}
        <div className="mt-16 bg-white rounded-xl shadow-sm border p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-semibold text-gray-900">システム状況</h3>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-green-600 font-medium">正常稼働中</span>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-sm text-gray-600">稼働率</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">24/7</div>
              <div className="text-sm text-gray-600">監視体制</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">リアルタイム</div>
              <div className="text-sm text-gray-600">データ更新</div>
            </div>
          </div>
        </div>
      </main>

      {/* フッター */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              <span className="text-lg font-semibold text-gray-900">J-Quants 株価予測システム</span>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="/usage" className="text-sm text-gray-600 hover:text-gray-900 flex items-center space-x-1">
                <BookOpen className="h-4 w-4" />
                <span>使い方</span>
              </Link>
              <Link href="/troubleshooting" className="text-sm text-gray-600 hover:text-gray-900">
                トラブルシューティング
              </Link>
            </div>
          </div>
          <div className="border-t mt-6 pt-6 text-center">
            <p className="text-sm text-gray-500">
              © 2024 J-Quants 株価予測システム. 機械学習による投資判断支援ツール.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
