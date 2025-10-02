"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useFiveMinRoutine } from "@/hooks/useFiveMinRoutine";
import { useSignalWithFallback } from "@/hooks/useSignalWithFallback";
import { useEnhancedTodayData, useTodayDataFallback } from "@/hooks/useEnhancedTodayData";
import EnhancedInstructionCard from "@/components/EnhancedInstructionCard";
import EnhancedLoadingSpinner from "@/components/EnhancedLoadingSpinner";
// import SignalHistoryDisplay from "@/components/SignalHistoryDisplay"; // 一時的に無効化
import ErrorGuidance from "@/components/ErrorGuidance";
import { Clock, Target, TrendingUp, RefreshCw, CheckCircle, AlertTriangle } from "lucide-react";

export default function TodayPage() {
  const routine = useFiveMinRoutine();
  const [startTime] = useState(Date.now());
  const [completedTasks, setCompletedTasks] = useState<string[]>([]);
  
  // 強化された今日の指示データ取得
  const todayData = useEnhancedTodayData();
  const { fallbackData, fallbackTimestamp, saveFallbackData } = useTodayDataFallback();
  
  // シンボル配列をメモ化して無限ループを防ぐ
  const symbols = useMemo(() => 
    routine.topCandidates.map(c => c.symbol), 
    [routine.topCandidates]
  );
  const signalData = useSignalWithFallback(symbols);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const from = params.get("from");
    if (from === "notification") {
      setTimeout(() => {
        const el = document.querySelector("[data-highlight=\"true\"]");
        if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 800);
    }
  }, []);

  // データの保存（成功時）
  useEffect(() => {
    if (todayData.data) {
      saveFallbackData(todayData.data);
    }
  }, [todayData.data, saveFallbackData]);

  // ローディング表示
  if (routine.isLoading || todayData.loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <EnhancedLoadingSpinner
            state={{
              isLoading: true,
              progress: 50,
              message: '今日の指示を取得中...',
              canRetry: false,
              retryCount: 0,
              maxRetries: 3,
            }}
            variant="default"
            showProgress={true}
          />
        </div>
      </div>
    );
  }

  // エラー表示（フォールバックデータがある場合）
  if (todayData.error && fallbackData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800">
                  最新データの取得に失敗しました
                </h3>
                <p className="text-sm text-yellow-700 mt-1">
                  前回の結果を表示しています（{fallbackTimestamp ? new Date(fallbackTimestamp).toLocaleString() : '不明'}）
                </p>
              </div>
            </div>
            <div className="mt-3">
              <button
                onClick={todayData.retry}
                className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4 inline mr-2" />
                再試行
              </button>
            </div>
          </div>
          {/* フォールバックデータの表示 */}
          <div className="space-y-6">
            {/* フォールバックデータの内容を表示 */}
          </div>
        </div>
      </div>
    );
  }

  // エラー表示（フォールバックデータがない場合）
  if (todayData.error && !fallbackData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-red-800 mb-2">
              データの取得に失敗しました
            </h3>
            <p className="text-red-700 mb-4">
              {todayData.error}
            </p>
            <button
              onClick={todayData.retry}
              className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 inline mr-2" />
              再試行
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 経過時間の計算
  const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
  const remainingTime = Math.max(0, 300 - elapsedTime); // 5分 = 300秒

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-md mx-auto px-4 py-4 md:max-w-3xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Target className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">今日のタスク</h1>
                <p className="text-sm text-gray-600">5分で完了する投資判断</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {Math.floor(remainingTime / 60)}:{(remainingTime % 60).toString().padStart(2, '0')}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full max-w-md mx-auto px-4 py-4 md:max-w-3xl">
        {(routine.error || signalData.error) && (
          <div className="mb-4">
            <ErrorGuidance
              error={routine.error || signalData.error || ''}
              errorCode={signalData.error?.includes('分析を実行してから') ? 'ANALYSIS_REQUIRED' : 
                         signalData.error?.includes('ネットワーク') ? 'NETWORK_ERROR' : 'API_ERROR'}
              onRetry={() => {
                if (routine.actions?.refresh) routine.actions.refresh();
                if (signalData.refresh) signalData.refresh();
              }}
              onClearError={signalData.clearError}
              isUsingFallback={signalData.isUsingFallback}
              analysisRequired={signalData.error?.includes('分析を実行してから') || routine.error?.includes('分析を実行してから')}
            />
          </div>
        )}

        {/* ① チェック：データ更新状況 */}
        <section className="mb-6" aria-label="データ更新状況">
          <div className="bg-white rounded-xl border p-4 flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">最終更新</p>
              <p className="text-base font-semibold text-gray-900">{routine.lastUpdated ? new Date(routine.lastUpdated).toLocaleString("ja-JP") : "—"}</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                routine.freshness === "Fresh" ? "bg-green-100 text-green-800" : routine.freshness === "Stale" ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-700"
              }`}>
                {routine.freshness === "Fresh" ? <CheckCircle className="h-4 w-4 mr-1" /> : 
                 routine.freshness === "Stale" ? <AlertTriangle className="h-4 w-4 mr-1" /> : null}
                {routine.freshness}
              </span>
              <button
                className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 flex items-center space-x-1"
                onClick={routine.actions.refresh}
              >
                <RefreshCw className="h-4 w-4" />
                <span>更新</span>
              </button>
            </div>
          </div>
        </section>

        {/* ② 候補：上位5銘柄（拡張版） */}
        <section className="mb-6" aria-label="上位候補">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-gray-900">今日の投資指示</h2>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-sm text-gray-600">{routine.topCandidates.length}件の候補</span>
            </div>
          </div>
          {routine.topCandidates.length === 0 ? (
            <div className="bg-white rounded-xl border p-4 text-gray-600 text-sm">該当候補がありません</div>
          ) : (
            <div className="space-y-4">
              {routine.topCandidates.map((c, idx) => (
                <EnhancedInstructionCard
                  key={c.symbol}
                  symbol={c.symbol}
                  name={c.name}
                  recommendation={c.recommendation}
                  confidence={c.confidence ?? 0.5}
                  price={1000}
                  reason={c.routine_reasons.join(", ") || "スコア上位"}
                  expectedHoldingPeriod={30}
                  riskLevel="MEDIUM"
                  category="テクニカルブレイクアウト"
                  historicalAccuracy={0.0}
                  evidence={{
                    technical: [
                      { name: "RSI", value: 65, signal: "買い" },
                      { name: "MACD", value: 1.2, signal: "買い" },
                      { name: "移動平均", value: 2480, signal: "買い" },
                    ],
                    fundamental: [
                      { name: "PER", value: 15.2, signal: "買い" },
                      { name: "PBR", value: 1.1, signal: "買い" },
                    ],
                    sentiment: [
                      { name: "ニュース", value: 0.7, signal: "買い" },
                      { name: "SNS", value: 0.6, signal: "買い" },
                    ],
                  }}
                  onActionClick={(symbol, action, quantity) => {
                    console.log(`${symbol}: ${action} ${quantity * 100}%`);
                    // 実際の取引実行ロジックをここに実装
                  }}
                />
              ))}
            </div>
          )}
        </section>

        {/* ③ アクション：保有中銘柄の提案 */}
        <section className="mb-6" aria-label="保有銘柄アクション">
          <h2 className="text-lg font-bold text-gray-900 mb-3">保有中の提案</h2>
          {routine.holdingProposals.length === 0 ? (
            <div className="bg-white rounded-xl border p-4 text-sm text-gray-600">保有銘柄が見つかりません</div>
          ) : (
            <div className="space-y-3">
              {routine.holdingProposals.map((h) => (
                <div key={h.symbol} className="bg-white rounded-xl border p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-gray-900">{h.symbol}</div>
                      <div className="text-xs text-gray-600">{h.reason}</div>
                    </div>
                    <div className="text-right">
                      <span className={`inline-block text-xs px-2 py-1 rounded mr-2 ${
                        h.proposal === "継続" ? "bg-blue-100 text-blue-800" : h.proposal === "利確" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}>{h.proposal}</span>
                      {h.qtyOptions.map((q) => (
                        <button key={q} className="ml-1 bg-gray-100 px-2 py-1 rounded text-xs hover:bg-gray-200">
                          {Math.round(q * 100)}%
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ④ メモ：1行メモ */}
        <section className="mb-8" aria-label="本日のメモ">
          <h2 className="text-lg font-bold text-gray-900 mb-3">今日のメモ</h2>
          <div className="bg-white rounded-xl border p-3 flex items-center gap-2">
            <input
              type="text"
              value={routine.memo}
              onChange={(e) => routine.actions.setMemo(e.target.value)}
              placeholder="本日の決定を1行で記録（ローカル保存）"
              className="flex-1 outline-none text-sm"
            />
            <button
              className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700"
              onClick={() => routine.actions.saveMemo(routine.memo)}
            >
              保存
            </button>
          </div>
        </section>

        {/* ⑤ シグナル履歴 - 一時的に無効化 */}
        <section className="mb-8" aria-label="シグナル履歴">
          <h2 className="text-lg font-bold text-gray-900 mb-3">シグナル履歴</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600">シグナル履歴機能は一時的に無効化されています。</p>
          </div>
        </section>

        {/* 進捗表示 */}
        <div className="bg-white rounded-xl border p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">進捗状況</span>
            <span className="text-sm text-gray-600">{completedTasks.length}/5 完了</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(completedTasks.length / 5) * 100}%` }}
            />
          </div>
        </div>

        <div className="text-center text-xs text-gray-500 pb-6">
          <div className="flex items-center justify-center space-x-2">
            <Clock className="h-4 w-4" />
            <span>5分で完了・上下スクロールのみで完結</span>
          </div>
        </div>
      </div>
    </div>
  );
}
