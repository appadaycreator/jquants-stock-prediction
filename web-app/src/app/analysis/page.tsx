"use client";

export const dynamic = "force-dynamic";

import { Suspense, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import SymbolAnalysisResults from "@/components/SymbolAnalysisResults";

function AnalysisInner() {
  const sp = useSearchParams();
  const symbolParam = sp.getAll("symbol");

  const selectedSymbols = useMemo(() => {
    if (!symbolParam || symbolParam.length === 0) return [] as string[];
    return symbolParam.filter(Boolean) as string[];
  }, [symbolParam]);

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold text-gray-900">詳細分析</h1>
        <a href="/analysis-history" className="text-sm text-blue-700 underline">分析履歴</a>
      </div>

      {selectedSymbols.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded">
          銘柄コードが指定されていません。銘柄一覧やダッシュボードから銘柄を選択して詳細分析に遷移してください。
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">銘柄別分析結果</h2>
        <SymbolAnalysisResults selectedSymbols={selectedSymbols} />
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={<div className="p-4">読み込み中...</div>}>
      <AnalysisInner />
    </Suspense>
  );
}


