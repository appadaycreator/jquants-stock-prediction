"use client";

import { useEffect, useMemo, useState } from "react";
import Navigation from "@/components/Navigation";
import { History, Search, Trash2, ExternalLink } from "lucide-react";

interface AnalysisRecord {
  symbol: string;
  name: string;
  analyzedAt: string;
  currentPrice: number;
  recommendation: "BUY" | "SELL" | "HOLD";
  confidence: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  targetPrice?: number;
  technicalIndicators?: Record<string, unknown>;
  reasons: string[];
}

export default function AnalysisHistoryPage() {
  const [records, setRecords] = useState<AnalysisRecord[]>([]);
  const [query, setQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<"ALL" | "LOW" | "MEDIUM" | "HIGH">("ALL");

  useEffect(() => {
    try {
      const raw = localStorage.getItem("analysis_history");
      const parsed: AnalysisRecord[] = raw ? JSON.parse(raw) : [];
      setRecords(parsed);
    } catch (e) {
      console.error("分析履歴の読み込みに失敗しました", e);
      setRecords([]);
    }
  }, []);

  const filtered = useMemo(() => {
    return records.filter((r) => {
      const matchesQuery =
        !query ||
        r.symbol.toLowerCase().includes(query.toLowerCase()) ||
        r.name.toLowerCase().includes(query.toLowerCase());
      const matchesRisk = riskFilter === "ALL" ? true : r.riskLevel === riskFilter;
      return matchesQuery && matchesRisk;
    });
  }, [records, query, riskFilter]);

  const clearHistory = () => {
    localStorage.removeItem("analysis_history");
    setRecords([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center mb-6">
          <History className="h-6 w-6 text-blue-600 mr-3" />
          <h1 className="text-2xl font-bold text-gray-900">分析履歴</h1>
        </div>

        <div className="bg-white rounded-lg shadow p-4 md:p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="銘柄コード・名称で検索"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="分析履歴を検索"
                data-help="銘柄コードや銘柄名で分析履歴を検索できます。過去の分析結果から特定の銘柄の履歴を素早く見つけられます。分析日時、推奨アクション、信頼度、リスクレベルなどの詳細情報を確認できます。投資判断の精度向上のため、過去の分析結果を振り返って学習効果を高めることができます。リアルタイム検索で、入力と同時に結果が絞り込まれます。投資戦略の検証と改善、投資パフォーマンスの分析、投資判断の精度向上に役立つ貴重な記録として活用できます。"
              />
            </div>

            <div className="flex items-center gap-2">
              <select
                className="border rounded-lg px-3 py-2 text-sm"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value as any)}
                aria-label="リスクレベルでフィルタ"
                data-help="分析履歴をリスクレベルでフィルタリングします。低リスク、中リスク、高リスクの分析結果を分類して表示できます。リスク許容度に応じて過去の分析結果を絞り込んで確認できます。投資戦略の検証やリスク管理の改善に役立ちます。リスクレベルは分析時の市場状況と銘柄の特性に基づいて自動的に設定されます。投資判断の精度向上のため、リスクレベル別の分析結果を比較して、投資戦略の最適化に活用できます。"
              >
                <option value="ALL">リスク: すべて</option>
                <option value="LOW">リスク: 低</option>
                <option value="MEDIUM">リスク: 中</option>
                <option value="HIGH">リスク: 高</option>
              </select>

              <button
                onClick={clearHistory}
                className="flex items-center gap-2 px-3 py-2 text-sm text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg"
                aria-label="分析履歴を全削除"
                data-help="すべての分析履歴を削除します。この操作は取り消せません。ローカルストレージから全ての履歴データが完全に削除されます。データをクリーンアップしたい場合や、プライバシーを重視する場合に使用します。システムのパフォーマンス向上やストレージ容量の節約にも役立ちます。削除前に重要な分析結果は別途バックアップすることを推奨します。投資戦略の検証と改善、投資パフォーマンスの分析、投資判断の精度向上に役立つ貴重な記録が失われるため、慎重に判断してください。"
              >
                <Trash2 className="h-4 w-4" />
                履歴を全消去
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow divide-y">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              まだ分析履歴がありません。「詳細分析を実行」するとここに表示されます。
            </div>
          ) : (
            filtered.map((r, idx) => (
              <div key={idx} className="p-4 md:p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900">{r.name}</span>
                      <span className="text-xs text-gray-500">{r.symbol}</span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      分析日時: {new Date(r.analyzedAt).toLocaleString("ja-JP")}
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-sm">
                      <span className="text-gray-500 mr-1">推奨:</span>
                      <span
                        className={
                          r.recommendation === "BUY"
                            ? "text-green-700"
                            : r.recommendation === "SELL"
                            ? "text-red-700"
                            : "text-yellow-700"
                        }
                      >
                        {r.recommendation}
                      </span>
                    </div>

                    <div className="text-sm">
                      <span className="text-gray-500 mr-1">信頼度:</span>
                      <span className="font-medium">{(r.confidence * 100).toFixed(1)}%</span>
                    </div>

                    <span
                      className={`text-xs px-2 py-1 rounded border ${
                        r.riskLevel === "LOW"
                          ? "bg-green-50 text-green-700 border-green-200"
                          : r.riskLevel === "MEDIUM"
                          ? "bg-yellow-50 text-yellow-700 border-yellow-200"
                          : "bg-red-50 text-red-700 border-red-200"
                      }`}
                    >
                      リスク: {r.riskLevel === "LOW" ? "低" : r.riskLevel === "MEDIUM" ? "中" : "高"}
                    </span>

                    <a
                      href={`/stock/${r.symbol}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                      aria-label={`${r.symbol}の詳細ページを開く`}
                      data-help="この銘柄の詳細ページを新しいタブで開きます。チャート分析、テクニカル指標、機械学習予測結果を確認できます。過去の分析結果と現在の状況を比較して、投資判断の精度向上に活用できます。プロの投資家レベルの分析ツールで、投資戦略の検証と改善に役立ちます。インタラクティブなチャートで、ズーム、パン、指標の追加・削除が可能です。投資判断の信頼性を高めるため、推奨アクションの根拠となる分析結果を詳細に確認できます。"
                    >
                      詳細ページ <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>

                {r.reasons?.length > 0 && (
                  <ul className="mt-3 list-disc list-inside text-sm text-gray-700 space-y-1">
                    {r.reasons.map((reason, i) => (
                      <li key={i}>{reason}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}


