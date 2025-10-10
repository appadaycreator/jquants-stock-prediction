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
  {
    href: "/",
    label: "ホーム",
    icon: "🏠",
    shortLabel: "ホーム",
  },
  {
    href: "/today",
    label: "今日のタスク",
    icon: "🎯",
    shortLabel: "今日",
  },
  {
    href: "/dashboard",
    label: "詳細分析",
    icon: "📊",
    shortLabel: "分析",
  },
  {
    href: "/listed-data",
    label: "銘柄一覧",
    icon: "📋",
    shortLabel: "銘柄",
  },
  {
    href: "/portfolio",
    label: "ポートフォリオ",
    icon: "💼",
    shortLabel: "ポート",
  },
  {
    href: "/watchlist",
    label: "ウォッチリスト",
    icon: "👁️",
    shortLabel: "ウォッチ",
  },
];

export default function BottomNav() {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
                <Link
                  href="/personal-investment"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>💼</span>
                  <span>個人投資</span>
                </Link>
                <Link
                  href="/reports"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>📈</span>
                  <span>レポート</span>
                </Link>
                <Link
                  href="/analysis-progress"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>🔄</span>
                  <span>分析状況</span>
                </Link>
                <Link
                  href="/test-coverage"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>🧪</span>
                  <span>テストカバレッジ</span>
                </Link>
              </div>
            </div>
          </div>
        </>
      )}

      {/* デスクトップのサイドバーは `components/desktop/Sidebar.tsx` を使用（重複実装を排除） */}
    </>
  );
}
