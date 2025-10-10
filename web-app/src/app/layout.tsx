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
import ResponsiveLayout from "@/components/ResponsiveLayout";
import GlobalHoverHelp from "@/components/GlobalHoverHelp";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "J-Quants株価予測システム",
  description: "J-Quants APIを使用した株価予測システム - モバイル最適化された投資判断支援ツール",
  keywords: ["株価","予測","J-Quants","機械学習","データ分析","投資"],
  icons: (() => {
    // クライアント・サーバ共通のパス解決
    const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
    const prefix = base ? `${base}` : "";
    const iconPath = `${prefix}/icon.svg`;
    return {
      icon: iconPath,
      shortcut: iconPath,
      apple: iconPath,
    } as const;
  })(),
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
};

export const viewport = {
  themeColor: "#2563eb",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={`${inter.className} theme-base`}>
        <ThemeProvider>
          <AccessibilityProvider>
            <SettingsProvider>
              <UserProfileProvider>
                <UnifiedErrorBoundary>
                  <GlobalErrorBoundary>
                    <div id="root">
                      {/* レスポンシブレイアウト */}
                      <ResponsiveLayout>
                        {children}
                      </ResponsiveLayout>
                      <Sidebar />
                      <BottomNav />
                      <GlobalHoverHelp />
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