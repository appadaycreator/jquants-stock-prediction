'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Settings, Save, RefreshCw, Database, Cpu, BarChart, Play, AlertCircle, CheckCircle, BookOpen } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    prediction: {
      days: 30
    },
    model: {
      type: 'all',
      primary_model: 'xgboost',
      compare_models: true,
      auto_retrain: false,
      retrain_frequency: 'weekly'
    },
    data: {
      refresh_interval: 'daily',
      max_data_points: 1000,
      include_technical_indicators: true
    },
    features: {
      selected: ['sma_5', 'sma_10', 'sma_25', 'sma_50', 'rsi', 'macd']
    },
    ui: {
      theme: 'light',
      refresh_rate: 30,
      show_tooltips: true
    }
  })

  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('')

  useEffect(() => {
    loadSettings()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const loadSettings = async () => {
    try {
      setLoading(true)
      // ローカルストレージから設定を読み込み
      const savedSettings = localStorage.getItem('jquants-settings')
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings)
        setSettings(prev => ({
          ...prev,
          ...parsedSettings
        }))
      }
    } catch (error) {
      console.error('設定の読み込みに失敗:', error)
      showMessage('設定の読み込みに失敗しました', 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (text: string, type: 'success' | 'error') => {
    setMessage(text)
    setMessageType(type)
    setTimeout(() => {
      setMessage('')
      setMessageType('')
    }, 3000)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      // ローカルストレージに設定を保存
      localStorage.setItem('jquants-settings', JSON.stringify(settings))
      showMessage('設定が正常に保存されました', 'success')
    } catch (error) {
      console.error('設定保存エラー:', error)
      showMessage('設定の保存に失敗しました', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (confirm('設定をリセットしますか？')) {
      setSettings({
        prediction: {
          days: 30
        },
        model: {
          type: 'all',
          primary_model: 'xgboost',
          compare_models: true,
          auto_retrain: false,
          retrain_frequency: 'weekly'
        },
        data: {
          refresh_interval: 'daily',
          max_data_points: 1000,
          include_technical_indicators: true
        },
        features: {
          selected: ['sma_5', 'sma_10', 'sma_25', 'sma_50', 'rsi', 'macd']
        },
        ui: {
          theme: 'light',
          refresh_rate: 30,
          show_tooltips: true
        }
      })
    }
  }

  const runAnalysis = async () => {
    try {
      // 分析実行のシミュレーション
      showMessage('分析を実行しています...', 'success')
      
      // 実際の実装では、ここでPythonスクリプトを実行するか、
      // サーバーサイドのAPIエンドポイントを呼び出す
      setTimeout(() => {
        showMessage('分析が完了しました（シミュレーション）', 'success')
      }, 2000)
    } catch (error) {
      console.error('分析実行エラー:', error)
      showMessage('分析の実行に失敗しました', 'error')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">設定を読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">システム設定</h1>
              <p className="text-gray-600">予測システムの動作を設定</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/usage"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
              >
                <BookOpen className="h-4 w-4 mr-2" />
                使い方
              </Link>
              <button
                onClick={runAnalysis}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <Play className="h-4 w-4 mr-2" />
                分析実行
              </button>
              <button
                onClick={handleReset}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                リセット
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? '保存中...' : '保存'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* メッセージ表示 */}
      {message && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          messageType === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <div className="flex items-center">
            {messageType === 'success' ? (
              <CheckCircle className="h-5 w-5 mr-2" />
            ) : (
              <AlertCircle className="h-5 w-5 mr-2" />
            )}
            {message}
          </div>
        </div>
      )}

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* 予測設定 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <BarChart className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">予測設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  予測期間（日数）
                </label>
                <input
                  type="number"
                  value={settings.prediction.days}
                  onChange={(e) => setSettings({
                    ...settings,
                    prediction: { ...settings.prediction, days: parseInt(e.target.value) }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用するモデル
                </label>
                <select 
                  value={settings.model.type}
                  onChange={(e) => setSettings({
                    ...settings,
                    model: { ...settings.model, type: e.target.value }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="all">すべてのモデル</option>
                  <option value="linear">線形回帰</option>
                  <option value="random_forest">ランダムフォレスト</option>
                  <option value="xgboost">XGBoost</option>
                </select>
              </div>
            </div>
          </div>

          {/* 特徴量設定 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">特徴量設定</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { key: 'sma_5', label: 'SMA_5' },
                { key: 'sma_10', label: 'SMA_10' },
                { key: 'sma_25', label: 'SMA_25' },
                { key: 'sma_50', label: 'SMA_50' },
                { key: 'rsi', label: 'RSI' },
                { key: 'macd', label: 'MACD' },
                { key: 'bollinger_upper', label: 'ボリンジャー上' },
                { key: 'bollinger_lower', label: 'ボリンジャー下' }
              ].map(feature => (
                <label key={feature.key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.features.selected.includes(feature.key)}
                    onChange={(e) => {
                      const newSelected = e.target.checked
                        ? [...settings.features.selected, feature.key]
                        : settings.features.selected.filter(f => f !== feature.key)
                      setSettings({
                        ...settings,
                        features: { ...settings.features, selected: newSelected }
                      })
                    }}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{feature.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* モデル設定 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Cpu className="h-6 w-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">モデル設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  プライマリモデル
                </label>
                <select 
                  value={settings.model.primary_model}
                  onChange={(e) => setSettings({
                    ...settings,
                    model: { ...settings.model, primary_model: e.target.value }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="xgboost">XGBoost</option>
                  <option value="random_forest">Random Forest</option>
                  <option value="linear_regression">線形回帰</option>
                  <option value="ridge">Ridge回帰</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  再訓練頻度
                </label>
                <select 
                  value={settings.model.retrain_frequency}
                  onChange={(e) => setSettings({
                    ...settings,
                    model: { ...settings.model, retrain_frequency: e.target.value }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="daily">毎日</option>
                  <option value="weekly">毎週</option>
                  <option value="monthly">毎月</option>
                  <option value="manual">手動</option>
                </select>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.model.compare_models}
                  onChange={(e) => setSettings({
                    ...settings,
                    model: { ...settings.model, compare_models: e.target.checked }
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  モデル比較を有効にする
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.model.auto_retrain}
                  onChange={(e) => setSettings({
                    ...settings,
                    model: { ...settings.model, auto_retrain: e.target.checked }
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  自動再訓練を有効にする
                </label>
              </div>
            </div>
          </div>

          {/* データ設定 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Database className="h-6 w-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">データ設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  データ更新間隔
                </label>
                <select 
                  value={settings.data.refresh_interval}
                  onChange={(e) => setSettings({
                    ...settings,
                    data: { ...settings.data, refresh_interval: e.target.value }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="realtime">リアルタイム</option>
                  <option value="hourly">1時間ごと</option>
                  <option value="daily">毎日</option>
                  <option value="weekly">毎週</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  最大データポイント数
                </label>
                <input
                  type="number"
                  value={settings.data.max_data_points}
                  onChange={(e) => setSettings({
                    ...settings,
                    data: { ...settings.data, max_data_points: parseInt(e.target.value) }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.data.include_technical_indicators}
                  onChange={(e) => setSettings({
                    ...settings,
                    data: { ...settings.data, include_technical_indicators: e.target.checked }
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  技術指標を含める
                </label>
              </div>
            </div>
          </div>

          {/* UI設定 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <BarChart className="h-6 w-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">UI設定</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  テーマ
                </label>
                <select 
                  value={settings.ui.theme}
                  onChange={(e) => setSettings({
                    ...settings,
                    ui: { ...settings.ui, theme: e.target.value }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="light">ライト</option>
                  <option value="dark">ダーク</option>
                  <option value="auto">自動</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  更新間隔（秒）
                </label>
                <input
                  type="number"
                  value={settings.ui.refresh_rate}
                  onChange={(e) => setSettings({
                    ...settings,
                    ui: { ...settings.ui, refresh_rate: parseInt(e.target.value) }
                  })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.ui.show_tooltips}
                  onChange={(e) => setSettings({
                    ...settings,
                    ui: { ...settings.ui, show_tooltips: e.target.checked }
                  })}
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">
                  ツールチップを表示
                </label>
              </div>
            </div>
          </div>

          {/* システム情報 */}
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex items-center mb-6">
              <Settings className="h-6 w-6 text-gray-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">システム情報</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600">バージョン</p>
                <p className="text-lg font-semibold">v1.0.0</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">最終更新</p>
                <p className="text-lg font-semibold">2024-09-27</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">データソース</p>
                <p className="text-lg font-semibold">J-Quants API</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
