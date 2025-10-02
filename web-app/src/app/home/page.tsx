"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MobileOptimizedDashboard from "@/components/MobileOptimizedDashboard";
import EnhancedFiveMinRoutine from "@/components/EnhancedFiveMinRoutine";
import { 
  Smartphone, 
  Target, 
  TrendingUp, 
  Clock, 
  Zap,
  Eye,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Play,
  Pause,
  RotateCcw,
  Home,
  Settings,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [currentView, setCurrentView] = useState<"dashboard" | "routine">("dashboard");
  const [isMobile, setIsMobile] = useState(false);

  // モバイル判定
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // ナビゲーションハンドラー
  const handleAnalysisClick = () => {
    router.push("/analysis");
  };

  const handleReportClick = () => {
    router.push("/reports");
  };

  const handleTradeClick = () => {
    router.push("/trading");
  };

  const handleSettingsClick = () => {
    router.push("/settings");
  };

  const handleRoutineStart = () => {
    setCurrentView("routine");
  };

  const handleBackToDashboard = () => {
    setCurrentView("dashboard");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Home className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {currentView === "dashboard" ? "ホーム" : "5分ルーティン"}
                </h1>
                <p className="text-sm text-gray-600">
                  {currentView === "dashboard" ? "今日の投資判断" : "効率的な分析フロー"}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {currentView === "routine" && (
                <button
                  onClick={handleBackToDashboard}
                  className="bg-gray-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-gray-700 flex items-center space-x-1"
                >
                  <Home className="h-4 w-4" />
                  <span>ホーム</span>
                </button>
              )}
              <button
                onClick={handleSettingsClick}
                className="bg-gray-100 text-gray-600 px-3 py-2 rounded-lg text-sm hover:bg-gray-200 flex items-center space-x-1"
              >
                <Settings className="h-4 w-4" />
                <span>設定</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="max-w-md mx-auto">
        {currentView === "dashboard" ? (
          <MobileOptimizedDashboard
            onAnalysisClick={handleAnalysisClick}
            onReportClick={handleReportClick}
            onTradeClick={handleTradeClick}
            onSettingsClick={handleSettingsClick}
          />
        ) : (
          <div className="p-4">
            <EnhancedFiveMinRoutine
              onAnalysisClick={handleAnalysisClick}
              onReportClick={handleReportClick}
              onTradeClick={handleTradeClick}
              onSettingsClick={handleSettingsClick}
            />
          </div>
        )}
      </div>

      {/* モバイル最適化インジケーター */}
      {isMobile && (
        <div className="fixed bottom-4 right-4 z-20">
          <div className="bg-blue-600 text-white p-3 rounded-full shadow-lg">
            <Smartphone className="h-5 w-5" />
          </div>
        </div>
      )}

      {/* フッター */}
      <div className="bg-white border-t mt-8">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="text-center text-xs text-gray-500">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Clock className="h-4 w-4" />
              <span>5分で完了・上下スクロールのみで完結</span>
            </div>
            <p>個人投資のための効率的な分析ツール</p>
          </div>
        </div>
      </div>
    </div>
  );
}
