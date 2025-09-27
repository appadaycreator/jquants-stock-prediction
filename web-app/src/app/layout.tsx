import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "J-Quants株価予測システム",
  description: "J-Quants APIを使用した株価予測システム",
  keywords: ["株価", "予測", "J-Quants", "機械学習", "データ分析"],
  authors: [{ name: "J-Quants Stock Prediction Team" }],
  viewport: "width=device-width, initial-scale=1",
  robots: "index, follow",
  icons: {
    icon: "/favicon.ico",
    apple: "/favicon.ico",
  },
  themeColor: "#000000",
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div id="root">
          {children}
        </div>
      </body>
    </html>
  );
}