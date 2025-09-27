"use client";

import { useState, useEffect } from "react";
import { Search, X, Check, TrendingUp } from "lucide-react";

// 主要日本株の銘柄データ
const JAPANESE_STOCKS = [
  { code: "7203.T", name: "トヨタ自動車", sector: "自動車" },
  { code: "6758.T", name: "ソニーグループ", sector: "エンターテインメント" },
  { code: "9984.T", name: "ソフトバンクグループ", sector: "通信" },
  { code: "9432.T", name: "日本電信電話", sector: "通信" },
  { code: "6861.T", name: "キーエンス", sector: "電子部品" },
  { code: "4063.T", name: "信越化学工業", sector: "化学" },
  { code: "8035.T", name: "東京エレクトロン", sector: "半導体" },
  { code: "8306.T", name: "三菱UFJフィナンシャル・グループ", sector: "金融" },
  { code: "4503.T", name: "アステラス製薬", sector: "製薬" },
  { code: "4519.T", name: "中外製薬", sector: "製薬" },
  { code: "4061.T", name: "デンカ", sector: "化学" },
  { code: "4568.T", name: "第一三共", sector: "製薬" },
  { code: "6501.T", name: "日立製作所", sector: "電機" },
  { code: "6752.T", name: "パナソニック", sector: "電機" },
  { code: "6981.T", name: "村田製作所", sector: "電子部品" },
  { code: "7741.T", name: "HOYA", sector: "光学機器" },
  { code: "7974.T", name: "任天堂", sector: "エンターテインメント" },
  { code: "8001.T", name: "伊藤忠商事", sector: "商社" },
  { code: "8002.T", name: "丸紅", sector: "商社" },
  { code: "8031.T", name: "三井物産", sector: "商社" },
];

interface SymbolSelectorProps {
  selectedSymbols: string[];
  onSymbolsChange: (symbols: string[]) => void;
  onAnalysis: (symbols: string[]) => void;
  isAnalyzing?: boolean;
}

export default function SymbolSelector({
  selectedSymbols,
  onSymbolsChange,
  onAnalysis,
  isAnalyzing = false,
}: SymbolSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredStocks, setFilteredStocks] = useState(JAPANESE_STOCKS);

  useEffect(() => {
    if (searchTerm) {
      const filtered = JAPANESE_STOCKS.filter(
        (stock) =>
          stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stock.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stock.sector.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredStocks(filtered);
    } else {
      setFilteredStocks(JAPANESE_STOCKS);
    }
  }, [searchTerm]);

  const handleSymbolToggle = (symbol: string) => {
    if (selectedSymbols.includes(symbol)) {
      onSymbolsChange(selectedSymbols.filter((s) => s !== symbol));
    } else {
      onSymbolsChange([...selectedSymbols, symbol]);
    }
  };

  const handleRemoveSymbol = (symbol: string) => {
    onSymbolsChange(selectedSymbols.filter((s) => s !== symbol));
  };

  const getStockInfo = (code: string) => {
    return JAPANESE_STOCKS.find((stock) => stock.code === code);
  };

  return (
    <div className="space-y-4">
      {/* 検索バー */}
      <div className="relative">
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="銘柄名、コード、セクターで検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => setShowDropdown(true)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            onClick={() => onAnalysis(selectedSymbols)}
            disabled={selectedSymbols.length === 0 || isAnalyzing}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            {isAnalyzing ? "分析中..." : "分析実行"}
          </button>
        </div>

        {/* ドロップダウン */}
        {showDropdown && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {filteredStocks.map((stock) => (
              <div
                key={stock.code}
                onClick={() => {
                  handleSymbolToggle(stock.code);
                  setSearchTerm("");
                  setShowDropdown(false);
                }}
                className="flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer"
              >
                <div>
                  <div className="font-medium text-gray-900">{stock.name}</div>
                  <div className="text-sm text-gray-500">
                    {stock.code} • {stock.sector}
                  </div>
                </div>
                {selectedSymbols.includes(stock.code) && (
                  <Check className="h-4 w-4 text-blue-600" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 選択された銘柄 */}
      {selectedSymbols.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">
            選択された銘柄 ({selectedSymbols.length}件)
          </h3>
          <div className="flex flex-wrap gap-2">
            {selectedSymbols.map((symbol) => {
              const stockInfo = getStockInfo(symbol);
              return (
                <div
                  key={symbol}
                  className="flex items-center space-x-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm"
                >
                  <span className="font-medium">
                    {stockInfo?.name || symbol}
                  </span>
                  <span className="text-blue-500">({symbol})</span>
                  <button
                    onClick={() => handleRemoveSymbol(symbol)}
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* クイック選択ボタン */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-700">クイック選択</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onSymbolsChange(["7203.T", "6758.T", "9984.T"])}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            主要3銘柄
          </button>
          <button
            onClick={() => onSymbolsChange(["7203.T", "6758.T", "9984.T", "9432.T", "6861.T"])}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            主要5銘柄
          </button>
          <button
            onClick={() => onSymbolsChange(JAPANESE_STOCKS.slice(0, 10).map(s => s.code))}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            主要10銘柄
          </button>
          <button
            onClick={() => onSymbolsChange([])}
            className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full hover:bg-red-200"
          >
            全クリア
          </button>
        </div>
      </div>
    </div>
  );
}
