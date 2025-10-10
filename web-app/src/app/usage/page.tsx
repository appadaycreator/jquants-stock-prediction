"use client";

import { useState } from "react";
import Navigation from "@/components/Navigation";
import { 
  BookOpen, 
  Play, 
  Settings, 
  BarChart3, 
  TrendingUp, 
  Target, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  Info,
  RefreshCw,
} from "lucide-react";

export default function UsagePage() {
  const [activeSection, setActiveSection] = useState("overview");

  const sections = [
    { id: "overview", label: "概要", icon: BookOpen },
    { id: "getting-started", label: "はじめに", icon: Play },
    { id: "ml-basics", label: "機械学習モデルの仕組み", icon: Target },
    { id: "metrics", label: "予測指標の読み方", icon: BarChart3 },
    { id: "jquants", label: "J‑Quants API 概要", icon: Database },
    { id: "faq-videos", label: "FAQ / 動画", icon: Info },
    { id: "dashboard", label: "ダッシュボード", icon: BarChart3 },
    { id: "analysis", label: "分析機能", icon: TrendingUp },
    { id: "settings", label: "設定", icon: Settings },
    { id: "troubleshooting", label: "トラブルシューティング", icon: AlertCircle },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ナビゲーション */}
      <Navigation />

      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">使い方ガイド</h1>
              <p className="text-gray-600">J-Quants株価予測システムの詳細な使用方法</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-600">システム稼働中</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* サイドバーナビゲーション */}
          <div className="lg:w-1/4">
            <nav className="bg-white rounded-lg shadow p-4 sticky top-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">目次</h3>
              <div className="space-y-2">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        activeSection === section.id
                          ? "bg-blue-50 text-blue-700 border-l-4 border-blue-500"
                          : "text-gray-600 hover:bg-gray-50"
                      }`}
                      aria-label={`${section.label}セクションを表示`}
                      data-help={`${section.label}の詳細な説明を表示します。システムの使い方、機能の詳細、操作手順などを学習できます。初心者から上級者まで、段階的にシステムの機能を理解できるよう設計されています。機械学習モデルの仕組み、予測指標の読み方、J-Quants APIの活用方法など、投資判断に必要な知識を体系的に学習できます。各セクションは独立しており、必要な部分だけを学習することも可能です。`}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="text-sm font-medium">{section.label}</span>
                    </button>
                  );
                })}
              </div>
            </nav>
          </div>

          {/* メインコンテンツ */}
          <div className="lg:w-3/4">
            <div className="bg-white rounded-lg shadow">
              {/* 概要セクション */}
              {activeSection === "overview" && (
                <div className="p-8">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">システム概要</h2>
                    <p className="text-gray-600 leading-relaxed">
                      J-Quants株価予測システムは、機械学習技術を活用して日本株の価格予測を行うWebアプリケーションです。
                      複数の予測モデルを比較し、最も精度の高い予測結果を提供します。
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-blue-50 rounded-lg p-6">
                      <div className="flex items-center mb-4">
                        <Database className="h-6 w-6 text-blue-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">データソース</h3>
                      </div>
                      <p className="text-gray-600">
                        J-Quants APIから取得したリアルタイムの株価データとテクニカル指標を使用
                      </p>
                    </div>

                    <div className="bg-green-50 rounded-lg p-6">
                      <div className="flex items-center mb-4">
                        <Target className="h-6 w-6 text-green-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">予測精度</h3>
                      </div>
                      <p className="text-gray-600">
                        複数の機械学習モデルを比較し、最適な予測モデルを自動選択
                      </p>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-6">
                      <div className="flex items-center mb-4">
                        <BarChart3 className="h-6 w-6 text-purple-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">可視化</h3>
                      </div>
                      <p className="text-gray-600">
                        インタラクティブなチャートとダッシュボードで予測結果を視覚化
                      </p>
                    </div>

                    <div className="bg-yellow-50 rounded-lg p-6">
                      <div className="flex items-center mb-4">
                        <Settings className="h-6 w-6 text-yellow-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">カスタマイズ</h3>
                      </div>
                      <p className="text-gray-600">
                        予測期間や使用する特徴量を自由に設定可能
                      </p>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">主な機能</h3>
                    <ul className="space-y-3">
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                        <span className="text-gray-700">リアルタイム株価データの取得と前処理</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                        <span className="text-gray-700">複数の機械学習モデル（線形回帰、ランダムフォレスト、XGBoost等）の比較</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                        <span className="text-gray-700">テクニカル指標（SMA、RSI、MACD等）の自動計算</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                        <span className="text-gray-700">予測精度の評価とモデル性能の可視化</span>
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5" />
                        <span className="text-gray-700">インタラクティブなダッシュボードとレポート機能</span>
                      </li>
                    </ul>
                  </div>
                </div>
              )}

              {/* はじめにセクション */}
              {activeSection === "getting-started" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">はじめに</h2>
                  
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">1. システムへのアクセス</h3>
                      <div className="bg-blue-50 rounded-lg p-6">
                        <div className="flex items-center mb-4">
                          <Play className="h-5 w-5 text-blue-600 mr-2" />
                          <span className="font-medium text-blue-900">ステップ 1</span>
                        </div>
                        <p className="text-gray-700 mb-4">
                          Webブラウザでシステムにアクセスします。メインダッシュボードが表示されます。
                        </p>
                        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                          <p className="text-sm text-gray-600">
                            💡 <strong>ヒント:</strong> 初回アクセス時は、データの読み込みに少し時間がかかる場合があります。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">2. データの確認</h3>
                      <div className="bg-green-50 rounded-lg p-6">
                        <div className="flex items-center mb-4">
                          <Database className="h-5 w-5 text-green-600 mr-2" />
                          <span className="font-medium text-green-900">ステップ 2</span>
                        </div>
                        <p className="text-gray-700 mb-4">
                          ダッシュボードの「概要」タブで、現在のデータ状況と予測精度を確認できます。
                        </p>
                        <ul className="space-y-2 text-sm text-gray-600">
                          <li>• 最優秀モデルとその性能指標</li>
                          <li>• 予測精度（R²スコア）</li>
                          <li>• 平均絶対誤差（MAE）</li>
                          <li>• データポイント数</li>
                        </ul>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">3. 分析の実行</h3>
                      <div className="bg-purple-50 rounded-lg p-6">
                        <div className="flex items-center mb-4">
                          <RefreshCw className="h-5 w-5 text-purple-600 mr-2" />
                          <span className="font-medium text-purple-900">ステップ 3</span>
                        </div>
                        <p className="text-gray-700 mb-4">
                          ヘッダーの「分析実行」ボタンをクリックして、新しい予測分析を実行します。
                        </p>
                        <div className="bg-white rounded-lg p-4 border-l-4 border-purple-500">
                          <p className="text-sm text-gray-600">
                            ⚠️ <strong>注意:</strong> 分析実行には数分かかる場合があります。実行中は他の操作を避けてください。
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ダッシュボードセクション */}
              {activeSection === "dashboard" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">ダッシュボードの使い方</h2>
                  
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">タブナビゲーション</h3>
                      <div className="bg-gray-50 rounded-lg p-6">
                        <p className="text-gray-700 mb-4">
                          ダッシュボードには4つの主要タブがあります：
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg">
                            <BarChart3 className="h-5 w-5 text-blue-600" />
                            <div>
                              <h4 className="font-medium text-gray-900">概要</h4>
                              <p className="text-sm text-gray-600">システムの全体像とサマリー</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg">
                            <TrendingUp className="h-5 w-5 text-green-600" />
                            <div>
                              <h4 className="font-medium text-gray-900">予測結果</h4>
                              <p className="text-sm text-gray-600">予測値と実際値の比較</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg">
                            <Target className="h-5 w-5 text-purple-600" />
                            <div>
                              <h4 className="font-medium text-gray-900">モデル比較</h4>
                              <p className="text-sm text-gray-600">各モデルの性能比較</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg">
                            <Database className="h-5 w-5 text-orange-600" />
                            <div>
                              <h4 className="font-medium text-gray-900">分析</h4>
                              <p className="text-sm text-gray-600">特徴量重要度と詳細分析</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">概要タブ</h3>
                      <div className="space-y-4">
                        <div className="bg-blue-50 rounded-lg p-6">
                          <h4 className="font-semibold text-gray-900 mb-2">サマリーカード</h4>
                          <p className="text-gray-700 mb-3">
                            システムの主要指標が4つのカードで表示されます：
                          </p>
                          <ul className="space-y-1 text-sm text-gray-600">
                            <li>• <strong>最優秀モデル:</strong> 最も精度の高い予測モデル</li>
                            <li>• <strong>予測精度 (R²):</strong> モデルの説明力</li>
                            <li>• <strong>MAE:</strong> 平均絶対誤差</li>
                            <li>• <strong>データ数:</strong> 分析対象のデータポイント数</li>
                          </ul>
                        </div>

                        <div className="bg-green-50 rounded-lg p-6">
                          <h4 className="font-semibold text-gray-900 mb-2">株価チャート</h4>
                          <p className="text-gray-700 mb-3">
                            株価の推移と移動平均線が表示されます：
                          </p>
                          <ul className="space-y-1 text-sm text-gray-600">
                            <li>• <strong>実際価格:</strong> 実際の株価（青線）</li>
                            <li>• <strong>SMA_5:</strong> 5日移動平均（赤線）</li>
                            <li>• <strong>SMA_10:</strong> 10日移動平均（緑線）</li>
                            <li>• <strong>SMA_25:</strong> 25日移動平均（オレンジ線）</li>
                            <li>• <strong>SMA_50:</strong> 50日移動平均（紫線）</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">ヘッダー機能</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white border rounded-lg p-4">
                          <div className="flex items-center mb-2">
                            <Play className="h-4 w-4 text-blue-600 mr-2" />
                            <span className="font-medium text-gray-900">分析実行</span>
                          </div>
                          <p className="text-sm text-gray-600">
                            新しい予測分析を実行します
                          </p>
                        </div>
                        <div className="bg-white border rounded-lg p-4">
                          <div className="flex items-center mb-2">
                            <Settings className="h-4 w-4 text-gray-600 mr-2" />
                            <span className="font-medium text-gray-900">設定</span>
                          </div>
                          <p className="text-sm text-gray-600">
                            予測パラメータを変更します
                          </p>
                        </div>
                        <div className="bg-white border rounded-lg p-4">
                          <div className="flex items-center mb-2">
                            <RefreshCw className="h-4 w-4 text-green-600 mr-2" />
                            <span className="font-medium text-gray-900">更新</span>
                          </div>
                          <p className="text-sm text-gray-600">
                            データを最新に更新します
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 機械学習モデルの仕組み */}
              {activeSection === "ml-basics" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">機械学習モデルの仕組み（概要）</h2>
                  <div className="space-y-6">
                    <div className="bg-white rounded-lg border p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">学習と推論の流れ</h3>
                      <ol className="list-decimal pl-5 space-y-2 text-gray-700">
                        <li>データ前処理（欠損補完・特徴量作成）</li>
                        <li>学習データと検証データに分割</li>
                        <li>モデル学習（例: 線形回帰、ランダムフォレスト、XGBoost）</li>
                        <li>検証指標で性能評価し、最適モデルを選択</li>
                        <li>新しいデータに対して予測を出力（推論）</li>
                      </ol>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-1">線形/正則化モデル</h4>
                        <p className="text-sm text-gray-700">解釈容易・高速。ただし非線形は苦手。</p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-1">ランダムフォレスト</h4>
                        <p className="text-sm text-gray-700">非線形に強くロバスト。外挿は苦手。</p>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-1">XGBoost</h4>
                        <p className="text-sm text-gray-700">高精度になりやすいが調整が複雑。</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 予測指標の読み方 */}
              {activeSection === "metrics" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">予測指標の読み方</h2>
                  <div className="bg-white rounded-lg border p-6">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="px-3 py-2 text-left">指標</th>
                          <th className="px-3 py-2 text-left">解釈</th>
                          <th className="px-3 py-2 text-left">目安</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white">
                        <tr>
                          <td className="px-3 py-2 font-medium">MAE</td>
                          <td className="px-3 py-2">平均絶対誤差。小さいほど良い（単位: 円）。</td>
                          <td className="px-3 py-2">他モデルと相対比較</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 font-medium">RMSE</td>
                          <td className="px-3 py-2">大きな誤差をより重く評価。小さいほど良い。</td>
                          <td className="px-3 py-2">他モデルと相対比較</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 font-medium">R²</td>
                          <td className="px-3 py-2">0〜1。1に近いほど説明力が高い。</td>
                          <td className="px-3 py-2">0.6〜0.9程度を目安（用途依存）</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 font-medium">MAPE</td>
                          <td className="px-3 py-2">平均絶対パーセント誤差。相対誤差（%）。</td>
                          <td className="px-3 py-2">他モデルと相対比較</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* J-Quants API 概要 */}
              {activeSection === "jquants" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">J‑Quants API 概要</h2>
                  <div className="space-y-6">
                    <div className="bg-white rounded-lg border p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">主要エンドポイント（概要）</h3>
                      <ul className="space-y-2 text-gray-700">
                        <li>• 時系列株価（OHLCV）</li>
                        <li>• 財務・決算情報</li>
                        <li>• 指数・先物などの関連データ</li>
                      </ul>
                      <p className="text-sm text-gray-600 mt-3">本アプリではトークン設定後にクライアントから安全に取得できるデータのみを使用します。</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-2">トークン設定</h4>
                      <p className="text-gray-700 text-sm">ヘッダーの「J‑Quants設定」からトークンを登録してください。</p>
                    </div>
                  </div>
                </div>
              )}

              {/* FAQ / 動画 */}
              {activeSection === "faq-videos" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">FAQ / 動画</h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg border p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">FAQ</h3>
                      <ul className="space-y-3 text-sm text-gray-700">
                        <li>
                          <p className="font-medium">Q. MAEとR²の違いは？</p>
                          <p className="text-gray-700">A. MAEは誤差の平均（絶対値）。R²は説明力（0〜1）。</p>
                        </li>
                        <li>
                          <p className="font-medium">Q. どのモデルを選べばいい？</p>
                          <p className="text-gray-700">A. まずは「すべてのモデル」で比較し、上位モデルを検討。</p>
                        </li>
                        <li>
                          <p className="font-medium">Q. 予測が外れる時の見方は？</p>
                          <p className="text-gray-700">A. 誤差分布や外れた期間の傾向を確認し特徴量や期間を調整。</p>
                        </li>
                      </ul>
                    </div>
                    <div className="bg-white rounded-lg border p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">学習動画（外部リンク）</h3>
                      <ul className="space-y-2 text-sm text-blue-700">
                        <li>
                          <a href="https://www.youtube.com" target="_blank" rel="noreferrer" className="hover:underline">J‑Quants入門（外部）</a>
                        </li>
                        <li>
                          <a href="https://www.youtube.com" target="_blank" rel="noreferrer" className="hover:underline">機械学習モデル比較（外部）</a>
                        </li>
                        <li>
                          <a href="https://www.youtube.com" target="_blank" rel="noreferrer" className="hover:underline">指標の読み方（外部）</a>
                        </li>
                      </ul>
                      <p className="text-xs text-gray-500 mt-3">注意: 外部サイトの内容は本ツールの保証対象外です。</p>
                    </div>
                  </div>
                </div>
              )}

              {/* 分析機能セクション */}
              {activeSection === "analysis" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">分析機能の詳細</h2>
                  
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">予測結果タブ</h3>
                      <div className="bg-blue-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">予測 vs 実際値チャート</h4>
                        <p className="text-gray-700 mb-4">
                          機械学習モデルによる予測値と実際の株価を比較表示します。
                        </p>
                        <ul className="space-y-2 text-sm text-gray-600">
                          <li>• <strong>青線（実際値）:</strong> 実際の株価データ</li>
                          <li>• <strong>赤線（予測値）:</strong> モデルによる予測値</li>
                          <li>• 2つの線が近いほど予測精度が高いことを示します</li>
                        </ul>
                      </div>

                      <div className="bg-green-50 rounded-lg p-6 mt-4">
                        <h4 className="font-semibold text-gray-900 mb-3">予測誤差分布</h4>
                        <p className="text-gray-700 mb-4">
                          各予測ポイントでの誤差の大きさを棒グラフで表示します。
                        </p>
                        <ul className="space-y-2 text-sm text-gray-600">
                          <li>• 誤差が小さいほど予測精度が高い</li>
                          <li>• 誤差の分布パターンからモデルの特性を把握可能</li>
                        </ul>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">モデル比較タブ</h3>
                      <div className="bg-purple-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">モデル性能比較表</h4>
                        <p className="text-gray-700 mb-4">
                          複数の機械学習モデルの性能を比較します。
                        </p>
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="px-3 py-2 text-left">指標</th>
                                <th className="px-3 py-2 text-left">説明</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white">
                              <tr>
                                <td className="px-3 py-2 font-medium">MAE</td>
                                <td className="px-3 py-2">平均絶対誤差（小さいほど良い）<br/>
                                  <span className="text-xs text-gray-500">予測値と実際の値の差の絶対値の平均。単位：円</span>
                                </td>
                              </tr>
                              <tr>
                                <td className="px-3 py-2 font-medium">RMSE</td>
                                <td className="px-3 py-2">平均平方根誤差（小さいほど良い）<br/>
                                  <span className="text-xs text-gray-500">大きな誤差を重く評価する指標。単位：円</span>
                                </td>
                              </tr>
                              <tr>
                                <td className="px-3 py-2 font-medium">R²</td>
                                <td className="px-3 py-2">決定係数（0-1の範囲）<br/>
                                  <span className="text-xs text-gray-500">モデルが説明できる分散の割合。0.99以上は過学習の可能性</span>
                                </td>
                              </tr>
                              <tr>
                                <td className="px-3 py-2 font-medium">MAPE</td>
                                <td className="px-3 py-2">平均絶対パーセント誤差（小さいほど良い）<br/>
                                  <span className="text-xs text-gray-500">予測誤差の相対的な大きさを示す。単位：%</span>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">分析タブ</h3>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-orange-50 rounded-lg p-6">
                          <h4 className="font-semibold text-gray-900 mb-3">特徴量重要度</h4>
                          <p className="text-gray-700 mb-4">
                            どの特徴量が予測に最も影響するかを示します。
                          </p>
                          <ul className="space-y-1 text-sm text-gray-600">
                            <li>• パーセンテージが高いほど重要</li>
                            <li>• 特徴量選択の参考になる</li>
                          </ul>
                        </div>

                        <div className="bg-pink-50 rounded-lg p-6">
                          <h4 className="font-semibold text-gray-900 mb-3">散布図</h4>
                          <p className="text-gray-700 mb-4">
                            実際値と予測値の相関関係を視覚化します。
                          </p>
                          <ul className="space-y-1 text-sm text-gray-600">
                            <li>• 点が対角線に近いほど精度が高い</li>
                            <li>• 外れ値の特定が可能</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 設定セクション */}
              {activeSection === "settings" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">設定の使い方</h2>
                  
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">設定画面へのアクセス</h3>
                      <div className="bg-blue-50 rounded-lg p-6">
                        <p className="text-gray-700 mb-4">
                          ヘッダーの「設定」ボタンをクリックして設定画面を開きます。
                        </p>
                        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                          <p className="text-sm text-gray-600">
                            💡 <strong>ヒント:</strong> 設定を変更した後は、分析を再実行して新しい設定を反映させてください。
                          </p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">予測期間の設定</h3>
                      <div className="bg-green-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">利用可能な期間</h4>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">7日</h5>
                            <p className="text-sm text-gray-600">短期予測に適している</p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">14日</h5>
                            <p className="text-sm text-gray-600">中期予測に適している</p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">30日</h5>
                            <p className="text-sm text-gray-600">長期予測（推奨）</p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">60日</h5>
                            <p className="text-sm text-gray-600">超長期予測</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">モデル選択</h3>
                      <div className="bg-purple-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">利用可能なモデル</h4>
                        <div className="space-y-4">
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">すべてのモデル</h5>
                            <p className="text-sm text-gray-600">
                              全モデルを比較して最適なものを自動選択（推奨）
                            </p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">線形回帰</h5>
                            <p className="text-sm text-gray-600">
                              シンプルで高速、線形関係に強い
                            </p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">ランダムフォレスト</h5>
                            <p className="text-sm text-gray-600">
                              非線形関係に強く、過学習に強い
                            </p>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900">XGBoost</h5>
                            <p className="text-sm text-gray-600">
                              高精度だが計算時間が長い
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">特徴量選択</h3>
                      <div className="bg-yellow-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">利用可能な特徴量</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">SMA_5</h5>
                              <p className="text-sm text-gray-600">5日移動平均</p>
                            </div>
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">SMA_10</h5>
                              <p className="text-sm text-gray-600">10日移動平均</p>
                            </div>
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">SMA_25</h5>
                              <p className="text-sm text-gray-600">25日移動平均</p>
                            </div>
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">SMA_50</h5>
                              <p className="text-sm text-gray-600">50日移動平均</p>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">RSI</h5>
                              <p className="text-sm text-gray-600">相対力指数</p>
                            </div>
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">MACD</h5>
                              <p className="text-sm text-gray-600">移動平均収束発散</p>
                            </div>
                            <div className="bg-white rounded-lg p-3">
                              <h5 className="font-medium text-gray-900">ボリンジャーバンド</h5>
                              <p className="text-sm text-gray-600">価格の変動性指標</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* トラブルシューティングセクション */}
              {activeSection === "troubleshooting" && (
                <div className="p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">トラブルシューティング</h2>
                  
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">よくある問題と解決方法</h3>
                      
                      <div className="space-y-6">
                        <div className="bg-red-50 rounded-lg p-6">
                          <div className="flex items-start">
                            <AlertCircle className="h-5 w-5 text-red-600 mr-3 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">データが読み込まれない</h4>
                              <p className="text-gray-700 mb-3">
                                ページが読み込まれない、または「データを読み込み中...」が表示され続ける場合
                              </p>
                              <ul className="space-y-1 text-sm text-gray-600">
                                <li>• ブラウザを更新してください（F5キーまたはCtrl+R）</li>
                                <li>• インターネット接続を確認してください</li>
                                <li>• しばらく待ってから再度アクセスしてください</li>
                              </ul>
                            </div>
                          </div>
                        </div>

                        <div className="bg-yellow-50 rounded-lg p-6">
                          <div className="flex items-start">
                            <AlertCircle className="h-5 w-5 text-yellow-600 mr-3 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">分析実行が失敗する</h4>
                              <p className="text-gray-700 mb-3">
                                「分析実行」ボタンを押しても分析が開始されない、またはエラーが発生する場合
                              </p>
                              <ul className="space-y-1 text-sm text-gray-600">
                                <li>• 設定で予測期間を短くしてみてください</li>
                                <li>• 使用する特徴量の数を減らしてみてください</li>
                                <li>• ページを更新してから再度試してください</li>
                              </ul>
                            </div>
                          </div>
                        </div>

                        <div className="bg-blue-50 rounded-lg p-6">
                          <div className="flex items-start">
                            <Info className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">チャートが表示されない</h4>
                              <p className="text-gray-700 mb-3">
                                チャートエリアが空白になっている場合
                              </p>
                              <ul className="space-y-1 text-sm text-gray-600">
                                <li>• データが十分に取得されていない可能性があります</li>
                                <li>• 「更新」ボタンをクリックしてデータを再読み込みしてください</li>
                                <li>• 別のブラウザで試してみてください</li>
                              </ul>
                            </div>
                          </div>
                        </div>

                        <div className="bg-green-50 rounded-lg p-6">
                          <div className="flex items-start">
                            <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5" />
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">予測精度が低い</h4>
                              <p className="text-gray-700 mb-3">
                                予測結果の精度が期待より低い場合
                              </p>
                              <ul className="space-y-1 text-sm text-gray-600">
                                <li>• より多くの特徴量を有効にしてみてください</li>
                                <li>• 予測期間を短くしてみてください</li>
                                <li>• 異なるモデルを試してみてください</li>
                                <li>• より多くのデータが蓄積されるまで待ってください</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">パフォーマンスの最適化</h3>
                      <div className="bg-gray-50 rounded-lg p-6">
                        <h4 className="font-semibold text-gray-900 mb-3">システムを快適に使用するためのヒント</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900 mb-2">ブラウザの推奨設定</h5>
                            <ul className="space-y-1 text-sm text-gray-600">
                              <li>• Chrome、Firefox、Safariの最新版を使用</li>
                              <li>• JavaScriptを有効にする</li>
                              <li>• ポップアップブロックを無効にする</li>
                            </ul>
                          </div>
                          <div className="bg-white rounded-lg p-4">
                            <h5 className="font-medium text-gray-900 mb-2">ネットワーク環境</h5>
                            <ul className="space-y-1 text-sm text-gray-600">
                              <li>• 安定したインターネット接続</li>
                              <li>• 十分な帯域幅（推奨: 10Mbps以上）</li>
                              <li>• ファイアウォールの設定確認</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">サポート情報</h3>
                      <div className="bg-blue-50 rounded-lg p-6">
                        <p className="text-gray-700 mb-4">
                          上記の解決方法で問題が解決しない場合は、以下の情報を確認してください：
                        </p>
                        <ul className="space-y-2 text-sm text-gray-600">
                          <li>• 使用しているブラウザとバージョン</li>
                          <li>• エラーメッセージの詳細</li>
                          <li>• 問題が発生した時刻</li>
                          <li>• 実行していた操作の手順</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
