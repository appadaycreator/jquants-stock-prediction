import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { BarChart3, FileText, Home, Settings } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'J-Quants 株価予測システム',
  description: '機械学習による株価予測ダッシュボード',
  icons: {
    icon: './favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* サイドバー */}
          <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
            <div className="flex flex-col h-full">
              {/* ロゴ */}
              <div className="flex items-center px-6 py-6 border-b">
                <BarChart3 className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <h1 className="text-lg font-bold text-gray-900">J-Quants</h1>
                  <p className="text-sm text-gray-600">株価予測システム</p>
                </div>
              </div>

              {/* ナビゲーション */}
              <nav className="flex-1 px-4 py-6 space-y-2">
                <Link 
                  href="/"
                  className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Home className="h-5 w-5 mr-3" />
                  ダッシュボード
                </Link>
                <Link 
                  href="/reports/"
                  className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <FileText className="h-5 w-5 mr-3" />
                  レポート
                </Link>
                <Link 
                  href="/settings/"
                  className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Settings className="h-5 w-5 mr-3" />
                  設定
                </Link>
              </nav>

              {/* フッター */}
              <div className="px-6 py-4 border-t">
                <p className="text-xs text-gray-500">
                  © 2024 J-Quants Stock Prediction
                </p>
              </div>
            </div>
          </div>

          {/* メインコンテンツ */}
          <div className="pl-64">
            {children}
          </div>
        </div>
      </body>
    </html>
  )
}