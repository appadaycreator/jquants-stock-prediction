"use client";

import React, { useState, useEffect } from "react";
import { SettingsProvider } from "../../contexts/SettingsContext";
import FiveMinRoutine from "../../components/FiveMinRoutine";
import TutorialSystem from "../../components/TutorialSystem";
import { useTutorial } from "../../components/TutorialSystem";
import { 
  ArrowLeft, 
  Home, 
  Settings, 
  BarChart3, 
  Target, 
  Shield,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

export default function FiveMinRoutinePage() {
  const [showTutorial, setShowTutorial] = useState(false);
  const { showTutorial: tutorialVisible, showTutorialAgain, hideTutorial } = useTutorial();

  const handleAnalysisClick = () => {
    // 分析実行ページに遷移
    window.location.href = "/";
  };

  const handleSettingsClick = () => {
    // 設定ページに遷移
    window.location.href = "/settings";
  };

  const handleReportClick = () => {
    // レポートページに遷移
    window.location.href = "/reports";
  };

  const handleTradeClick = () => {
    // 個人投資ページに遷移
    window.location.href = "/personal-investment";
  };

  const handleStepComplete = (stepId: string) => {
    console.log("ステップ完了:", stepId);
    // ステップ完了時の処理を追加
  };

  const handleTutorialComplete = () => {
    console.log("チュートリアル完了");
    setShowTutorial(false);
  };

  const handleTutorialSkip = () => {
    console.log("チュートリアルスキップ");
    setShowTutorial(false);
  };

  return (
    <SettingsProvider>
      <div className="min-h-screen bg-gray-50">
        {/* ヘッダー */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center space-x-4">
                <Link
                  href="/"
                  className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  ダッシュボードに戻る
                </Link>
                <div className="h-6 w-px bg-gray-300" />
                <h1 className="text-2xl font-bold text-gray-900">5分ルーティン</h1>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={showTutorialAgain}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <Target className="h-4 w-4 mr-2" />
                  チュートリアル
                </button>
                
                <Link
                  href="/settings"
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  設定
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* メインコンテンツ */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <FiveMinRoutine
            onAnalysisClick={handleAnalysisClick}
            onSettingsClick={handleSettingsClick}
            onReportClick={handleReportClick}
            onTradeClick={handleTradeClick}
            onStepComplete={handleStepComplete}
          />
        </main>

        {/* チュートリアル */}
        {tutorialVisible && (
          <TutorialSystem
            onComplete={handleTutorialComplete}
            onSkip={handleTutorialSkip}
            onStartAnalysis={handleAnalysisClick}
            onOpenSettings={handleSettingsClick}
            onOpenRoutine={() => {}}
          />
        )}
      </div>
    </SettingsProvider>
  );
}
