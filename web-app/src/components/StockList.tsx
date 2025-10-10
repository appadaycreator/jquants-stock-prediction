"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Search, Filter, SortAsc, SortDesc, TrendingUp, TrendingDown, Eye, ExternalLink } from "lucide-react";
import { formatStockCode, normalizeStockCode } from "@/lib/stock-code-utils";
import { openMinkabuLink, isMinkabuLinkAvailable } from "@/lib/minkabu-utils";

interface Stock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
  riskLevel: "Low" | "Medium" | "High";
  predictionAccuracy?: number;
}

interface StockListProps {
  stocks: Stock[];
  isLoading?: boolean;
  error?: Error | null;
  onStockSelect?: (stock: Stock) => void;
  onAddToPortfolio?: (stock: Stock) => void;
  onAddToWatchlist?: (stock: Stock) => void;
}

export const StockList: React.FC<StockListProps> = ({
  stocks,
  isLoading = false,
  error,
  onStockSelect,
  onAddToPortfolio,
  onAddToWatchlist,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<keyof Stock>("changePercent");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [filterSector, setFilterSector] = useState<string>("");
  const [filterRisk, setFilterRisk] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // フィルタリングとソート
  const filteredAndSortedStocks = useMemo(() => {
    let filtered = stocks.filter(stock => {
      const matchesSearch = stock.code.includes(searchTerm) || 
                           stock.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSector = !filterSector || stock.sector === filterSector;
      const matchesRisk = !filterRisk || stock.riskLevel === filterRisk;
      
      return matchesSearch && matchesSector && matchesRisk;
    });

    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
      }
      
      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortDirection === "asc" 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return 0;
    });

    return filtered;
  }, [stocks, searchTerm, sortField, sortDirection, filterSector, filterRisk]);

  // ページネーション
  const totalPages = Math.ceil(filteredAndSortedStocks.length / itemsPerPage);
  const paginatedStocks = filteredAndSortedStocks.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  // セクター一覧
  const sectors = useMemo(() => {
    const uniqueSectors = [...new Set(stocks.map(stock => stock.sector))];
    return uniqueSectors.sort();
  }, [stocks]);

  const handleSort = (field: keyof Stock) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "Low": return "text-green-600 bg-green-100";
      case "Medium": return "text-yellow-600 bg-yellow-100";
      case "High": return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
            <div className="flex items-center space-x-4">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <span className="font-medium">銘柄データの読み込みに失敗しました</span>
        </div>
        <p className="text-red-600 mt-2">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 検索・フィルター */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="銘柄コード・企業名で検索"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={filterSector}
            onChange={(e) => setFilterSector(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全セクター</option>
            {sectors.map(sector => (
              <option key={sector} value={sector}>{sector}</option>
            ))}
          </select>
          
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全リスクレベル</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
          
          <div className="text-sm text-gray-600 flex items-center">
            {filteredAndSortedStocks.length}件中 {paginatedStocks.length}件表示
          </div>
        </div>
      </div>

      {/* 銘柄一覧 */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 sticky left-0 z-10 bg-gray-50"
                  onClick={() => handleSort("code")}
                >
                  <div className="flex items-center space-x-1">
                    <span>コード</span>
                    {sortField === "code" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 sticky left-[10rem] z-10 bg-gray-50"
                  onClick={() => handleSort("name")}
                >
                  <div className="flex items-center space-x-1">
                    <span>企業名</span>
                    {sortField === "name" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("price")}
                >
                  <div className="flex items-center space-x-1">
                    <span>価格</span>
                    {sortField === "price" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("changePercent")}
                >
                  <div className="flex items-center space-x-1">
                    <span>騰落率</span>
                    {sortField === "changePercent" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("marketCap")}
                >
                  <div className="flex items-center space-x-1">
                    <span>時価総額</span>
                    {sortField === "marketCap" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort("riskLevel")}
                >
                  <div className="flex items-center space-x-1">
                    <span>リスク</span>
                    {sortField === "riskLevel" && (
                      sortDirection === "asc" ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  チャート
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  アクション
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedStocks.map((stock) => (
                <tr key={normalizeStockCode(stock.code)} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                    {formatStockCode(stock.code)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 sticky left-[10rem] bg-white">
                    <div className="flex items-center space-x-2">
                      <span>{stock.name}</span>
                      {isMinkabuLinkAvailable(stock.code) && (
                        <button
                          onClick={() => openMinkabuLink(stock.code)}
                          className="text-orange-600 hover:text-orange-900"
                          title="みんかぶで詳細を見る"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ¥{stock.price.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center space-x-1">
                      {stock.changePercent >= 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`font-medium ${
                        stock.changePercent >= 0 ? "text-green-600" : "text-red-600"
                      }`}>
                        {stock.changePercent >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ¥{(stock.marketCap / 100000000).toFixed(1)}億
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(stock.riskLevel)}`}>
                      {stock.riskLevel}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        // チャートページに遷移
                        window.location.href = `/analysis?code=${stock.code}`;
                      }}
                      className="text-green-600 hover:text-green-900 flex items-center space-x-1"
                      title="チャートを表示"
                    >
                      <TrendingUp className="w-4 h-4" />
                      <span>チャート</span>
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onStockSelect?.(stock)}
                        className="text-blue-600 hover:text-blue-900 flex items-center space-x-1"
                      >
                        <Eye className="w-4 h-4" />
                        <span>詳細</span>
                      </button>
                      <button
                        onClick={() => onAddToPortfolio?.(stock)}
                        className="text-green-600 hover:text-green-900"
                      >
                        ポートフォリオ
                      </button>
                      <button
                        onClick={() => onAddToWatchlist?.(stock)}
                        className="text-purple-600 hover:text-purple-900"
                      >
                        ウォッチ
                      </button>
                      {isMinkabuLinkAvailable(stock.code) && (
                        <button
                          onClick={() => openMinkabuLink(stock.code)}
                          className="text-orange-600 hover:text-orange-900 flex items-center space-x-1"
                          title="みんかぶで詳細を見る"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>みんかぶ</span>
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ページネーション */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                前へ
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                次へ
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span>
                  -
                  <span className="font-medium">
                    {Math.min(currentPage * itemsPerPage, filteredAndSortedStocks.length)}
                  </span>
                  /
                  <span className="font-medium">{filteredAndSortedStocks.length}</span>
                  件
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  {[...Array(totalPages)].map((_, i) => (
                    <button
                      key={i + 1}
                      onClick={() => setCurrentPage(i + 1)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        currentPage === i + 1
                          ? "z-10 bg-blue-50 border-blue-500 text-blue-600"
                          : "bg-white border-gray-300 text-gray-500 hover:bg-gray-50"
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockList;
