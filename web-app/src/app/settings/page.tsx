'use client'

import { useState } from 'react'
import { Settings, Save, RefreshCw, Database, Cpu, BarChart } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    model: {
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
    ui: {
      theme: 'light',
      refresh_rate: 30,
      show_tooltips: true
    }
  })

  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    // 設定保存のシミュレーション
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
    alert('設定が保存されました')
  }

  const handleReset = () => {
    if (confirm('設定をリセットしますか？')) {
      setSettings({
        model: {
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
        ui: {
          theme: 'light',
          refresh_rate: 30,
          show_tooltips: true
        }
      })
    }
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

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
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
