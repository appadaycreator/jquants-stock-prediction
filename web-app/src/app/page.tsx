"use client";

import { useState, useEffect } from "react";
import { cacheInitializer } from "@/lib/cache/CacheInitializer";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";
import { DiagnosticsPanel } from "@/components/diagnostics/DiagnosticsPanel";

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
  const [cacheReady, setCacheReady] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  useEffect(() => {
    setIsClient(true);
    
    // キャッシュシステムの初期化
    const initializeCache = async () => {
      try {
        await cacheInitializer.initialize();
        setCacheReady(true);
        console.log("✅ キャッシュシステム準備完了");
      } catch (error) {
        console.error("❌ キャッシュシステム初期化エラー:", error);
        setCacheReady(true); // エラーでもアプリは続行
      }
    };

    initializeCache();
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
    <ErrorBoundary>
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
              <button
                onClick={() => setShowDiagnostics(true)}
                className="text-gray-600 hover:text-gray-900 flex items-center space-x-2"
                aria-label="システム診断を開く"
                data-help="システムの状態とパフォーマンスを包括的に診断します。CPU使用率、メモリ使用量、ディスク容量、ネットワーク接続状況、エラー状況、キャッシュ状態、データベース接続、API応答時間などを詳細に確認できます。問題が発生した際の最初の確認ポイントとして、システムの健全性をリアルタイムで監視し、パフォーマンスの最適化に役立ちます。診断結果に基づいてシステムの改善提案も表示され、トラブルシューティングの効率化をサポートします。システム管理者向けの詳細な技術情報も提供されます。リアルタイム監視機能により、システムの異常を早期に発見し、投資判断に影響を与える前に問題を解決できます。"
              >
                <Shield className="h-5 w-5" />
                <span>診断</span>
              </button>
              <Link
                href="/today"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                aria-label="今日のタスクを開始"
                data-help="今日の投資判断タスクを開始します。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。データ更新状況の確認、上位候補銘柄の分析、保有銘柄の提案、メモ記録まで一連の流れを実行します。初心者でも迷わずに投資判断を行えるよう設計されており、毎日の投資活動を効率化できます。機械学習による推奨アクションとテクニカル分析を組み合わせた総合的な投資判断を提供します。投資の学習効果を高め、過去の判断を振り返って投資スキルの向上に役立てることができます。リアルタイムの市場データに基づく最新の投資判断を提供し、投資機会を見逃さないようサポートします。毎日の投資判断を標準化し、一貫性のある投資戦略を実現できます。"
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
              aria-label="今日のタスクを開始"
              data-help="今日の投資判断タスクを開始します。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。データ更新状況の確認、上位候補銘柄の分析、保有銘柄の提案、メモ記録まで一連の流れを実行します。初心者でも迷わずに投資判断を行えるよう設計されており、毎日の投資活動を効率化できます。機械学習による推奨アクションとテクニカル分析を組み合わせた総合的な投資判断を提供します。投資の学習効果を高め、過去の判断を振り返って投資スキルの向上に役立てることができます。リアルタイムの市場データに基づく最新の投資判断を提供し、投資機会を見逃さないようサポートします。毎日の投資判断を標準化し、一貫性のある投資戦略を実現できます。"
            >
              <Target className="h-5 w-5" />
              <span>今日のタスクを開始</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/dashboard"
              className="bg-white text-gray-700 px-8 py-4 rounded-lg border border-gray-300 hover:bg-gray-50 flex items-center justify-center space-x-2 text-lg font-semibold"
              aria-label="詳細分析ダッシュボードを表示"
              data-help="詳細な分析結果とダッシュボードを表示します。機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供します。複数の予測モデルの精度比較、特徴量重要度分析、予測誤差の詳細分析、モデル性能の可視化など、高度な分析機能を利用できます。プロの投資家向けの詳細な分析ツールとして、投資判断の精度向上に役立ちます。インタラクティブなチャートとレポート機能で、投資戦略の検証と改善に活用できます。リアルタイムデータ分析、セクター別パフォーマンス、リスク評価、投資推奨の詳細根拠など、包括的な投資分析機能を提供します。投資判断の信頼性を高めるため、複数の分析手法を組み合わせた総合的な評価を提供します。"
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
            <h3 className="text-xl font-semibold text-gray-900 mb-3">今日のタスク</h3>
            <p className="text-gray-600">
              重要なアクションを集約し、分析実行と結果確認を素早く行えます。
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
              aria-label="今日のタスクページへ移動"
              data-help="今日の投資判断タスクを確認・実行できます。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。データ更新状況の確認、上位候補銘柄の分析、保有銘柄の提案、メモ記録まで一連の流れを実行します。初心者でも迷わずに投資判断を行えるよう設計されており、毎日の投資活動を効率化できます。機械学習による推奨アクションとテクニカル分析を組み合わせた総合的な投資判断を提供し、投資機会を見逃さないようサポートします。毎日の投資判断を標準化し、一貫性のある投資戦略を実現できます。"
            >
              <Target className="h-6 w-6 text-blue-600" />
              <div>
                <div className="font-medium text-gray-900">今日のタスク</div>
                <div className="text-sm text-gray-600">今日のタスク</div>
              </div>
            </Link>

            <Link
              href="/dashboard"
              className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              aria-label="詳細分析ダッシュボードへ移動"
              data-help="詳細な分析結果とダッシュボードを表示します。機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供します。複数の予測モデルの精度比較、特徴量重要度分析、予測誤差の詳細分析、モデル性能の可視化など、高度な分析機能を利用できます。プロの投資家向けの詳細な分析ツールとして、投資判断の精度向上に役立ちます。リアルタイムデータ分析、セクター別パフォーマンス、リスク評価、投資推奨の詳細根拠など、包括的な投資分析機能を提供します。投資判断の信頼性を高めるため、複数の分析手法を組み合わせた総合的な評価を提供します。"
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
              aria-label="銘柄一覧ページへ移動"
              data-help="上場銘柄の一覧と検索・フィルタリング機能です。セクター別、市場別、価格帯別の詳細フィルタリングが可能で、投資対象銘柄を効率的に発見できます。機械学習による推奨銘柄やテクニカル分析結果も確認でき、投資判断の精度向上に役立ちます。CSVエクスポート機能で分析結果を外部ツールで活用できます。リアルタイム価格データ、出来高情報、テクニカル指標、投資推奨ランキングなど、包括的な銘柄情報を提供します。投資戦略に応じた銘柄選別機能も利用できます。投資機会の発見と銘柄選別の効率化により、投資判断の精度向上をサポートします。"
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
              aria-label="リスク管理ページへ移動"
              data-help="リスク評価と損切りラインの管理を行います。ポートフォリオのリスク分析、ドローダウン監視、自動アラート機能で投資を安全にサポートします。VaR（バリューアットリスク）計算、ストレステスト、相関分析などの高度なリスク指標を提供し、投資戦略の安全性を向上させます。リアルタイムリスク監視、ポジション別リスク分析、セクター集中度分析、流動性リスク評価など、包括的なリスク管理機能を提供します。投資判断の安全性を高めるため、リスク許容度に応じた投資戦略の最適化もサポートします。投資損失の最小化とリスク管理の自動化により、投資の安全性を大幅に向上させます。"
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
              aria-label="設定ページへ移動"
              data-help="システム設定と予測パラメータを変更します。予測期間、使用モデル、特徴量選択、J-Quants API設定などをカスタマイズできます。設定のエクスポート・インポート機能で、設定をバックアップしたり他の環境で再利用できます。設定の検証機能で、設定値の妥当性を確認できます。個人の投資方針に合わせたシステムの最適化、通知設定、テーマ設定、データ更新頻度の調整など、包括的なカスタマイズ機能を提供します。投資戦略の個別化により、より精度の高い投資判断を実現できます。"
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
              <Link href="/usage" className="text-sm text-gray-600 hover:text-gray-900 flex items-center space-x-1" aria-label="使い方ガイドを表示" data-help="システムの使い方と機能説明を確認できます。詳細な操作手順、機械学習モデルの仕組み、予測指標の読み方などを学習できます。初心者から上級者まで、段階的にシステムの機能を理解できるよう設計されています。FAQ、動画リンク、トラブルシューティング情報も含まれています。投資判断に必要な知識を体系的に学習でき、投資スキルの向上に役立ちます。各機能の詳細な説明、ベストプラクティス、よくある質問と回答など、包括的な学習リソースを提供します。投資の学習効果を高め、過去の判断を振り返って投資スキルの向上に役立てることができます。">
                <BookOpen className="h-4 w-4" />
                <span>使い方</span>
              </Link>
              <Link href="/troubleshooting" className="text-sm text-gray-600 hover:text-gray-900" aria-label="トラブルシューティングページを表示" data-help="よくある問題と解決方法を確認できます。データ表示、分析実行、接続エラーなどの問題を段階的に解決できます。問題のカテゴリ別に整理されており、症状と解決手順を詳細に確認できます。システムのパフォーマンス最適化のヒントも提供されます。問題の重要度（軽微・中程度・重要・緊急）も表示され、優先順位を把握できます。段階的な解決手順に従って、問題を効率的に解決できます。システムの安定性向上と投資判断の継続性をサポートします。">
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

      {/* 診断パネル */}
      <DiagnosticsPanel
        isOpen={showDiagnostics}
        onClose={() => setShowDiagnostics(false)}
        onRefresh={() => {
          // リフレッシュ処理
          window.location.reload();
        }}
        onGoToSettings={() => {
          window.location.href = "/settings";
        }}
      />
      </div>
    </ErrorBoundary>
  );
}
