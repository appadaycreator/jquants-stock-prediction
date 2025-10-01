"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Search, 
  Plus, 
  X, 
  Upload, 
  Download, 
  Trash2, 
  Edit, 
  Check, 
  AlertCircle,
  Info,
  FileText,
  Clock,
  Star,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

interface WatchlistItem {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  addedDate: string;
  notes?: string;
  priority: "high" | "medium" | "low";
  alerts: {
    priceTarget?: number;
    stopLoss?: number;
    volumeAlert?: boolean;
  };
}

interface EnhancedWatchlistModalProps {
  isOpen: boolean;
  onClose: () => void;
  watchlist: WatchlistItem[];
  onWatchlistUpdate: (watchlist: WatchlistItem[]) => void;
  onImport: (file: File) => void;
  onExport: () => void;
}

export default function EnhancedWatchlistModal({
  isOpen,
  onClose,
  watchlist,
  onWatchlistUpdate,
  onImport,
  onExport,
}: EnhancedWatchlistModalProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSymbol, setNewSymbol] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const [newPriority, setNewPriority] = useState<"high" | "medium" | "low">("medium");
  const [editingItem, setEditingItem] = useState<WatchlistItem | null>(null);
  const [showImportHelp, setShowImportHelp] = useState(false);
  const [recentSymbols, setRecentSymbols] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 最近追加した銘柄を取得
  useEffect(() => {
    const recent = localStorage.getItem("recent_watchlist_symbols");
    if (recent) {
      setRecentSymbols(JSON.parse(recent));
    }
  }, []);

  // 銘柄検索の候補
  const searchSuggestions = [
    "7203.T", "6758.T", "6861.T", "9984.T", "9432.T", "6752.T", "4063.T", "8306.T",
  ].filter(symbol => 
    symbol.toLowerCase().includes(searchTerm.toLowerCase()) && 
    !watchlist.some(item => item.symbol === symbol),
  );

  const filteredWatchlist = watchlist.filter(item =>
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const handleAddSymbol = () => {
    if (!newSymbol.trim()) return;

    const newItem: WatchlistItem = {
      symbol: newSymbol.toUpperCase(),
      name: "", // 実際の実装ではAPIから取得
      currentPrice: 0,
      change: 0,
      changePercent: 0,
      addedDate: new Date().toISOString(),
      notes: newNotes,
      priority: newPriority,
      alerts: {},
    };

    const updatedWatchlist = [...watchlist, newItem];
    onWatchlistUpdate(updatedWatchlist);

    // 最近追加した銘柄に追加
    const recent = [...recentSymbols.filter(s => s !== newSymbol), newSymbol].slice(0, 5);
    setRecentSymbols(recent);
    localStorage.setItem("recent_watchlist_symbols", JSON.stringify(recent));

    setNewSymbol("");
    setNewNotes("");
    setNewPriority("medium");
    setShowAddForm(false);
  };

  const handleRemoveSymbol = (symbol: string) => {
    const updatedWatchlist = watchlist.filter(item => item.symbol !== symbol);
    onWatchlistUpdate(updatedWatchlist);
  };

  const handleEditSymbol = (item: WatchlistItem) => {
    setEditingItem(item);
  };

  const handleSaveEdit = () => {
    if (!editingItem) return;

    const updatedWatchlist = watchlist.map(item =>
      item.symbol === editingItem.symbol ? editingItem : item,
    );
    onWatchlistUpdate(updatedWatchlist);
    setEditingItem(null);
  };

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onImport(file);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-300";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "low":
        return "bg-green-100 text-green-800 border-green-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return "text-green-600";
    if (change < 0) return "text-red-600";
    return "text-gray-600";
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-4 w-4" />;
    if (change < 0) return <TrendingDown className="h-4 w-4" />;
    return null;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* ヘッダー */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">ウォッチリスト管理</h2>
              <p className="text-sm text-gray-600">監視銘柄の追加・編集・削除</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* 検索と追加 */}
          <div className="flex items-center space-x-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="銘柄コードまたは銘柄名で検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              銘柄追加
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Upload className="h-4 w-4 mr-2" />
              インポート
            </button>
            <button
              onClick={onExport}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              エクスポート
            </button>
          </div>

          {/* 検索候補 */}
          {searchTerm && searchSuggestions.length > 0 && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="text-sm font-medium text-blue-900 mb-2">検索候補</div>
              <div className="flex flex-wrap gap-2">
                {searchSuggestions.slice(0, 5).map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => {
                      setNewSymbol(symbol);
                      setShowAddForm(true);
                    }}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 transition-colors"
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 最近追加した銘柄 */}
          {recentSymbols.length > 0 && !searchTerm && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="text-sm font-medium text-gray-900 mb-2">最近追加した銘柄</div>
              <div className="flex flex-wrap gap-2">
                {recentSymbols.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => {
                      setNewSymbol(symbol);
                      setShowAddForm(true);
                    }}
                    className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm hover:bg-gray-200 transition-colors"
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 追加フォーム */}
          {showAddForm && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">銘柄追加</h3>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    銘柄コード
                  </label>
                  <input
                    type="text"
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                    placeholder="例: 7203.T"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    優先度
                  </label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value as any)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="high">高</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    メモ（任意）
                  </label>
                  <textarea
                    value={newNotes}
                    onChange={(e) => setNewNotes(e.target.value)}
                    placeholder="この銘柄についてのメモ..."
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end space-x-3 mt-4">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleAddSymbol}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  追加
                </button>
              </div>
            </div>
          )}

          {/* ウォッチリスト一覧 */}
          <div className="space-y-3">
            {filteredWatchlist.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Star className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>ウォッチリストが空です</p>
                <p className="text-sm">銘柄を追加して監視を開始しましょう</p>
              </div>
            ) : (
              filteredWatchlist.map((item) => (
                <div
                  key={item.symbol}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-900">{item.symbol}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(item.priority)}`}>
                            {item.priority === "high" ? "高" : item.priority === "medium" ? "中" : "低"}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{item.name || "銘柄名を取得中..."}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="font-semibold text-gray-900">
                          ¥{item.currentPrice.toLocaleString()}
                        </div>
                        <div className={`flex items-center space-x-1 text-sm ${getChangeColor(item.change)}`}>
                          {getChangeIcon(item.change)}
                          <span>
                            {item.change > 0 ? "+" : ""}{item.change} ({item.changePercent > 0 ? "+" : ""}{item.changePercent}%)
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEditSymbol(item)}
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleRemoveSymbol(item.symbol)}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  {item.notes && (
                    <div className="mt-2 text-sm text-gray-600">
                      <Info className="h-4 w-4 inline mr-1" />
                      {item.notes}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* インポートヘルプ */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-blue-900">CSVインポートについて</h4>
              <button
                onClick={() => setShowImportHelp(!showImportHelp)}
                className="text-blue-600 hover:text-blue-800"
              >
                <Info className="h-4 w-4" />
              </button>
            </div>
            {showImportHelp && (
              <div className="text-sm text-blue-800">
                <p className="mb-2">CSVファイルの形式:</p>
                <div className="bg-white p-3 rounded border text-xs font-mono">
                  symbol,name,priority,notes<br />
                  7203.T,トヨタ自動車,high,注目銘柄<br />
                  6758.T,ソニーグループ,medium,
                </div>
                <p className="mt-2 text-xs">
                  • symbol: 銘柄コード（必須）<br />
                  • name: 銘柄名（任意）<br />
                  • priority: 優先度（high/medium/low、任意）<br />
                  • notes: メモ（任意）
                </p>
              </div>
            )}
          </div>

          {/* 隠しファイル入力 */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileImport}
            className="hidden"
          />
        </div>
      </div>
    </div>
  );
}
