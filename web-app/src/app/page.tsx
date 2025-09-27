'use client'

import { useEffect, useState } from 'react'
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter
} from 'recharts'
import { TrendingUp, BarChart3, Target, Database, CheckCircle, Play, Settings, RefreshCw } from 'lucide-react'

// 型定義
interface StockData {
  date: string
  code: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  sma_5?: number
  sma_10?: number
  sma_25?: number
  sma_50?: number
}

interface ModelComparison {
  name: string
  type: string
  mae: number
  mse: number
  rmse: number
  r2: number
  rank: number
}

interface FeatureAnalysis {
  feature: string
  importance: number
  percentage: number
}

interface PredictionData {
  index: number
  actual: number
  predicted: number
  error: number
  error_percentage: number
}

interface DashboardSummary {
  total_data_points: number
  prediction_period: string
  best_model: string
  mae: string
  r2: string
  last_updated: string
}

// カラーパレット
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [stockData, setStockData] = useState<StockData[]>([])
  const [modelComparison, setModelComparison] = useState<ModelComparison[]>([])
  const [featureAnalysis, setFeatureAnalysis] = useState<FeatureAnalysis[]>([])
  const [predictions, setPredictions] = useState<PredictionData[]>([])
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisStatus, setAnalysisStatus] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      const [summaryRes, stockRes, modelRes, featureRes, predRes] = await Promise.all([
        fetch('./data/dashboard_summary.json'),
        fetch('./data/stock_data.json'),
        fetch('./data/model_comparison.json'),
        fetch('./data/feature_analysis.json'),
        fetch('./data/prediction_results.json')
      ])

      const summaryData = await summaryRes.json()
      const stockDataRes = await stockRes.json()
      const modelDataRes = await modelRes.json()
      const featureDataRes = await featureRes.json()
      const predDataRes = await predRes.json()

      setSummary(summaryData)
      setStockData(stockDataRes.slice(0, 100)) // 最初の100件のみ表示
      setModelComparison(modelDataRes)
      setFeatureAnalysis(featureDataRes)
      setPredictions(predDataRes)
      
    } catch (error) {
      console.error('データの読み込みに失敗:', error)
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    try {
      setIsAnalyzing(true)
      setAnalysisProgress(0)
      setAnalysisStatus('分析を開始しています...')
      
      // プログレスバーのシミュレーション
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + Math.random() * 10
        })
      }, 500)

      // 分析実行のシミュレーション
      setAnalysisStatus('分析が完了しました。データを更新しています...')
      setAnalysisProgress(100)
      
      // データを再読み込み
      await loadData()
      
      setTimeout(() => {
        setShowAnalysisModal(false)
        setIsAnalyzing(false)
        setAnalysisProgress(0)
        setAnalysisStatus('')
      }, 1000)
      
    } catch (error) {
      console.error('分析実行エラー:', error)
      setAnalysisStatus('分析の実行に失敗しました')
      setIsAnalyzing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">データを読み込み中...</p>
        </div>
      </div>
    )
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ja-JP')
  }

  const chartData = stockData.map(item => ({
    date: formatDate(item.date),
    実際価格: item.close,
    SMA_5: item.sma_5,
    SMA_10: item.sma_10,
    SMA_25: item.sma_25,
    SMA_50: item.sma_50,
    出来高: item.volume / 1000000 // 百万単位
  }))

  const predictionChartData = predictions.slice(0, 50).map(item => ({
    index: item.index,
    実際値: item.actual,
    予測値: item.predicted
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">J-Quants 株価予測ダッシュボード</h1>
              <p className="text-gray-600">機械学習による株価予測システム</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-600">
                  システム: 正常稼働中
                </span>
                <span className="text-sm text-gray-600">
                  最終更新: {summary ? summary.last_updated : '-'}
                </span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowAnalysisModal(true)}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Play className="h-4 w-4 mr-2" />
                  分析実行
                </button>
                <button
                  onClick={() => setShowSettingsModal(true)}
                  className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  設定
                </button>
                <button
                  onClick={loadData}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  更新
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* タブナビゲーション */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: '概要', icon: BarChart3 },
              { id: 'predictions', label: '予測結果', icon: TrendingUp },
              { id: 'models', label: 'モデル比較', icon: Target },
              { id: 'analysis', label: '分析', icon: Database }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* サマリーカード */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">最優秀モデル</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {summary?.best_model?.toUpperCase() || '-'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Target className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">予測精度 (R²)</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {summary?.r2 || '-'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">MAE</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {summary?.mae || '-'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Database className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">データ数</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {summary?.total_data_points || '-'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 株価チャート */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">株価推移と移動平均</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="実際価格" stroke="#2563eb" strokeWidth={2} />
                  <Line type="monotone" dataKey="SMA_5" stroke="#dc2626" strokeWidth={1} />
                  <Line type="monotone" dataKey="SMA_10" stroke="#059669" strokeWidth={1} />
                  <Line type="monotone" dataKey="SMA_25" stroke="#d97706" strokeWidth={1} />
                  <Line type="monotone" dataKey="SMA_50" stroke="#7c3aed" strokeWidth={1} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'predictions' && (
          <div className="space-y-6">
            {/* 予測結果チャート */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">予測 vs 実際値</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={predictionChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="実際値" stroke="#2563eb" strokeWidth={2} />
                  <Line type="monotone" dataKey="予測値" stroke="#dc2626" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 予測精度分布 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">予測誤差分布</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={predictions.slice(0, 20).map(p => ({ 
                  index: p.index, 
                  誤差: p.error.toFixed(2) 
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="誤差" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div className="space-y-6">
            {/* モデル比較表 */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">モデル性能比較</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">順位</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">モデル名</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAE</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RMSE</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">R²</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {modelComparison.map((model, index) => (
                      <tr key={model.name} className={index === 0 ? 'bg-green-50' : ''}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {index + 1}
                          {index === 0 && <span className="ml-2 text-green-600">🏆</span>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.mae.toFixed(4)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.rmse.toFixed(4)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{model.r2.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* モデル性能比較チャート */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">MAE比較</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={modelComparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="mae" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            {/* 特徴量重要度 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">特徴量重要度</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={featureAnalysis} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="feature" type="category" width={100} />
                    <Tooltip />
                    <Bar dataKey="percentage" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">特徴量重要度分布</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={featureAnalysis.map(item => ({ ...item, name: item.feature }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="percentage"
                    >
                      {featureAnalysis.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 散布図 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">実際値 vs 予測値散布図</h3>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart data={predictions.slice(0, 50)}>
                  <CartesianGrid />
                  <XAxis dataKey="actual" name="実際値" />
                  <YAxis dataKey="predicted" name="予測値" />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter name="予測ポイント" data={predictions.slice(0, 50)} fill="#8884d8" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </main>

      {/* 分析実行モーダル */}
      {showAnalysisModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">分析実行</h3>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            {!isAnalyzing ? (
              <div className="space-y-4">
                <p className="text-gray-600">
                  新しい分析を実行しますか？この処理には数分かかる場合があります。
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowAnalysisModal(false)}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    キャンセル
                  </button>
                  <button
                    onClick={runAnalysis}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    実行
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">{analysisStatus}</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${analysisProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500 text-center">
                  {Math.round(analysisProgress)}% 完了
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 設定モーダル */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">設定</h3>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  予測期間（日数）
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="7">7日</option>
                  <option value="14">14日</option>
                  <option value="30" selected>30日</option>
                  <option value="60">60日</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用するモデル
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="all">すべてのモデル</option>
                  <option value="linear">線形回帰</option>
                  <option value="random_forest">ランダムフォレスト</option>
                  <option value="xgboost">XGBoost</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  特徴量選択
                </label>
                <div className="space-y-2">
                  {['SMA_5', 'SMA_10', 'SMA_25', 'SMA_50', 'RSI', 'MACD', 'ボリンジャーバンド'].map(feature => (
                    <label key={feature} className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  onClick={() => setShowSettingsModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={() => {
                    // 設定保存のロジック
                    setShowSettingsModal(false)
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  保存
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}