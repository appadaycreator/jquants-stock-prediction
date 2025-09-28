"use client";

import { useState, useEffect } from "react";
import { 
  RefreshCw, 
  Menu, 
  X, 
  Home, 
  TrendingUp, 
  Target, 
  Settings,
  Star,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  Eye,
  Plus
} from "lucide-react";
import JudgmentPanel from "./JudgmentPanel";
import WatchlistManager from "./WatchlistManager";
import PeriodSelector from "./PeriodSelector";
import ParallelUpdateManager from "./ParallelUpdateManager";

interface MobileFirstDashboardProps {
  className?: string;
}

export default function MobileFirstDashboard({ className = "" }: MobileFirstDashboardProps) {
  const [activeTab, setActiveTab] = useState<'home' | 'watchlist' | 'update' | 'settings'>('home');
  const [showSidebar, setShowSidebar] = useState(false);
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState('1m');
  const [isUpdating, setIsUpdating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // モバイル判定
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // タブの切り替え
  const handleTabChange = (tab: 'home' | 'watchlist' | 'update' | 'settings') => {
    setActiveTab(tab);
    setShowSidebar(false);
  };

  // 銘柄選択
  const handleStockSelect = (symbol: string) => {
    console.log('銘柄選択:', symbol);
    // 実際の実装では銘柄詳細ページに遷移
  };

  // アクション実行
  const handleActionClick = (action: string, symbol: string) => {
    console.log('アクション実行:', action, symbol);
    // 実際の実装では取引指示の実行
  };

  // 期間変更
  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
  };

  // カスタム日付変更
  const handleCustomDateChange = (startDate: string, endDate: string) => {
    console.log('カスタム期間:', startDate, endDate);
  };

  // 更新開始
  const handleUpdateStart = () => {
    setIsUpdating(true);
    setLastUpdate(new Date());
  };

  // 更新完了
  const handleUpdateComplete = (results: any[]) => {
    setIsUpdating(false);
    console.log('更新完了:', results);
  };

  // 進捗更新
  const handleProgressChange = (progress: number) => {
    console.log('進捗:', progress);
  };

  // サイドバーのコンテンツ
  const renderSidebarContent = () => (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">メニュー</h2>
        <button
          onClick={() => setShowSidebar(false)}
          className="p-2 text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
      
      <nav className="space-y-2">
        <button
          onClick={() => handleTabChange('home')}
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
            activeTab === 'home' 
              ? 'bg-blue-50 text-blue-700 border border-blue-200' 
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Home className="h-5 w-5" />
          <span>ホーム</span>
        </button>
        
        <button
          onClick={() => handleTabChange('watchlist')}
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
            activeTab === 'watchlist' 
              ? 'bg-blue-50 text-blue-700 border border-blue-200' 
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Star className="h-5 w-5" />
          <span>ウォッチリスト</span>
        </button>
        
        <button
          onClick={() => handleTabChange('update')}
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
            activeTab === 'update' 
              ? 'bg-blue-50 text-blue-700 border border-blue-200' 
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <RefreshCw className="h-5 w-5" />
          <span>一括更新</span>
        </button>
        
        <button
          onClick={() => handleTabChange('settings')}
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
            activeTab === 'settings' 
              ? 'bg-blue-50 text-blue-700 border border-blue-200' 
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Settings className="h-5 w-5" />
          <span>設定</span>
        </button>
      </nav>
    </div>
  );

  // メインコンテンツのレンダリング
  const renderMainContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="space-y-6">
            {/* 期間選択 */}
            <div className="bg-white rounded-lg shadow border p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">期間選択</h3>
              <PeriodSelector
                selectedPeriod={selectedPeriod}
                onPeriodChange={handlePeriodChange}
                onCustomDateChange={handleCustomDateChange}
              />
            </div>

            {/* 判断パネル */}
            <JudgmentPanel
              onStockSelect={handleStockSelect}
              onActionClick={handleActionClick}
            />

            {/* クイックアクション */}
            <div className="bg-white rounded-lg shadow border p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">クイックアクション</h3>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => handleTabChange('watchlist')}
                  className="flex items-center justify-center space-x-2 p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors"
                >
                  <Star className="h-5 w-5" />
                  <span>ウォッチリスト</span>
                </button>
                <button
                  onClick={() => handleTabChange('update')}
                  className="flex items-center justify-center space-x-2 p-4 bg-green-50 text-green-700 rounded-lg border border-green-200 hover:bg-green-100 transition-colors"
                >
                  <RefreshCw className="h-5 w-5" />
                  <span>一括更新</span>
                </button>
              </div>
            </div>
          </div>
        );

      case 'watchlist':
        return (
          <WatchlistManager
            onStockSelect={handleStockSelect}
            onWatchlistChange={(watchlists) => {
              console.log('ウォッチリスト変更:', watchlists);
            }}
          />
        );

      case 'update':
        return (
          <ParallelUpdateManager
            symbols={selectedSymbols.length > 0 ? selectedSymbols : ['7203.T', '6758.T', '6861.T']}
            onUpdateComplete={handleUpdateComplete}
            onProgressChange={handleProgressChange}
            maxConcurrent={4}
            timeout={30000}
          />
        );

      case 'settings':
        return (
          <div className="bg-white rounded-lg shadow border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">設定</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  更新間隔（秒）
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="30">30秒</option>
                  <option value="60">1分</option>
                  <option value="300">5分</option>
                  <option value="600">10分</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  通知設定
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="mr-2" />
                    <span className="text-sm text-gray-700">価格変動通知</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="mr-2" />
                    <span className="text-sm text-gray-700">出来高急増通知</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm text-gray-700">予測乖離通知</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowSidebar(true)}
                className="p-2 text-gray-600 hover:text-gray-900"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-lg font-bold text-gray-900">J-Quants予測</h1>
                <p className="text-xs text-gray-600">5分ルーティン</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {lastUpdate && (
                <div className="text-xs text-gray-500">
                  {lastUpdate.toLocaleTimeString('ja-JP')}
                </div>
              )}
              <button
                onClick={() => handleTabChange('update')}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* サイドバー */}
      {showSidebar && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50" onClick={() => setShowSidebar(false)} />
          <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg z-50">
            {renderSidebarContent()}
          </div>
        </>
      )}

      {/* メインコンテンツ */}
      <main className="p-4 pb-20">
        {renderMainContent()}
      </main>

      {/* 固定CTA（モバイル用） */}
      {isMobile && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-30">
          <div className="p-4">
            <button
              onClick={() => handleTabChange('update')}
              className="w-full flex items-center justify-center space-x-2 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="h-5 w-5" />
              <span className="font-medium">更新</span>
            </button>
          </div>
        </div>
      )}

      {/* タブナビゲーション（モバイル用） */}
      {isMobile && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-30">
          <div className="grid grid-cols-4">
            <button
              onClick={() => handleTabChange('home')}
              className={`flex flex-col items-center py-3 px-2 text-xs ${
                activeTab === 'home' 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600'
              }`}
            >
              <Home className="h-5 w-5 mb-1" />
              <span>ホーム</span>
            </button>
            
            <button
              onClick={() => handleTabChange('watchlist')}
              className={`flex flex-col items-center py-3 px-2 text-xs ${
                activeTab === 'watchlist' 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600'
              }`}
            >
              <Star className="h-5 w-5 mb-1" />
              <span>ウォッチ</span>
            </button>
            
            <button
              onClick={() => handleTabChange('update')}
              className={`flex flex-col items-center py-3 px-2 text-xs ${
                activeTab === 'update' 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600'
              }`}
            >
              <RefreshCw className="h-5 w-5 mb-1" />
              <span>更新</span>
            </button>
            
            <button
              onClick={() => handleTabChange('settings')}
              className={`flex flex-col items-center py-3 px-2 text-xs ${
                activeTab === 'settings' 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600'
              }`}
            >
              <Settings className="h-5 w-5 mb-1" />
              <span>設定</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
