"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useFiveMinRoutine } from "@/hooks/useFiveMinRoutine";
import { useSignalWithFallback } from "@/hooks/useSignalWithFallback";
import EnhancedInstructionCard from "@/components/EnhancedInstructionCard";
import SignalHistoryDisplay from "@/components/SignalHistoryDisplay";
import ErrorGuidance from "@/components/ErrorGuidance";

export default function TodayPage() {
  const routine = useFiveMinRoutine();
  const signalData = useSignalWithFallback(routine.topCandidates.map(c => c.symbol));

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

  if (routine.isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="animate-pulse space-y-4">
            <div className="h-16 bg-gray-200 rounded" />
            <div className="h-32 bg-gray-200 rounded" />
            <div className="h-56 bg-gray-200 rounded" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
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
            <div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                routine.freshness === "Fresh" ? "bg-green-100 text-green-800" : routine.freshness === "Stale" ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-700"
              }`}>
                {routine.freshness}
              </span>
            </div>
            <button
              className="ml-3 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700"
              onClick={routine.actions.refresh}
            >
              更新
            </button>
          </div>
        </section>

        {/* ② 候補：上位5銘柄（拡張版） */}
        <section className="mb-6" aria-label="上位候補">
          <h2 className="text-lg font-bold text-gray-900 mb-3">今日の投資指示</h2>
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

        {/* ⑤ シグナル履歴 */}
        <section className="mb-8" aria-label="シグナル履歴">
          <h2 className="text-lg font-bold text-gray-900 mb-3">シグナル履歴</h2>
          <SignalHistoryDisplay symbol={routine.topCandidates[0]?.symbol} days={30} />
        </section>

        <div className="text-center text-xs text-gray-500 pb-6">上下スクロールのみで完結・最小3クリック設計</div>
      </div>
    </div>
  );
}
