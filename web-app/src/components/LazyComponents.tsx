import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// チャートコンポーネントの動的インポート
export const LazyChart = dynamic(() => import('./Chart'), {
  loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded"></div>,
  ssr: false
})

// データテーブルの動的インポート
export const LazyDataTable = dynamic(() => import('./DataTable'), {
  loading: () => <div className="animate-pulse bg-gray-200 h-32 rounded"></div>,
  ssr: false
})

// 予測結果の動的インポート
export const LazyPredictionResults = dynamic(() => import('./PredictionResults'), {
  loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded"></div>,
  ssr: false
})

// 設定パネルの動的インポート
export const LazySettingsPanel = dynamic(() => import('./SettingsPanel'), {
  loading: () => <div className="animate-pulse bg-gray-200 h-32 rounded"></div>,
  ssr: false
})

// エラーハンドリングコンポーネント
export const LazyErrorBoundary = dynamic(() => import('./ErrorBoundary'), {
  loading: () => <div className="text-red-500">エラーが発生しました</div>,
  ssr: false
})

// ローディングコンポーネント
export const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <span className="ml-2 text-gray-600">読み込み中...</span>
  </div>
)

// エラーフォールバックコンポーネント
export const ErrorFallback = ({ error, resetError }: { error: Error; resetError: () => void }) => (
  <div className="flex flex-col items-center justify-center p-8 bg-red-50 rounded-lg">
    <h2 className="text-lg font-semibold text-red-800 mb-2">エラーが発生しました</h2>
    <p className="text-red-600 mb-4">{error.message}</p>
    <button
      onClick={resetError}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    >
      再試行
    </button>
  </div>
)
