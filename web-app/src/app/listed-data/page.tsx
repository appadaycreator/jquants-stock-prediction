"use client";

export const dynamic = "force-dynamic";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import EnhancedJQuantsAdapter from "@/lib/enhanced-jquants-adapter";
import StockDetailModal from "@/components/StockDetailModal";
import StockSearchInput from "@/components/StockSearchInput";
import { formatStockCode, normalizeStockCode } from "@/lib/stock-code-utils";
import { openMinkabuLink } from "@/lib/minkabu-utils";

interface ListedStock {
  code: string;
  name: string;
  sector: string;
  market: string;
  updated_at: string;
  file_path: string;
  currentPrice?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
}

interface ListedData {
  metadata: {
    generated_at: string;
    version: string;
    total_stocks: number;
    last_updated: string;
    data_type: string;
  };
  stocks: ListedStock[];
}

type SortField = "code" | "name" | "sector" | "market" | "currentPrice" | "change" | "changePercent" | "volume";
type SortDirection = "asc" | "desc";

const ListedDataPage: React.FC = () => {
  const [data, setData] = useState<ListedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSector, setSelectedSector] = useState("");
  const [selectedMarket, setSelectedMarket] = useState("");
  const [sortField, setSortField] = useState<SortField>("code");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(200);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [priceRange, setPriceRange] = useState({ min: "", max: "" });
  const [volumeRange, setVolumeRange] = useState({ min: "", max: "" });
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [jquantsAdapter, setJquantsAdapter] = useState<EnhancedJQuantsAdapter | null>(null);
  // クイックフィルタ
  const [onlyUp, setOnlyUp] = useState(false);
  const [onlyDown, setOnlyDown] = useState(false);
  const [highVolume, setHighVolume] = useState(false);
  // URLクエリ同期
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const fetchListedData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // まずキャッシュされたデータを取得
      const { resolveStaticPath } = await import("@/lib/path");
      const response = await fetch(resolveStaticPath("/data/listed_index.json"));
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const listedData = await response.json();
      // 受領データのコードを正規化（5桁0埋め→4桁、新形式は大文字）
      if (listedData?.stocks?.length) {
        listedData.stocks = listedData.stocks.map((s: ListedStock) => ({
          ...s,
          code: normalizeStockCode(s.code),
        }));
      }
      
      // J-Quants APIから最新の銘柄一覧を取得
      try {
        // アダプタ未初期化ならスキップ（後続のuseEffectで初期化）
        if (!jquantsAdapter) throw new Error("adapter_not_ready");
        const symbols = await jquantsAdapter.getAllSymbols();
        if (symbols.length > 0) {
          // APIから取得したデータで更新
          const updatedStocks = listedData.stocks.map((stock: ListedStock) => {
            const apiStock = symbols.find(s => s.code === stock.code);
            return {
              ...stock,
              name: apiStock?.name || stock.name,
              sector: apiStock?.sector || stock.sector,
            };
          });
          
          setData({
            ...listedData,
            stocks: updatedStocks,
            metadata: {
              ...listedData.metadata,
              last_updated: new Date().toISOString(),
            },
          });
        } else {
          setData(listedData);
        }
      } catch (apiError) {
        console.warn("J-Quants API取得に失敗、キャッシュデータを使用:", apiError);
        setData(listedData);
      }
    } catch (err) {
      console.error("Error fetching listed data:", err);
      setError("データの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  }, [jquantsAdapter]);

  useEffect(() => {
    // クライアント側でのみIndexedDBを使用するため遅延初期化
    setJquantsAdapter(new EnhancedJQuantsAdapter());
  }, []);

  useEffect(() => {
    fetchListedData();
  }, [fetchListedData]);

  // 初期化時にURLクエリから状態復元
  useEffect(() => {
    if (!searchParams) return;
    const q = searchParams.get("q") || "";
    const sector = searchParams.get("sector") || "";
    const market = searchParams.get("market") || "";
    const sortBy = (searchParams.get("sortBy") as SortField) || "code";
    const sortOrder = (searchParams.get("sortOrder") as SortDirection) || "asc";
    const page = parseInt(searchParams.get("page") || "1", 10);
    const up = searchParams.get("up") === "1";
    const down = searchParams.get("down") === "1";
    const hv = searchParams.get("hv") === "1";
    setSearchTerm(q);
    setSelectedSector(sector);
    setSelectedMarket(market);
    setSortField(sortBy);
    setSortDirection(sortOrder);
    setCurrentPage(isNaN(page) ? 1 : page);
    setOnlyUp(up);
    setOnlyDown(down);
    setHighVolume(hv);
    const pmin = searchParams.get("pmin");
    const pmax = searchParams.get("pmax");
    const vmin = searchParams.get("vmin");
    const vmax = searchParams.get("vmax");
    setPriceRange({ min: pmin || "", max: pmax || "" });
    setVolumeRange({ min: vmin || "", max: vmax || "" });
  }, [searchParams]);

  // 状態をURLクエリへ反映
  useEffect(() => {
    if (!router || !pathname) return;
    const params = new URLSearchParams();
    if (searchTerm) params.set("q", searchTerm);
    if (selectedSector) params.set("sector", selectedSector);
    if (selectedMarket) params.set("market", selectedMarket);
    if (sortField) params.set("sortBy", sortField);
    if (sortDirection) params.set("sortOrder", sortDirection);
    if (currentPage > 1) params.set("page", String(currentPage));
    if (priceRange.min) params.set("pmin", priceRange.min);
    if (priceRange.max) params.set("pmax", priceRange.max);
    if (volumeRange.min) params.set("vmin", volumeRange.min);
    if (volumeRange.max) params.set("vmax", volumeRange.max);
    if (onlyUp) params.set("up", "1");
    if (onlyDown) params.set("down", "1");
    if (highVolume) params.set("hv", "1");
    const q = params.toString();
    router.replace(q ? `${pathname}?${q}` : pathname);
  }, [searchTerm, selectedSector, selectedMarket, sortField, sortDirection, currentPage, priceRange, volumeRange, onlyUp, onlyDown, highVolume, router, pathname]);

  const getUniqueSectors = useMemo(() => {
    if (!data) return [];
    return Array.from(new Set(data.stocks.map(stock => stock.sector))).sort();
  }, [data]);

  const getUniqueMarkets = useMemo(() => {
    if (!data) return [];
    return Array.from(new Set(data.stocks.map(stock => stock.market))).sort();
  }, [data]);

  const handleSort = useCallback((field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
    setCurrentPage(1); // ソート時にページをリセット
  }, [sortField, sortDirection]);

  const filteredAndSortedStocks = useMemo(() => {
    if (!data) return [];

    const searchTermLower = searchTerm.toLowerCase();
    const minPrice = priceRange.min ? parseFloat(priceRange.min) : null;
    const maxPrice = priceRange.max ? parseFloat(priceRange.max) : null;
    const minVolume = volumeRange.min ? parseFloat(volumeRange.min) : null;
    const maxVolume = volumeRange.max ? parseFloat(volumeRange.max) : null;

    // 全角・半角を統一した検索用の関数
    const normalizeText = (text: string): string => {
      return text
        .toLowerCase()
        .trim()
        // 全角数字を半角に変換
        .replace(/[０-９]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
        // 全角英字を半角に変換
        .replace(/[Ａ-Ｚａ-ｚ]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
        // 全角記号を半角に変換
        .replace(/[（）]/g, (match) => match === "（" ? "(" : ")")
        .replace(/[　]/g, " "); // 全角スペースを半角に変換
    };

    const normalizedSearchTerm = normalizeText(searchTerm);

    let filtered = data.stocks.filter(stock => {
      const normalizedName = normalizeText(stock.name);
      const normalizedCode = normalizeText(formatStockCode(stock.code));
      const matchesSearch = normalizedName.includes(normalizedSearchTerm) || 
                           normalizedCode.includes(normalizedSearchTerm);
      const matchesSector = !selectedSector || stock.sector === selectedSector;
      const matchesMarket = !selectedMarket || stock.market === selectedMarket;
      
      // 価格フィルター
      const matchesPrice = !minPrice || !maxPrice || 
        (stock.currentPrice && 
         stock.currentPrice >= minPrice && 
         stock.currentPrice <= maxPrice);
      
      // 出来高フィルター
      const matchesVolume = !minVolume || !maxVolume || 
        (stock.volume && 
         stock.volume >= minVolume && 
         stock.volume <= maxVolume);

      // クイックフィルタ（上昇/下落）
      const matchesUpDown = (
        (!onlyUp && !onlyDown) ||
        (onlyUp && (stock.change ?? 0) >= 0) ||
        (onlyDown && (stock.change ?? 0) < 0)
      );

      return matchesSearch && matchesSector && matchesMarket && matchesPrice && matchesVolume && matchesUpDown;
    });

    // 高出来高（上位25%目安）
    if (highVolume) {
      const volumes = filtered.map(s => s.volume || 0).sort((a, b) => a - b);
      const thresholdIndex = Math.floor(volumes.length * 0.75);
      const threshold = volumes[thresholdIndex] || 0;
      filtered = filtered.filter(s => (s.volume || 0) >= threshold);
    }

    // ソート
    filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      if (sortField === "currentPrice" || sortField === "change" || sortField === "changePercent" || sortField === "volume") {
        aValue = aValue || 0;
        bValue = bValue || 0;
      }

      if (typeof aValue === "string") {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
      if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [data, searchTerm, selectedSector, selectedMarket, sortField, sortDirection, priceRange, volumeRange, onlyUp, onlyDown, highVolume]);

  // フィルター変更時にページをリセット
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedSector, selectedMarket, priceRange, volumeRange]);

  const paginatedStocks = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredAndSortedStocks.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedStocks, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredAndSortedStocks.length / itemsPerPage);

  // ページネーション用のヘルパー関数
  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  }, [totalPages]);

  const goToFirstPage = useCallback(() => goToPage(1), [goToPage]);
  const goToLastPage = useCallback(() => goToPage(totalPages), [goToPage, totalPages]);
  const goToPreviousPage = useCallback(() => goToPage(currentPage - 1), [goToPage, currentPage]);
  const goToNextPage = useCallback(() => goToPage(currentPage + 1), [goToPage, currentPage]);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-lg">上場銘柄データを読み込み中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">エラーが発生しました</h2>
          <p>{error}</p>
          <button 
            onClick={fetchListedData}
            className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">データが見つかりません</h2>
          <p>上場銘柄データが利用できません。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">jQuants 上場銘柄データ</h1>
      
      {/* メタデータ表示 */}
      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-2">データ情報</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <strong>総銘柄数:</strong> {data.metadata.total_stocks}
          </div>
          <div>
            <strong>最終更新:</strong> {new Date(data.metadata.last_updated).toLocaleString("ja-JP")}
          </div>
          <div>
            <strong>データタイプ:</strong> {data.metadata.data_type}
          </div>
        </div>
      </div>

      {/* 検索・フィルター */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">検索・フィルター</h2>
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              aria-expanded={showAdvancedFilters}
              aria-controls="advanced-filters"
            >
              {showAdvancedFilters ? "詳細フィルターを閉じる" : "詳細フィルターを開く"}
            </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              検索 (銘柄名・コード)
            </label>
            <StockSearchInput
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="銘柄名またはコードを入力..."
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              セクター
            </label>
            <select
              value={selectedSector}
              onChange={(e) => setSelectedSector(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">すべてのセクター</option>
              {getUniqueSectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              市場
            </label>
            <select
              value={selectedMarket}
              onChange={(e) => setSelectedMarket(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">すべての市場</option>
              {getUniqueMarkets.map(market => (
                <option key={market} value={market}>{market}</option>
              ))}
            </select>
          </div>
        </div>

        {showAdvancedFilters && (
          <div id="advanced-filters" className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  価格範囲 (円)
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={priceRange.min}
                    onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                    placeholder="最小価格"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="number"
                    value={priceRange.max}
                    onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                    placeholder="最大価格"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  出来高範囲
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={volumeRange.min}
                    onChange={(e) => setVolumeRange(prev => ({ ...prev, min: e.target.value }))}
                    placeholder="最小出来高"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="number"
                    value={volumeRange.max}
                    onChange={(e) => setVolumeRange(prev => ({ ...prev, max: e.target.value }))}
                    placeholder="最大出来高"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* クイックフィルタ */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => { setOnlyUp(prev => !prev); if (!onlyUp && onlyDown) setOnlyDown(false); setCurrentPage(1); }}
            className={`px-3 py-1 text-sm rounded border ${onlyUp ? "bg-green-50 border-green-500 text-green-700" : "bg-white border-gray-300 text-gray-700"}`}
          >
            上昇
          </button>
          <button
            onClick={() => { setOnlyDown(prev => !prev); if (!onlyDown && onlyUp) setOnlyUp(false); setCurrentPage(1); }}
            className={`px-3 py-1 text-sm rounded border ${onlyDown ? "bg-red-50 border-red-500 text-red-700" : "bg-white border-gray-300 text-gray-700"}`}
          >
            下落
          </button>
          <button
            onClick={() => { setHighVolume(prev => !prev); setCurrentPage(1); }}
            className={`px-3 py-1 text-sm rounded border ${highVolume ? "bg-blue-50 border-blue-500 text-blue-700" : "bg-white border-gray-300 text-gray-700"}`}
          >
            高出来高
          </button>
          {["プライム", "スタンダード", "グロース"].map(m => (
            <button
              key={m}
              onClick={() => { setSelectedMarket(cur => cur === m ? "" : m); setCurrentPage(1); }}
              className={`px-3 py-1 text-sm rounded border ${selectedMarket === m ? "bg-purple-50 border-purple-500 text-purple-700" : "bg-white border-gray-300 text-gray-700"}`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* 銘柄一覧 */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">
            銘柄一覧 ({filteredAndSortedStocks.length}件)
          </h2>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              {currentPage} / {totalPages} ページ
            </span>
            <button
              onClick={() => {
                const rows = filteredAndSortedStocks.map(s => ({
                  code: s.code,
                  name: s.name,
                  sector: s.sector,
                  market: s.market,
                  currentPrice: s.currentPrice ?? "",
                  change: s.change ?? "",
                  changePercent: s.changePercent ?? "",
                  volume: s.volume ?? "",
                  updated_at: s.updated_at,
                }));
                const header = Object.keys(rows[0] || { code: "", name: "" });
                const csv = [header.join(","), ...rows.map(r => header.map(h => `${(r as any)[h]}`.replace(/"/g, '""')).map(v => /[",\n]/.test(v) ? `"${v}"` : v).join(","))].join("\n");
                const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `listed_stocks_${new Date().toISOString().slice(0,10)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              CSVエクスポート
            </button>
            <button
              onClick={fetchListedData}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              更新
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleSort("code")}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleSort("code");
                    }
                  }}
                >
                  銘柄コード
                  {sortField === "code" && (
                    <span className="ml-1" aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
                  )}
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleSort("name")}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleSort("name");
                    }
                  }}
                >
                  会社名
                  {sortField === "name" && (
                    <span className="ml-1" aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
                  )}
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleSort("sector")}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleSort("sector");
                    }
                  }}
                >
                  セクター
                  {sortField === "sector" && (
                    <span className="ml-1" aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
                  )}
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleSort("market")}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleSort("market");
                    }
                  }}
                >
                  市場
                  {sortField === "market" && (
                    <span className="ml-1" aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
                  )}
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => handleSort("changePercent")}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleSort("changePercent");
                    }
                  }}
                >
                  騰落率
                  {sortField === "changePercent" && (
                    <span className="ml-1" aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
                  )}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  現在価格
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  出来高
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  更新日時
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  チャート
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  みんかぶ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  アクション
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedStocks.map((stock) => (
                <tr key={stock.code} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {formatStockCode(stock.code)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="max-w-xs truncate" title={stock.name}>
                      {stock.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="max-w-xs truncate" title={stock.sector}>
                      {stock.sector}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stock.market === "プライム" ? "bg-green-100 text-green-800" :
                      stock.market === "スタンダード" ? "bg-blue-100 text-blue-800" :
                      stock.market === "グロース" ? "bg-purple-100 text-purple-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {stock.market}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {stock.currentPrice ? `¥${stock.currentPrice.toLocaleString()}` : (
                      <span className="text-gray-400 italic">データ取得中...</span>
                    )}
                    {stock.change && stock.changePercent && (
                      <div className={`text-xs ${stock.change >= 0 ? "text-red-600" : "text-green-600"}`}>
                        {stock.change >= 0 ? "+" : ""}{stock.change.toLocaleString()} ({stock.changePercent >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%)
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stock.volume ? stock.volume.toLocaleString() : (
                      <span className="text-gray-400 italic">データ取得中...</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(stock.updated_at).toLocaleString("ja-JP")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => {
                        // チャートページに遷移
                        window.location.href = `/analysis?code=${stock.code}`;
                      }}
                      className="text-green-600 hover:text-green-800 font-medium focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 rounded px-2 py-1"
                      aria-label={`${stock.name} (${formatStockCode(stock.code)}) のチャートを表示`}
                    >
                      チャート
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => openMinkabuLink(stock.code)}
                      className="text-orange-600 hover:text-orange-800 font-medium focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 rounded px-2 py-1"
                      aria-label={`${stock.name} (${formatStockCode(stock.code)}) のみんかぶページを開く`}
                    >
                      みんかぶ
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setSelectedStock(stock.code);
                          setIsModalOpen(true);
                        }}
                        className="text-blue-600 hover:text-blue-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
                        aria-label={`${stock.name} (${formatStockCode(stock.code)}) の詳細を表示`}
                      >
                        詳細
                      </button>
                      <button
                      onClick={() => {
                          try {
                            const list = JSON.parse(localStorage.getItem("user_watchlist") || "[]");
                          const normalized = normalizeStockCode(stock.code);
                          if (!list.some((i: any) => i.symbol === normalized)) {
                              list.push({
                              symbol: normalized,
                                name: stock.name,
                                sector: stock.sector,
                                market: stock.market,
                                currentPrice: stock.currentPrice || 0,
                                change: stock.change || 0,
                                changePercent: stock.changePercent || 0,
                                addedAt: new Date().toISOString(),
                              });
                              localStorage.setItem("user_watchlist", JSON.stringify(list));
                            }
                          } catch (e) {
                            console.error("ウォッチリスト追加失敗", e);
                          }
                        }}
                        className="text-purple-600 hover:text-purple-800 font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 rounded px-2 py-1"
                      >
                        ウォッチ追加
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ページネーション */}
        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-sm text-gray-700">
                {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredAndSortedStocks.length)} / {filteredAndSortedStocks.length} 件
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={goToFirstPage}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="最初のページへ"
              >
                最初
              </button>
              <button
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="前のページへ"
              >
                前へ
              </button>
              <span className="px-3 py-1 text-sm bg-blue-500 text-white rounded" aria-label={`現在のページ: ${currentPage}`}>
                {currentPage}
              </span>
              <button
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="次のページへ"
              >
                次へ
              </button>
              <button
                onClick={goToLastPage}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="最後のページへ"
              >
                最後
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 銘柄詳細モーダル */}
      {selectedStock && (
        <StockDetailModal
          symbol={selectedStock}
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedStock(null);
          }}
        />
      )}
    </div>
  );
};

export default ListedDataPage;
