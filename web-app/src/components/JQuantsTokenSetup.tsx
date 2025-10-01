"use client";

import { useState, useEffect } from "react";
import { CheckCircle, AlertTriangle, Key, Database, RefreshCw, Trash2 } from "lucide-react";
import JQuantsAdapter, { JQuantsConfig } from "@/lib/jquants-adapter";
import ReliableApiSystem from "@/lib/reliable-api-system";

interface JQuantsTokenSetupProps {
  onTokenConfigured: (adapter: JQuantsAdapter) => void;
  onTokenRemoved: () => void;
  onReliableSystemConfigured?: (system: ReliableApiSystem) => void;
}

export default function JQuantsTokenSetup({ onTokenConfigured, onTokenRemoved, onReliableSystemConfigured }: JQuantsTokenSetupProps) {
  const [token, setToken] = useState("");
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [adapter, setAdapter] = useState<JQuantsAdapter | null>(null);
  const [cacheStats, setCacheStats] = useState<{ totalRecords: number; symbols: string[]; lastUpdated: string } | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // 保存されたトークンを読み込み
  useEffect(() => {
    const savedToken = localStorage.getItem("jquants_token");
    if (savedToken) {
      setToken(savedToken);
      initializeAdapter(savedToken);
    }
  }, []);

  const initializeAdapter = async (tokenValue: string) => {
    try {
      const config: JQuantsConfig = {
        token: tokenValue,
        baseUrl: "https://api.jquants.com/v1",
        timeout: 30000,
      };

      const newAdapter = new JQuantsAdapter(config);
      setAdapter(newAdapter);
      
      // キャッシュ統計を取得
      await loadCacheStats(newAdapter);
    } catch (error) {
      console.error("アダプタ初期化エラー:", error);
    }
  };

  const handleTokenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      await initializeAdapter(token);
      const result = await adapter!.testConnection();
      setTestResult(result);

      if (result.success) {
        localStorage.setItem("jquants_token", token);
        onTokenConfigured(adapter!);
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: `接続テストエラー: ${error instanceof Error ? error.message : "不明なエラー"}`,
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleTokenRemove = async () => {
    if (adapter) {
      await adapter.clearCache();
    }
    
    localStorage.removeItem("jquants_token");
    setToken("");
    setAdapter(null);
    setTestResult(null);
    setCacheStats(null);
    onTokenRemoved();
  };

  const handleRefreshData = async () => {
    if (!adapter) return;

    setIsLoadingStats(true);
    try {
      await loadCacheStats(adapter);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const loadCacheStats = async (adapterInstance: JQuantsAdapter) => {
    try {
      const stats = await adapterInstance.getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error("キャッシュ統計取得エラー:", error);
    }
  };

  const formatLastUpdated = (dateString: string) => {
    if (!dateString) return "未設定";
    return new Date(dateString).toLocaleString("ja-JP");
  };

  return (
    <div className="bg-white rounded-lg shadow border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Key className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">J-Quants API設定</h3>
            <p className="text-sm text-gray-600">トークンを設定してリアルタイムデータを取得</p>
          </div>
        </div>
        {adapter && (
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-green-600 font-medium">接続済み</span>
          </div>
        )}
      </div>

      {!adapter ? (
        <form onSubmit={handleTokenSubmit} className="space-y-4">
          <div>
            <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-2">
              J-Quants APIトークン
            </label>
            <input
              id="token"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="J-Quants APIトークンを入力してください"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              J-Quantsの無料アカウントでトークンを取得できます
            </p>
          </div>

          <button
            type="submit"
            disabled={!token.trim() || isTesting}
            className={`w-full flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors ${
              !token.trim() || isTesting
                ? "bg-gray-400 cursor-not-allowed text-white"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            {isTesting ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                接続テスト中...
              </>
            ) : (
              <>
                <Key className="h-4 w-4 mr-2" />
                接続テスト & 設定
              </>
            )}
          </button>

          {testResult && (
            <div className={`p-3 rounded-lg ${
              testResult.success 
                ? "bg-green-50 border border-green-200" 
                : "bg-red-50 border border-red-200"
            }`}>
              <div className="flex items-center">
                {testResult.success ? (
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                )}
                <span className={`text-sm font-medium ${
                  testResult.success ? "text-green-800" : "text-red-800"
                }`}>
                  {testResult.message}
                </span>
              </div>
            </div>
          )}
        </form>
      ) : (
        <div className="space-y-4">
          {/* 接続状態 */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                <div>
                  <p className="text-sm font-medium text-green-800">J-Quants API接続済み</p>
                  <p className="text-xs text-green-600">リアルタイムデータ取得可能</p>
                </div>
              </div>
              <button
                onClick={handleTokenRemove}
                className="flex items-center px-3 py-1 text-sm text-red-600 hover:bg-red-100 rounded-lg transition-colors"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                削除
              </button>
            </div>
          </div>

          {/* キャッシュ統計 */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <Database className="h-5 w-5 text-blue-600 mr-2" />
                <h4 className="text-sm font-medium text-gray-900">キャッシュ統計</h4>
              </div>
              <button
                onClick={handleRefreshData}
                disabled={isLoadingStats}
                className="p-1 text-gray-500 hover:text-gray-700 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isLoadingStats ? "animate-spin" : ""}`} />
              </button>
            </div>

            {cacheStats ? (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">総レコード数</p>
                  <p className="font-semibold text-gray-900">{cacheStats.totalRecords.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">銘柄数</p>
                  <p className="font-semibold text-gray-900">{cacheStats.symbols.length}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-gray-600">最終更新</p>
                  <p className="font-semibold text-gray-900">{formatLastUpdated(cacheStats.lastUpdated)}</p>
                </div>
                {cacheStats.symbols.length > 0 && (
                  <div className="col-span-2">
                    <p className="text-gray-600 mb-1">キャッシュ済み銘柄</p>
                    <div className="flex flex-wrap gap-1">
                      {cacheStats.symbols.slice(0, 10).map(symbol => (
                        <span key={symbol} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {symbol}
                        </span>
                      ))}
                      {cacheStats.symbols.length > 10 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          +{cacheStats.symbols.length - 10}件
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-sm text-gray-500">キャッシュデータがありません</p>
              </div>
            )}
          </div>

          {/* 1クリック更新ボタン */}
          <button
            onClick={() => {
              // 1クリック更新の実装
              console.log("1クリック更新実行");
            }}
            className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            1クリック更新で最新化
          </button>
        </div>
      )}
    </div>
  );
}
