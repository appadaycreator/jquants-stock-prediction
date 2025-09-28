"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, 
  TrendingUp, 
  Settings, 
  BookOpen, 
  FileText,
  Home,
  Eye,
  Calendar,
} from "lucide-react";

interface NavigationProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onAnalysisClick?: () => void;
  onSettingsClick?: () => void;
  onMonitoringClick?: () => void;
}

export default function Navigation({
  activeTab,
  onTabChange,
  onAnalysisClick,
  onSettingsClick,
  onMonitoringClick,
}: NavigationProps) {
  const pathname = usePathname();

  const navigationItems = [
    { 
      href: "/", 
      label: "ダッシュボード", 
      icon: Home,
      description: "メインダッシュボード",
    },
    { 
      href: "/today", 
      label: "今日の投資指示", 
      icon: Calendar,
      description: "本日の売買候補と指示",
    },
    { 
      href: "/reports", 
      label: "レポート", 
      icon: FileText,
      description: "詳細レポート",
    },
    { 
      href: "/settings", 
      label: "設定", 
      icon: Settings,
      description: "システム設定",
    },
    { 
      href: "/usage", 
      label: "使い方", 
      icon: BookOpen,
      description: "使用方法ガイド",
    },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* ロゴ・タイトル */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">J-Quants株価予測</h1>
                <p className="text-sm text-gray-600">機械学習による株価予測システム</p>
              </div>
            </div>
          </div>

          {/* ナビゲーションメニュー */}
          <div className="flex space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  prefetch={false}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                  title={item.description}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            
            {/* 銘柄監視管理ボタン */}
            {onMonitoringClick && (
              <button
                onClick={onMonitoringClick}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
                title="銘柄監視管理"
              >
                <Eye className="h-4 w-4" />
                <span>銘柄監視</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
