import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SettingsProvider } from "@/contexts/SettingsContext";
import BottomNav from "@/components/mobile/BottomNav";
import Sidebar from "@/components/desktop/Sidebar";
import { UserProfileProvider } from "@/contexts/UserProfileContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "J-Quants株価予測システム",
  description: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール",
  keywords: ["株価", "予測", "J-Quants", "機械学習", "データ分析", "モバイル", "投資", "トレーディング"],
  authors: [{ name: "J-Quants Stock Prediction Team" }],
  robots: "index, follow",
  icons: {
    icon: "/favicon.ico",
    apple: "/favicon.ico",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "J-Quants株価予測",
  },
  openGraph: {
    title: "J-Quants株価予測システム",
    description: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール",
    type: "website",
    locale: "ja_JP",
  },
  twitter: {
    card: "summary_large_image",
    title: "J-Quants株価予測システム",
    description: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール",
  },
  other: {
    "mobile-web-app-capable": "yes",
    "mobile-web-app-status-bar-style": "default",
    "format-detection": "telephone=no",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: "#2563eb",
  colorScheme: "light",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <SettingsProvider>
          <UserProfileProvider>
          <div id="root">
            {/* モバイル用のパディング調整 */}
            <div className="pb-20 md:pb-0 md:pl-64">
              {children}
            </div>
            <Sidebar />
            <BottomNav />
          </div>
          </UserProfileProvider>
        </SettingsProvider>
      </body>
    </html>
  );
}