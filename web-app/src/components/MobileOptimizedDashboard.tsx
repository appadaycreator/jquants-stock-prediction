"use client";

import { useState, useEffect, useCallback } from "react";
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
} from "lucide-react";

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  action: () => void;
  estimatedTime: string;
}

interface MobileOptimizedDashboardProps {
  onAnalysisClick?: () => void;
  onReportClick?: () => void;
  onTradeClick?: () => void;
  onSettingsClick?: () => void;
}

export default function MobileOptimizedDashboard({
  onAnalysisClick,
  onReportClick,
  onTradeClick,
  onSettingsClick,
}: MobileOptimizedDashboardProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [routineProgress, setRoutineProgress] = useState(0);
  const [isRoutineRunning, setIsRoutineRunning] = useState(false);

  // モバイル判定
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // タイマー更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // クイックアクション定義
  const quickActions: QuickAction[] = [
    {
      id: "start_routine",
      title: "5分ルーティン開始",
      description: "今日の投資判断を5分で完了",
      icon: <Play className="h-6 w-6" />,
      color: "bg-green-600 hover:bg-green-700",
      action: () => {
        setIsRoutineRunning(true);
        setRoutineProgress(0);
        // ルーティン開始ロジック
      },
      estimatedTime: "5分",
    },
    {
      id: "quick_analysis",
      title: "ワンクリック分析",
      description: "主要銘柄の即座分析",
      icon: <BarChart3 className="h-6 w-6" />,
      color: "bg-blue-600 hover:bg-blue-700",
      action: onAnalysisClick || (() => console.log("分析開始")),
      estimatedTime: "2分",
    },
    {
      id: "view_reports",
      title: "分析結果確認",
      description: "最新の予測結果を確認",
      icon: <TrendingUp className="h-6 w-6" />,
      color: "bg-purple-600 hover:bg-purple-700",
      action: onReportClick || (() => console.log("レポート表示")),
      estimatedTime: "1分",
    },
    {
      id: "trading_dashboard",
      title: "取引ダッシュボード",
      description: "投資判断とアクション",
      icon: <Target className="h-6 w-6" />,
      color: "bg-orange-600 hover:bg-orange-700",
      action: onTradeClick || (() => console.log("取引ダッシュボード")),
      estimatedTime: "3分",
    },
  ];

  // ルーティン進捗更新
  useEffect(() => {
    if (isRoutineRunning) {
      const interval = setInterval(() => {
        setRoutineProgress(prev => {
          if (prev >= 100) {
            setIsRoutineRunning(false);
            return 100;
          }
          return prev + 2; // 5分で100%になるように調整
        });
      }, 6000); // 6秒ごとに2%増加

      return () => clearInterval(interval);
    }
  }, [isRoutineRunning]);

  // ルーティン完了処理
  const handleRoutineComplete = useCallback(() => {
    setIsRoutineRunning(false);
    setRoutineProgress(100);
  }, []);

  // ルーティンリセット
  const handleRoutineReset = useCallback(() => {
    setIsRoutineRunning(false);
    setRoutineProgress(0);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Smartphone className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">投資ダッシュボード</h1>
                <p className="text-sm text-gray-600">5分で完了する投資判断</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">
                {currentTime.toLocaleTimeString("ja-JP", { 
                  hour: "2-digit", 
                  minute: "2-digit", 
                })}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto px-4 py-6 space-y-6">
        {/* ルーティン進捗 */}
        {isRoutineRunning && (
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-green-600" />
                <h2 className="text-lg font-semibold text-gray-900">5分ルーティン実行中</h2>
              </div>
              <button
                onClick={handleRoutineReset}
                className="text-gray-500 hover:text-gray-700"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
              <div 
                className="bg-green-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${routineProgress}%` }}
              />
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>進捗: {routineProgress}%</span>
              <span>残り時間: {Math.max(0, 5 - Math.floor(routineProgress / 20))}分</span>
            </div>
            
            {routineProgress >= 100 && (
              <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-green-800 font-medium">ルーティン完了！</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* クイックアクション */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-gray-900">今日のアクション</h2>
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={action.action}
              className={`w-full ${action.color} text-white p-4 rounded-xl transition-all duration-200 transform hover:scale-105 active:scale-95`}
            >
              <div className="flex items-center space-x-4">
                <div className="bg-white bg-opacity-20 p-2 rounded-lg">
                  {action.icon}
                </div>
                <div className="flex-1 text-left">
                  <h3 className="font-semibold text-lg">{action.title}</h3>
                  <p className="text-sm opacity-90">{action.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs opacity-75">{action.estimatedTime}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* 今日のサマリー */}
        <div className="bg-white rounded-xl border p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">今日のサマリー</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">完了したタスク</span>
              <span className="font-semibold text-green-600">3/5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">分析済み銘柄</span>
              <span className="font-semibold text-blue-600">12銘柄</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">推奨アクション</span>
              <span className="font-semibold text-orange-600">2件</span>
            </div>
          </div>
        </div>

        {/* モバイル最適化ヒント */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Smartphone className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">モバイル最適化</h3>
          </div>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 縦スクロールのみで全操作完了</li>
            <li>• 大きなボタンでタッチ操作を最適化</li>
            <li>• 5分以内に投資判断完了</li>
            <li>• オフライン時もフォールバック機能</li>
          </ul>
        </div>

        {/* 緊急アクション */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <h3 className="font-semibold text-red-900">緊急アクション</h3>
          </div>
          <p className="text-sm text-red-800 mb-3">
            市場の急変により、以下の銘柄で緊急対応が必要です。
          </p>
          <button className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
            緊急対応を確認
          </button>
        </div>

        {/* 進捗表示 */}
        <div className="bg-white rounded-xl border p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">進捗状況</h3>
            <span className="text-sm text-gray-600">3/5 完了</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: "60%" }}
            />
          </div>
        </div>

        {/* フッター */}
        <div className="text-center text-xs text-gray-500 pb-6">
          <div className="flex items-center justify-center space-x-2">
            <Clock className="h-4 w-4" />
            <span>5分で完了・上下スクロールのみで完結</span>
          </div>
        </div>
      </div>
    </div>
  );
}