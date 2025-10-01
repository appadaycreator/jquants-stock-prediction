"use client";

import { useState, useEffect } from "react";
import { 
  Plus, 
  Edit3, 
  Trash2, 
  Download, 
  Upload, 
  GripVertical,
  Search,
  X,
  Check,
  AlertCircle,
  Star,
  StarOff,
} from "lucide-react";

interface WatchlistItem {
  id: string;
  symbol: string;
  name: string;
  sector?: string;
  addedAt: string;
  isFavorite?: boolean;
  tags?: string[];
}

interface Watchlist {
  id: string;
  name: string;
  items: WatchlistItem[];
  createdAt: string;
  updatedAt: string;
}

interface WatchlistManagerProps {
  onWatchlistChange?: (watchlists: Watchlist[]) => void;
  onStockSelect?: (symbol: string) => void;
}

export default function WatchlistManager({ 
  onWatchlistChange, 
  onStockSelect, 
}: WatchlistManagerProps) {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [activeWatchlist, setActiveWatchlist] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingWatchlist, setEditingWatchlist] = useState<Watchlist | null>(null);
  const [newWatchlistName, setNewWatchlistName] = useState("");
  const [renamingWatchlistId, setRenamingWatchlistId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showStockSearch, setShowStockSearch] = useState(false);
  const [stockSearchResults, setStockSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [newTagInput, setNewTagInput] = useState<{ [itemId: string]: string }>({});
  const [activeSectorFilter, setActiveSectorFilter] = useState<string | null>(null);
  const [activeTagFilter, setActiveTagFilter] = useState<string | null>(null);

  // サンプルデータの初期化
  useEffect(() => {
    const sampleWatchlists: Watchlist[] = [
      {
        id: "1",
        name: "主要銘柄",
        items: [
          { id: "1-1", symbol: "7203.T", name: "トヨタ自動車", sector: "自動車", addedAt: "2024-01-01", isFavorite: true, tags: ["大型株", "自動車"] },
          { id: "1-2", symbol: "6758.T", name: "ソニーグループ", sector: "エンターテインメント", addedAt: "2024-01-02", isFavorite: false, tags: ["エレクトロニクス"] },
          { id: "1-3", symbol: "6861.T", name: "キーエンス", sector: "電子部品", addedAt: "2024-01-03", isFavorite: true, tags: ["計測機器"] },
        ],
        createdAt: "2024-01-01",
        updatedAt: "2024-01-15",
      },
      {
        id: "2",
        name: "成長株",
        items: [
          { id: "2-1", symbol: "9984.T", name: "ソフトバンクグループ", sector: "通信", addedAt: "2024-01-05", isFavorite: false, tags: ["投資持株"] },
          { id: "2-2", symbol: "4063.T", name: "信越化学工業", sector: "化学", addedAt: "2024-01-06", isFavorite: true, tags: ["半導体材料"] },
        ],
        createdAt: "2024-01-05",
        updatedAt: "2024-01-10",
      },
    ];
    
    setWatchlists(sampleWatchlists);
    if (sampleWatchlists.length > 0) {
      setActiveWatchlist(sampleWatchlists[0].id);
    }
  }, []);

  // ウォッチリスト変更の通知
  useEffect(() => {
    onWatchlistChange?.(watchlists);
  }, [watchlists, onWatchlistChange]);

  // 銘柄検索
  const searchStocks = async (query: string) => {
    if (query.length < 2) {
      setStockSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      // 実際のAPI呼び出しをここに実装
      // 現在はサンプルデータを使用
      const sampleResults = [
        { symbol: "7203.T", name: "トヨタ自動車", sector: "自動車" },
        { symbol: "6758.T", name: "ソニーグループ", sector: "エンターテインメント" },
        { symbol: "6861.T", name: "キーエンス", sector: "電子部品" },
        { symbol: "9984.T", name: "ソフトバンクグループ", sector: "通信" },
        { symbol: "4063.T", name: "信越化学工業", sector: "化学" },
      ].filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase()),
      );
      
      setStockSearchResults(sampleResults);
    } catch (error) {
      console.error("銘柄検索エラー:", error);
    } finally {
      setIsSearching(false);
    }
  };

  // ウォッチリスト作成
  const createWatchlist = () => {
    if (!newWatchlistName.trim()) return;

    const newWatchlist: Watchlist = {
      id: Date.now().toString(),
      name: newWatchlistName,
      items: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setWatchlists(prev => [...prev, newWatchlist]);
    setActiveWatchlist(newWatchlist.id);
    setNewWatchlistName("");
    setShowCreateModal(false);
  };

  // ウォッチリスト編集
  const editWatchlist = (watchlist: Watchlist) => {
    setEditingWatchlist(watchlist);
    setNewWatchlistName(watchlist.name);
    setRenamingWatchlistId(watchlist.id);
  };

  // ウォッチリスト更新
  const updateWatchlist = () => {
    if (!editingWatchlist || !newWatchlistName.trim()) return;

    setWatchlists(prev => prev.map(wl => 
      wl.id === editingWatchlist.id 
        ? { ...wl, name: newWatchlistName, updatedAt: new Date().toISOString() }
        : wl,
    ));
    
    setEditingWatchlist(null);
    setNewWatchlistName("");
    setRenamingWatchlistId(null);
  };

  // インライン編集保存（Enter/blur）
  const handleInlineRenameCommit = () => {
    if (!renamingWatchlistId) return;
    const wl = watchlists.find(w => w.id === renamingWatchlistId);
    if (!wl) return;
    if (!newWatchlistName.trim() || newWatchlistName === wl.name) {
      setRenamingWatchlistId(null);
      return;
    }
    setWatchlists(prev => prev.map(w =>
      w.id === renamingWatchlistId ? { ...w, name: newWatchlistName.trim(), updatedAt: new Date().toISOString() } : w,
    ));
    setRenamingWatchlistId(null);
    setNewWatchlistName("");
  };

  // ウォッチリスト削除
  const deleteWatchlist = (id: string) => {
    if (confirm("このウォッチリストを削除しますか？")) {
      setWatchlists(prev => prev.filter(wl => wl.id !== id));
      if (activeWatchlist === id) {
        const remaining = watchlists.filter(wl => wl.id !== id);
        setActiveWatchlist(remaining.length > 0 ? remaining[0].id : null);
      }
    }
  };

  // 銘柄追加
  const addStockToWatchlist = (stock: any) => {
    if (!activeWatchlist) return;

    const newItem: WatchlistItem = {
      id: `${activeWatchlist}-${Date.now()}`,
      symbol: stock.symbol,
      name: stock.name,
      sector: stock.sector,
      addedAt: new Date().toISOString(),
      isFavorite: false,
      tags: [],
    };

    setWatchlists(prev => prev.map(wl => 
      wl.id === activeWatchlist 
        ? { ...wl, items: [...wl.items, newItem], updatedAt: new Date().toISOString() }
        : wl,
    ));

    setShowStockSearch(false);
    setSearchQuery("");
    setStockSearchResults([]);
  };

  // 銘柄削除
  const removeStockFromWatchlist = (watchlistId: string, itemId: string) => {
    setWatchlists(prev => prev.map(wl => 
      wl.id === watchlistId 
        ? { ...wl, items: wl.items.filter(item => item.id !== itemId), updatedAt: new Date().toISOString() }
        : wl,
    ));
  };

  // お気に入り切り替え
  const toggleFavorite = (watchlistId: string, itemId: string) => {
    setWatchlists(prev => prev.map(wl => 
      wl.id === watchlistId 
        ? { 
            ...wl, 
            items: wl.items.map(item => 
              item.id === itemId 
                ? { ...item, isFavorite: !item.isFavorite }
                : item,
            ),
            updatedAt: new Date().toISOString(),
          }
        : wl,
    ));
  };

  // タグの追加
  const addTagToItem = (watchlistId: string, itemId: string, tag: string) => {
    const trimmed = tag.trim();
    if (!trimmed) return;
    setWatchlists(prev => prev.map(wl =>
      wl.id === watchlistId
        ? {
            ...wl,
            items: wl.items.map(item =>
              item.id === itemId
                ? { ...item, tags: Array.from(new Set([...(item.tags || []), trimmed])) }
                : item,
            ),
            updatedAt: new Date().toISOString(),
          }
        : wl,
    ));
    setNewTagInput(prev => ({ ...prev, [itemId]: "" }));
  };

  // タグの削除
  const removeTagFromItem = (watchlistId: string, itemId: string, tag: string) => {
    setWatchlists(prev => prev.map(wl =>
      wl.id === watchlistId
        ? {
            ...wl,
            items: wl.items.map(item =>
              item.id === itemId
                ? { ...item, tags: (item.tags || []).filter(t => t !== tag) }
                : item,
            ),
            updatedAt: new Date().toISOString(),
          }
        : wl,
    ));
  };

  // ドラッグ&ドロップで並べ替え
  const handleDragStart = (index: number) => {
    setDragIndex(index);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    if (dragIndex === null || !activeWatchlist) return;

    const activeWatchlistData = watchlists.find(wl => wl.id === activeWatchlist);
    if (!activeWatchlistData) return;

    const items = [...activeWatchlistData.items];
    const draggedItem = items[dragIndex];
    items.splice(dragIndex, 1);
    items.splice(dropIndex, 0, draggedItem);

    setWatchlists(prev => prev.map(wl => 
      wl.id === activeWatchlist 
        ? { ...wl, items, updatedAt: new Date().toISOString() }
        : wl,
    ));

    setDragIndex(null);
  };

  // JSONエクスポート
  const exportWatchlists = () => {
    const dataStr = JSON.stringify(watchlists, null, 2);
    const dataUri = "data:application/json;charset=utf-8,"+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `watchlists_${new Date().toISOString().split("T")[0]}.json`;
    
    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  // JSONインポート
  const importWatchlists = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target?.result as string);
        if (Array.isArray(importedData)) {
          setWatchlists(importedData);
          if (importedData.length > 0) {
            setActiveWatchlist(importedData[0].id);
          }
        }
      } catch (error) {
        alert("ファイルの形式が正しくありません。");
      }
    };
    reader.readAsText(file);
  };

  const currentWatchlist = watchlists.find(wl => wl.id === activeWatchlist);

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">ウォッチリスト管理</h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={exportWatchlists}
            className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            エクスポート
          </button>
          <label className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            インポート
            <input
              type="file"
              accept=".json"
              onChange={importWatchlists}
              className="hidden"
            />
          </label>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            新規作成
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ウォッチリスト一覧 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow border">
            <div className="p-4 border-b">
              <h3 className="font-semibold text-gray-900">ウォッチリスト</h3>
            </div>
            <div className="p-4 space-y-2">
              {watchlists.map((watchlist) => (
                <div
                  key={watchlist.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    activeWatchlist === watchlist.id
                      ? "bg-blue-50 border-blue-200"
                      : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                  }`}
                  onClick={() => setActiveWatchlist(watchlist.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      {renamingWatchlistId === watchlist.id ? (
                        <input
                          autoFocus
                          type="text"
                          value={newWatchlistName}
                          onChange={(e) => setNewWatchlistName(e.target.value)}
                          onBlur={handleInlineRenameCommit}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleInlineRenameCommit();
                            if (e.key === "Escape") {
                              setRenamingWatchlistId(null);
                              setNewWatchlistName("");
                            }
                          }}
                          className="px-2 py-1 border border-blue-300 rounded w-full"
                        />
                      ) : (
                        <h4 className="font-medium text-gray-900">{watchlist.name}</h4>
                      )}
                      <p className="text-sm text-gray-500">{watchlist.items.length}銘柄</p>
                    </div>
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          editWatchlist(watchlist);
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteWatchlist(watchlist.id);
                        }}
                        className="p-1 text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 銘柄一覧 */}
        <div className="lg:col-span-2">
          {currentWatchlist ? (
            <div className="bg-white rounded-lg shadow border">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">{currentWatchlist.name}</h3>
                  <button
                    onClick={() => setShowStockSearch(true)}
                    className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    銘柄追加
                  </button>
                </div>
              </div>
              {/* フィルタ行 */}
              <div className="px-4 pt-3">
                <div className="flex flex-wrap items-center gap-2">
                  <select
                    className="px-2 py-1 border border-gray-300 rounded"
                    value={activeSectorFilter || ""}
                    onChange={e => setActiveSectorFilter(e.target.value || null)}
                  >
                    <option value="">すべてのセクター</option>
                    {Array.from(new Set(currentWatchlist.items.map(i => i.sector).filter(Boolean))).map(sec => (
                      <option key={sec as string} value={sec as string}>{sec as string}</option>
                    ))}
                  </select>
                  <select
                    className="px-2 py-1 border border-gray-300 rounded"
                    value={activeTagFilter || ""}
                    onChange={e => setActiveTagFilter(e.target.value || null)}
                  >
                    <option value="">すべてのタグ</option>
                    {Array.from(new Set(currentWatchlist.items.flatMap(i => i.tags || []))).map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))}
                  </select>
                  {(activeSectorFilter || activeTagFilter) && (
                    <button
                      onClick={() => { setActiveSectorFilter(null); setActiveTagFilter(null); }}
                      className="text-xs px-2 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
                    >
                      フィルタ解除
                    </button>
                  )}
                </div>
              </div>
              
              {currentWatchlist.items.length > 0 ? (
                <div className="p-4 space-y-2">
                  {currentWatchlist.items
                    .filter(item => !activeSectorFilter || item.sector === activeSectorFilter)
                    .filter(item => !activeTagFilter || (item.tags || []).includes(activeTagFilter))
                    .map((item, index) => (
                    <div
                      key={item.id}
                      draggable
                      onDragStart={() => handleDragStart(index)}
                      onDragOver={handleDragOver}
                      onDrop={(e) => handleDrop(e, index)}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <GripVertical className="h-4 w-4 text-gray-400 cursor-move" />
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium text-gray-900">{item.symbol}</h4>
                            {item.isFavorite && <Star className="h-4 w-4 text-yellow-500 fill-current" />}
                          </div>
                          <p className="text-sm text-gray-600">{item.name}</p>
                          {item.sector && (
                            <p className="text-xs text-gray-500">{item.sector}</p>
                          )}
                            {/* タグ群 */}
                            <div className="flex flex-wrap items-center gap-1 mt-1">
                              {(item.tags || []).map(tag => (
                                <span key={tag} className="inline-flex items-center text-xs px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded">
                                  {tag}
                                  <button
                                    onClick={() => removeTagFromItem(currentWatchlist.id, item.id, tag)}
                                    className="ml-1 text-blue-500 hover:text-blue-700"
                                    aria-label="remove-tag"
                                  >
                                    ×
                                  </button>
                                </span>
                              ))}
                              <input
                                type="text"
                                value={newTagInput[item.id] || ""}
                                onChange={e => setNewTagInput(prev => ({ ...prev, [item.id]: e.target.value }))}
                                onKeyDown={e => {
                                  if (e.key === "Enter") {
                                    addTagToItem(currentWatchlist.id, item.id, newTagInput[item.id] || "");
                                  }
                                }}
                                placeholder="タグ追加"
                                className="text-xs px-2 py-1 border border-gray-300 rounded"
                              />
                              <button
                                onClick={() => addTagToItem(currentWatchlist.id, item.id, newTagInput[item.id] || "")}
                                className="text-xs px-2 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50"
                              >追加</button>
                            </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => toggleFavorite(currentWatchlist.id, item.id)}
                          className="p-1 text-gray-400 hover:text-yellow-500"
                        >
                          {item.isFavorite ? (
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          ) : (
                            <StarOff className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          onClick={() => onStockSelect?.(item.symbol)}
                          className="p-1 text-gray-400 hover:text-blue-600"
                        >
                          <Search className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => removeStockFromWatchlist(currentWatchlist.id, item.id)}
                          className="p-1 text-gray-400 hover:text-red-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium">銘柄がありません</p>
                  <p className="text-sm">「銘柄追加」ボタンから銘柄を追加してください</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow border p-8 text-center text-gray-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">ウォッチリストがありません</p>
              <p className="text-sm">「新規作成」ボタンからウォッチリストを作成してください</p>
            </div>
          )}
        </div>
      </div>

      {/* 新規作成モーダル */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">新しいウォッチリスト</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ウォッチリスト名
                </label>
                <input
                  type="text"
                  value={newWatchlistName}
                  onChange={(e) => setNewWatchlistName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="例: 主要銘柄"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={createWatchlist}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  作成
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 編集モーダルは廃止（インライン編集に置換） */}

      {/* 銘柄検索モーダル */}
      {showStockSearch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">銘柄検索・追加</h3>
              <button
                onClick={() => setShowStockSearch(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  銘柄検索（コード・社名）
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      searchStocks(e.target.value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="例: 7203, トヨタ"
                  />
                  {isSearching && (
                    <div className="absolute right-3 top-3">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    </div>
                  )}
                </div>
              </div>
              
              {stockSearchResults.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">検索結果</h4>
                  {stockSearchResults.map((stock) => (
                    <div
                      key={stock.symbol}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors"
                    >
                      <div>
                        <h5 className="font-medium text-gray-900">{stock.symbol}</h5>
                        <p className="text-sm text-gray-600">{stock.name}</p>
                        {stock.sector && (
                          <p className="text-xs text-gray-500">{stock.sector}</p>
                        )}
                      </div>
                      <button
                        onClick={() => addStockToWatchlist(stock)}
                        className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        追加
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              {searchQuery.length >= 2 && stockSearchResults.length === 0 && !isSearching && (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>該当する銘柄が見つかりませんでした</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
