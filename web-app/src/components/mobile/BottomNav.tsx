"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  shortLabel: string;
}

const navItems: NavItem[] = [
  { href: "/", label: "ダッシュボード", icon: "📊", shortLabel: "ホーム" },
  { href: "/today", label: "今日の指示", icon: "🎯", shortLabel: "今日" },
  { href: "/simple-dashboard", label: "シンプル投資判断", icon: "🎯", shortLabel: "判断" },
  { href: "/five-min-routine", label: "5分ルーティン", icon: "⏱️", shortLabel: "5分" },
  { href: "/personal-investment", label: "個人投資", icon: "💼", shortLabel: "投資" },
];

export default function BottomNav() {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMainOpen, setIsMainOpen] = useState(true);
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* モバイル用固定ボトムナビゲーション */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden">
        <div className="flex items-center justify-around px-3 py-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center min-h-[48px] min-w-[48px] px-3 py-2 rounded-lg transition-colors touch-target ${
                isActive(item.href)
                  ? "text-blue-600 bg-blue-50"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
              }`}
            >
              <span className="text-xl mb-1 leading-none">{item.icon}</span>
              <span className="text-[13px] font-medium leading-tight text-center">
                {item.shortLabel}
              </span>
            </Link>
          ))}
        </div>
      </nav>

      {/* ハンバーガーメニュー（モバイル用） */}
      <div className="fixed top-4 right-4 z-50 md:hidden">
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="bg-white shadow-lg rounded-full p-3 border border-gray-200 min-h-[48px] min-w-[48px] flex items-center justify-center touch-target"
          aria-label="メニューを開く"
        >
          <span className="text-lg">☰</span>
        </button>
      </div>

      {/* オーバーレイメニュー */}
      {isMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setIsMenuOpen(false)}
          />
          <div className="fixed top-16 right-4 bg-white rounded-lg shadow-lg border border-gray-200 z-50 md:hidden min-w-[200px]">
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">メニュー</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setIsMainOpen(!isMainOpen)}
                  className="w-full flex items-center justify-between px-2 py-1 text-xs font-semibold text-gray-600 hover:text-gray-800"
                  aria-expanded={isMainOpen}
                >
                  <span>メイン</span>
                  <span className={`transition-transform ${isMainOpen ? "rotate-0" : "-rotate-90"}`}>▾</span>
                </button>
                <div className={`overflow-hidden transition-all duration-200 ${isMainOpen ? "max-h-[600px]" : "max-h-0"}`}>
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </div>

                <button
                  onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
                  className="w-full flex items-center justify-between px-2 py-1 text-xs font-semibold text-gray-600 hover:text-gray-800"
                  aria-expanded={isAdvancedOpen}
                >
                  <span>分析・設定</span>
                  <span className={`transition-transform ${isAdvancedOpen ? "rotate-0" : "-rotate-90"}`}>▾</span>
                </button>
                <div className={`overflow-hidden transition-all duration-200 ${isAdvancedOpen ? "max-h-[1000px]" : "max-h-0"}`}>
                <Link href="/listed-data" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>📋</span>
                  <span>銘柄一覧</span>
                </Link>
                <Link href="/portfolio" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>💼</span>
                  <span>ポートフォリオ</span>
                </Link>
                <Link href="/watchlist" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>👁️</span>
                  <span>ウォッチリスト</span>
                </Link>
                <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>📈</span>
                  <span>詳細分析</span>
                </Link>
                <Link href="/reports" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>📑</span>
                  <span>レポート</span>
                </Link>
                <Link href="/analysis-history" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>📜</span>
                  <span>分析履歴</span>
                </Link>
                <Link href="/analysis-progress" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>🔄</span>
                  <span>分析状況</span>
                </Link>
                <Link href="/test-coverage" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>🧪</span>
                  <span>テストカバレッジ</span>
                </Link>
                <Link href="/risk" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>🛡️</span>
                  <span>リスク管理</span>
                </Link>
                <Link href="/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>⚙️</span>
                  <span>設定</span>
                </Link>
                <Link href="/usage" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm" onClick={() => setIsMenuOpen(false)}>
                  <span>📖</span>
                  <span>使い方</span>
                </Link>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* デスクトップのサイドバーは `components/desktop/Sidebar.tsx` を使用（重複実装を排除） */}
    </>
  );
}
