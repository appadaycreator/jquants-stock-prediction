"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Menu, X } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMainOpen, setIsMainOpen] = useState(true);
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(true);

  // メインセクション
  const navigation = [
    { name: "ダッシュボード", href: "/", icon: "📊", description: "全体の投資状況と主要指標を一覧表示します。機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供します。複数の予測モデルの精度比較、特徴量重要度分析、予測誤差の詳細分析、モデル性能の可視化など、高度な分析機能を利用できます。プロの投資家向けの詳細な分析ツールとして、投資判断の精度向上に役立ちます。インタラクティブなチャートとレポート機能で、投資戦略の検証と改善に活用できます。リアルタイムデータ分析、セクター別パフォーマンス、リスク評価、投資推奨の詳細根拠など、包括的な投資分析機能を提供します。投資判断の信頼性を高めるため、複数の分析手法を組み合わせた総合的な評価を提供します。" },
    { name: "今日の指示", href: "/today", icon: "🎯", description: "今日の投資判断と推奨アクションを確認できます。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。データ更新状況の確認、上位候補銘柄の分析、保有銘柄の提案、メモ記録まで一連の流れを実行します。初心者でも迷わずに投資判断を行えるよう設計されており、毎日の投資活動を効率化できます。機械学習による推奨アクションとテクニカル分析を組み合わせた総合的な投資判断を提供します。投資の学習効果を高め、過去の判断を振り返って投資スキルの向上に役立てることができます。リアルタイムの市場データに基づく最新の投資判断を提供し、投資機会を見逃さないようサポートします。毎日の投資判断を標準化し、一貫性のある投資戦略を実現できます。" },
    { name: "シンプル投資判断", href: "/simple-dashboard", icon: "🎯", description: "初心者向けの分かりやすい投資判断画面です。複雑な分析結果をシンプルに表示し、重要な投資判断に集中できるよう設計されています。推奨アクション、損益状況、保有銘柄の情報を分かりやすく表示します。市場の最新動向に基づいて投資判断に必要な情報を最新に保ちます。リアルタイムで投資状況を監視し、重要な投資判断に必要な最新情報を確認できます。市場の開場・閉場状況も同時に更新され、投資タイミングを把握できます。投資機会を見逃さないよう、重要な価格変動や投資推奨の変更をリアルタイムで監視できます。投資判断の効率化と精度向上をサポートします。" },
    { name: "個人投資", href: "/personal-investment", icon: "💼", description: "個人の投資戦略とポートフォリオ管理を行います。AI/ルールベースによる投資提案、LSTM深層学習による株価予測、リアルタイム損益計算、パフォーマンス比較とランキング、損益推移グラフとチャート分析など、包括的な投資管理機能を提供します。個人の投資方針に合わせてシステムの動作を最適化し、より精度の高い投資判断を実現できます。投資の安全性と収益性のバランスを最適化できます。" },
  ];

  // 分析/データ/設定セクション
  const additionalFeatures = [
    { name: "詳細分析", href: "/dashboard", icon: "📈", description: "銘柄の詳細な技術分析とチャートを表示します。テクニカル指標、価格予測、機械学習分析結果を確認できます。移動平均線、RSI、MACD、ボリンジャーバンドなどの技術分析指標と、AIによる価格予測を詳細に分析できます。プロの投資家レベルの分析ツールで、投資判断の精度向上に役立ちます。インタラクティブなチャートで、ズーム、パン、指標の追加・削除が可能です。投資判断の信頼性を高めるため、推奨アクションの根拠となる分析結果を詳細に確認できます。投資判断の精度向上と継続的な改善をサポートします。" },
    { name: "銘柄一覧", href: "/listed-data", icon: "📋", description: "上場銘柄の一覧と検索・フィルタリング機能です。セクター別、市場別、価格帯別の詳細フィルタリングが可能で、投資対象銘柄を効率的に発見できます。機械学習による推奨銘柄やテクニカル分析結果も確認でき、投資判断の精度向上に役立ちます。CSVエクスポート機能で分析結果を外部ツールで活用できます。リアルタイム価格データ、出来高情報、テクニカル指標、投資推奨ランキングなど、包括的な銘柄情報を提供します。投資戦略に応じた銘柄選別機能も利用できます。投資機会の発見と銘柄選別の効率化をサポートします。" },
    { name: "ポートフォリオ", href: "/portfolio", icon: "💼", description: "保有銘柄の管理とパフォーマンス分析を行います。各銘柄の現在価格、損益率、次のアクション、目標価格・損切り価格を表示します。投資判断に直結する重要な情報を優先表示し、緊急アクションが必要な銘柄を強調表示します。ポートフォリオのリスク分析、ドローダウン監視、自動アラート機能で投資を安全にサポートします。投資の安全性と収益性のバランスを最適化できます。" },
    { name: "ウォッチリスト", href: "/watchlist", icon: "👁️", description: "注目銘柄の監視と価格アラートを設定できます。銘柄の現在価格、推奨アクション、信頼度、リスクレベル、目標価格などの情報を監視し、投資機会を見逃さないようサポートします。リアルタイムで価格変動を監視し、アラート条件の再評価も行われます。投資対象から除外する際や、監視を終了する際にも便利です。投資機会の発見と銘柄監視の効率化をサポートします。" },
    { name: "レポート", href: "/reports", icon: "📑", description: "詳細な分析レポートとパフォーマンス評価を確認します。予測精度の評価、モデル性能の可視化、投資戦略の検証と改善に役立つ詳細な分析結果を確認できます。レポートのエクスポート機能で分析結果を外部ツールで活用できます。投資判断の精度向上のため、過去の分析結果を振り返って学習効果を高めることができます。投資の継続的な学習とスキル向上をサポートします。" },
    { name: "分析履歴", href: "/analysis-history", icon: "📜", description: "過去の分析結果と予測精度の履歴を表示します。銘柄コードや銘柄名で分析履歴を検索でき、過去の分析結果から特定の銘柄の履歴を素早く見つけられます。分析日時、推奨アクション、信頼度、リスクレベルなどの詳細情報を確認できます。投資判断の精度向上のため、過去の分析結果を振り返って学習効果を高めることができます。投資の継続的な学習とスキル向上をサポートします。" },
    { name: "分析状況", href: "/analysis-progress", icon: "🔄", description: "現在実行中の分析の進捗状況を確認できます。実行中の分析の進捗状況、完了した分析の結果、システム統計をリアルタイムで監視できます。長時間の分析プロセスを監視し、完了タイミングを把握できます。システムのパフォーマンス指標も同時に更新され、分析エンジンの健全性を確認できます。投資判断の継続性とシステムの安定性をサポートします。" },
    { name: "リスク管理", href: "/risk", icon: "🛡️", description: "リスク評価と損切りラインの管理を行います。ポートフォリオのリスク分析、ドローダウン監視、自動アラート機能で投資を安全にサポートします。VaR（バリューアットリスク）計算、ストレステスト、相関分析などの高度なリスク指標を提供し、投資戦略の安全性を向上させます。リスク許容度に応じて過去の分析結果を絞り込んで確認できます。投資損失の最小化とリスク管理の自動化により、投資の安全性を大幅に向上させます。" },
    { name: "設定", href: "/settings", icon: "⚙️", description: "システム設定と予測パラメータを変更します。予測期間、使用モデル、特徴量選択、J-Quants API設定などをカスタマイズできます。設定のエクスポート・インポート機能で、設定をバックアップしたり他の環境で再利用できます。設定の検証機能で、設定値の妥当性を確認できます。個人の投資方針に合わせてシステムの動作を最適化し、より精度の高い投資判断を実現できます。投資戦略の個別化により、より精度の高い投資判断を実現できます。" },
    { name: "使い方", href: "/usage", icon: "📖", description: "システムの使い方と機能説明を確認できます。詳細な操作手順、機械学習モデルの仕組み、予測指標の読み方などを学習できます。初心者から上級者まで、段階的にシステムの機能を理解できるよう設計されています。FAQ、動画リンク、トラブルシューティング情報も含まれています。投資判断に必要な知識を体系的に学習できます。各機能の詳細な説明、ベストプラクティス、よくある質問と回答など、包括的な学習リソースを提供します。投資の継続的な学習とスキル向上をサポートします。" },
  ];

  // ローカルストレージから状態を復元
  useEffect(() => {
    const savedState = localStorage.getItem("sidebar-collapsed");
    if (savedState !== null) {
      setIsCollapsed(JSON.parse(savedState));
    }
    const savedMain = localStorage.getItem("sidebar-main-open");
    const savedAdv = localStorage.getItem("sidebar-advanced-open");
    if (savedMain !== null) setIsMainOpen(JSON.parse(savedMain));
    if (savedAdv !== null) setIsAdvancedOpen(JSON.parse(savedAdv));
  }, []);

  // 状態をローカルストレージに保存
  const toggleCollapse = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    localStorage.setItem("sidebar-collapsed", JSON.stringify(newState));
    // カスタムイベントを発火して他のコンポーネントに通知
    window.dispatchEvent(new CustomEvent("sidebar-toggle"));
  };

  const toggleMain = () => {
    const next = !isMainOpen;
    setIsMainOpen(next);
    localStorage.setItem("sidebar-main-open", JSON.stringify(next));
  };

  const toggleAdvanced = () => {
    const next = !isAdvancedOpen;
    setIsAdvancedOpen(next);
    localStorage.setItem("sidebar-advanced-open", JSON.stringify(next));
  };

  const toggleMobile = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  return (
    <>
      {/* モバイル用ハンバーガーメニュー */}
      <button
        onClick={toggleMobile}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-gray-200"
        aria-label="メニューを開く"
        data-help="メニューを開きます。ナビゲーション項目へアクセスできます。"
      >
        {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* モバイル用オーバーレイ */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* デスクトップ用サイドバー */}
      <nav className={`hidden lg:block fixed left-0 top-0 h-full bg-white border-r border-gray-200 z-40 transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-64"
      }`}>
        <div className="p-4">
          {/* ヘッダーとトグルボタン */}
          <div className="flex items-center justify-between mb-6">
            {!isCollapsed && (
              <h2 className="text-lg font-semibold text-gray-900">
                J-Quants株価予測
              </h2>
            )}
            <button
              onClick={toggleCollapse}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={isCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}
              aria-label={isCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}
              data-help={isCollapsed ? "サイドバーを展開します。" : "サイドバーを折りたたみます。"}
            >
              {isCollapsed ? (
                <ChevronRight className="h-5 w-5 text-gray-600" />
              ) : (
                <ChevronLeft className="h-5 w-5 text-gray-600" />
              )}
            </button>
          </div>
          
          <div className="space-y-2">
            {/* メイン: アコーディオンヘッダー */}
            {!isCollapsed && (
              <button
                onClick={toggleMain}
                className="w-full flex items-center justify-between px-3 pb-2 text-xs font-semibold text-gray-500 hover:text-gray-700 transition-colors"
                aria-expanded={isMainOpen}
                aria-controls="sidebar-section-main"
                data-help="メインセクションの表示を切り替えます。"
              >
                <span>メイン</span>
                <span className={`transition-transform ${isMainOpen ? "rotate-0" : "-rotate-90"}`}>▾</span>
              </button>
            )}
            {/* メイン: リスト */}
            <div
              id="sidebar-section-main"
              role="region"
              aria-hidden={!isMainOpen && !isCollapsed}
              className={`overflow-hidden transition-all duration-300 ${
                isCollapsed ? "" : isMainOpen ? "max-h-[800px]" : "max-h-0"
              }`}
            >
              {navigation.map((item) => {
                const isRoot = item.href === "/";
                const isActive = isRoot
                  ? pathname === "/"
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${
                      isActive
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    title={isCollapsed ? item.name : undefined}
                    aria-label={item.name}
                    data-help={item.description}
                  >
                    <span className="text-lg flex-shrink-0">{item.icon}</span>
                    {!isCollapsed && (
                      <span className="font-medium truncate">{item.name}</span>
                    )}
                    {isCollapsed && (
                      <div className="absolute left-16 bg-gray-900 text-white text-sm px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                        {item.name}
                      </div>
                    )}
                  </Link>
                );
              })}
            </div>
            
            <div className="border-t border-gray-200 my-4"></div>

            {/* 分析・設定: アコーディオンヘッダー */}
            {!isCollapsed && (
              <button
                onClick={toggleAdvanced}
                className="w-full flex items-center justify-between px-3 pb-2 text-xs font-semibold text-gray-500 hover:text-gray-700 transition-colors"
                aria-expanded={isAdvancedOpen}
                aria-controls="sidebar-section-advanced"
                data-help="分析・設定セクションの表示を切り替えます。"
              >
                <span>分析・設定</span>
                <span className={`transition-transform ${isAdvancedOpen ? "rotate-0" : "-rotate-90"}`}>▾</span>
              </button>
            )}
            {/* 分析・設定: リスト */}
            <div
              id="sidebar-section-advanced"
              role="region"
              aria-hidden={!isAdvancedOpen && !isCollapsed}
              className={`overflow-hidden transition-all duration-300 ${
                isCollapsed ? "" : isAdvancedOpen ? "max-h-[1200px]" : "max-h-0"
              }`}
            >
              {additionalFeatures.map((item) => {
                const isRoot = item.href === "/";
                const isActive = isRoot
                  ? pathname === "/"
                  : pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${
                      isActive
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                    title={isCollapsed ? item.name : undefined}
                    aria-label={item.name}
                    data-help={item.description}
                  >
                    <span className="text-lg flex-shrink-0">{item.icon}</span>
                    {!isCollapsed && (
                      <span className="font-medium truncate">{item.name}</span>
                    )}
                    {isCollapsed && (
                      <div className="absolute left-16 bg-gray-900 text-white text-sm px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                        {item.name}
                      </div>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* モバイル用サイドバー */}
      <nav className={`lg:hidden fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 z-50 transform transition-transform duration-300 ${
        isMobileOpen ? "translate-x-0" : "-translate-x-full"
      }`}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              J-Quants株価予測
            </h2>
            <button
              onClick={() => setIsMobileOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <X className="h-5 w-5 text-gray-600" />
            </button>
          </div>
          
          <div className="space-y-2">
            {/* モバイル: メイン */}
            <div className="px-3 pb-2 text-xs font-semibold text-gray-500">メイン</div>
            {navigation.map((item) => {
              const isRoot = item.href === "/";
              const isActive = isRoot
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
            
            <div className="border-t border-gray-200 my-4"></div>
            {/* モバイル: 分析・設定 */}
            <div className="px-3 pb-2 text-xs font-semibold text-gray-500">分析・設定</div>
            {additionalFeatures.map((item) => {
              const isRoot = item.href === "/";
              const isActive = isRoot
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
    </>
  );
}
