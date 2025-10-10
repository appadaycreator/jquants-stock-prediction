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
    { name: "ダッシュボード", href: "/", icon: "📊", description: "全体の投資状況と主要指標を一覧表示します。機械学習モデルの比較、パフォーマンス指標、市場インサイトなど、深い分析機能を提供します。" },
    { name: "今日の投資指示", href: "/today", icon: "🎯", description: "今日の投資判断と推奨アクションを確認できます。5分で完了する効率的な投資判断フローで、重要なアクションを素早く実行できます。" },
    { name: "ポートフォリオ", href: "/personal-investment", icon: "💼", description: "個人の投資戦略とポートフォリオ管理を行います。AI/ルールベースによる投資提案、LSTM深層学習による株価予測、リアルタイム損益計算など、包括的な投資管理機能を提供します。" },
  ];

  // 分析/データ/設定セクション
  const additionalFeatures = [
    { name: "詳細分析", href: "/dashboard", icon: "📈", description: "銘柄の詳細な技術分析とチャートを表示します。テクニカル指標、価格予測、機械学習分析結果を確認できます。" },
    { name: "ウォッチリスト", href: "/watchlist", icon: "👁️", description: "注目銘柄の監視と価格アラートを設定できます。銘柄の現在価格、推奨アクション、信頼度、リスクレベル、目標価格などの情報を監視し、投資機会を見逃さないようサポートします。" },
    { name: "リスク管理", href: "/risk", icon: "🛡️", description: "リスク評価と損切りラインの管理を行います。ポートフォリオのリスク分析、ドローダウン監視、自動アラート機能で投資を安全にサポートします。" },
    { name: "設定", href: "/settings", icon: "⚙️", description: "システム設定と予測パラメータを変更します。予測期間、使用モデル、特徴量選択、J-Quants API設定などをカスタマイズできます。" },
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
