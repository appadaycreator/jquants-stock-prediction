/**
 * 404ページ（Not Found）
 * ユーザーフレンドリーなエラーページとナビゲーション
 */

"use client";

import Link from "next/link";
import { Home, ArrowLeft, HelpCircle } from "lucide-react";

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
            aria-label="ホームページに戻る"
            data-help="メインダッシュボードページに戻ります。全体の投資状況と主要指標を一覧表示し、機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供します。投資判断の精度向上に役立つ包括的な投資分析機能を利用できます。"
          >
            <Home className="w-5 h-5 mr-2" />
            ホームに戻る
          </Link>

          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors"
            aria-label="前のページに戻る"
            data-help="ブラウザの履歴を使用して前のページに戻ります。直前の操作や画面に戻ることができ、ナビゲーションの効率化をサポートします。"
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
              aria-label="今日の指示ページへ移動"
              data-help="今日の投資判断と推奨アクションを確認できます。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。データ更新状況の確認、上位候補銘柄の分析、保有銘柄の提案、メモ記録まで一連の流れを実行します。"
            >
              <span className="text-sm text-gray-700">今日の指示</span>
            </Link>
            <Link
              href="/personal-investment"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              aria-label="個人投資ページへ移動"
              data-help="個人の投資戦略とポートフォリオ管理を行います。AI/ルールベースによる投資提案、LSTM深層学習による株価予測、リアルタイム損益計算、パフォーマンス比較とランキング、損益推移グラフとチャート分析など、包括的な投資管理機能を提供します。"
            >
              <span className="text-sm text-gray-700">個人投資</span>
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              aria-label="ダッシュボードページへ移動"
              data-help="銘柄の詳細な技術分析とチャートを表示します。テクニカル指標、価格予測、機械学習分析結果を確認できます。移動平均線、RSI、MACD、ボリンジャーバンドなどの技術分析指標と、AIによる価格予測を詳細に分析できます。"
            >
              <span className="text-sm text-gray-700">ダッシュボード</span>
            </Link>
            <Link
              href="/settings"
              className="flex items-center justify-center p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              aria-label="設定ページへ移動"
              data-help="システム設定と予測パラメータを変更します。予測期間、使用モデル、特徴量選択、J-Quants API設定などをカスタマイズできます。設定のエクスポート・インポート機能で、設定をバックアップしたり他の環境で再利用できます。"
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
            aria-label="トラブルシューティングページへ移動"
            data-help="よくある問題と解決方法を確認できます。データ表示、分析実行、接続エラーなどの問題を段階的に解決できます。問題のカテゴリ別に整理されており、症状と解決手順を詳細に確認できます。システムのパフォーマンス最適化のヒントも提供されます。"
          >
            <HelpCircle className="w-4 h-4 mr-1" />
            トラブルシューティング
          </Link>
        </div>
      </div>
    </div>
  );
}
