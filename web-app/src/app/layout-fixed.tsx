/**
 * 修正版レイアウト
 * ナビゲーション機能の修復
 */

"use client";

import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SettingsProvider } from "@/contexts/SettingsContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AccessibilityProvider } from "@/components/AccessibilityProvider";
import BottomNav from "@/components/mobile/BottomNav";
import Sidebar from "@/components/desktop/Sidebar";
import { UserProfileProvider } from "@/contexts/UserProfileContext";
import GlobalErrorBoundary from "@/components/GlobalErrorBoundary";
import UnifiedErrorBoundary from "@/components/UnifiedErrorBoundary";
import FixedResponsiveLayout from "@/components/FixedResponsiveLayout";
import { useEffect, useState } from "react";
import { optimizedErrorHandler } from "@/lib/unified-error-handler";

const inter = Inter({ subsets: ["latin"] });

// クライアントサイドレンダリング用のメタデータ設定
const setMetadata = () => {
  if (typeof document !== "undefined") {
    // タイトル設定
    document.title = "J-Quants株価予測システム";
    
    // メタタグの設定
    const metaTags = [
      { name: "description", content: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール" },
      { name: "keywords", content: "株価,予測,J-Quants,機械学習,データ分析,モバイル,投資,トレーディング" },
      { name: "author", content: "J-Quants Stock Prediction Team" },
      { name: "robots", content: "index, follow" },
      { name: "viewport", content: "width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes" },
      { name: "theme-color", content: "#2563eb" },
      { name: "mobile-web-app-capable", content: "yes" },
      { name: "mobile-web-app-status-bar-style", content: "default" },
      { name: "format-detection", content: "telephone=no" },
      { property: "og:title", content: "J-Quants株価予測システム" },
      { property: "og:description", content: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール" },
      { property: "og:type", content: "website" },
      { property: "og:locale", content: "ja_JP" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "J-Quants株価予測システム" },
      { name: "twitter:description", content: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール" },
    ];
    
    metaTags.forEach(({ name, content, property }) => {
      const selector = property ? `meta[property="${property}"]` : `meta[name="${name}"]`;
      let meta = document.querySelector(selector) as HTMLMetaElement;
      
      if (!meta) {
        meta = document.createElement("meta");
        if (property) {
          meta.setAttribute("property", property);
        } else if (name) {
          meta.setAttribute("name", name);
        }
        document.head.appendChild(meta);
      }
      
      meta.setAttribute("content", content);
    });
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    setMetadata();
    
    // 自動復旧システムを開始
    startAutoRecovery();
  }, []);

  if (!isClient) {
    // サーバーサイドレンダリング時のフォールバック
    return (
      <html lang="ja">
        <head>
          <title>J-Quants株価予測システム</title>
          <meta name="description" content="J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール" />
          <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes" />
          <meta name="theme-color" content="#2563eb" />
        </head>
        <body className={inter.className}>
          <div id="root">
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">読み込み中...</p>
              </div>
            </div>
          </div>
        </body>
      </html>
    );
  }

  return (
    <html lang="ja">
      <body className={inter.className}>
        <ThemeProvider>
          <AccessibilityProvider>
            <SettingsProvider>
              <UserProfileProvider>
                <UnifiedErrorBoundary>
                  <GlobalErrorBoundary>
                    <div id="root" className="theme-base">
                      {/* 修正版レスポンシブレイアウト */}
                      <FixedResponsiveLayout>
                        {children}
                      </FixedResponsiveLayout>
                      <Sidebar />
                      <BottomNav />
                    </div>
                  </GlobalErrorBoundary>
                </UnifiedErrorBoundary>
              </UserProfileProvider>
            </SettingsProvider>
          </AccessibilityProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
