import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SettingsProvider } from "../contexts/SettingsContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "J-Quants株価予測システム",
  description: "J-Quants APIを使用した株価予測システム",
  keywords: ["株価", "予測", "J-Quants", "機械学習", "データ分析"],
  authors: [{ name: "J-Quants Stock Prediction Team" }],
  robots: "index, follow",
  icons: {
    icon: "/jquants-stock-prediction/favicon.ico",
    apple: "/jquants-stock-prediction/favicon.ico",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "J-Quants株価予測",
  },
  openGraph: {
    title: "J-Quants株価予測システム",
    description: "J-Quants APIを使用した株価予測システム",
    type: "website",
    locale: "ja_JP",
  },
  twitter: {
    card: "summary_large_image",
    title: "J-Quants株価予測システム",
    description: "J-Quants APIを使用した株価予測システム",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#000000",
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
          <div id="root">
            {children}
          </div>
        </SettingsProvider>
      </body>
    </html>
  );
}