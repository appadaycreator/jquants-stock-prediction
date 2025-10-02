/**
 * 404ページ（Not Found）
 * ユーザーフレンドリーなエラーページとナビゲーション
 */

"use client";

import Link from "next/link";
import { Home, ArrowLeft, Search, HelpCircle } from "lucide-react";

// 動的レンダリングを強制
export const dynamic = "force-dynamic";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* 404アイコン */}
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-red-100 rounded-full flex items-center justify-center">
            <span className="text-4xl font-bold text-red-600">404</span>
          </div>
        </div>

        {/* エラーメッセージ */}
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          ページが見つかりません
        </h1>
        <p className="text-gray-600 mb-8">
          お探しのページは存在しないか、移動された可能性があります。
        </p>

        {/* アクションボタン */}
        <div className="space-y-4">
          <Link
            href="/"
            className="inline-flex items-center justify-center w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Home className="w-5 h-5 mr-2" />
            ホームに戻る
          </Link>

          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            前のページに戻る
          </button>
        </div>

        {/* よく使われるページへのリンク */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-4">
            よく使われるページ
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <Link
              href="/today"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm text-gray-700">今日の指示</span>
            </Link>
            <Link
              href="/personal-investment"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm text-gray-700">個人投資</span>
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm text-gray-700">ダッシュボード</span>
            </Link>
            <Link
              href="/settings"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <span className="text-sm text-gray-700">設定</span>
            </Link>
          </div>
        </div>

        {/* ヘルプリンク */}
        <div className="mt-6">
          <Link
            href="/troubleshooting"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            <HelpCircle className="w-4 h-4 mr-1" />
            トラブルシューティング
          </Link>
        </div>
      </div>
    </div>
  );
}
