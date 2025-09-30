"use client";

import { useState } from 'react';
import { 
  BarChart3, 
  FileText, 
  ShoppingCart, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react';

interface QuickActionHandlerProps {
  onAnalysisComplete?: (result: any) => void;
  onReportGenerated?: (report: any) => void;
  onTradeExecuted?: (trade: any) => void;
}

export default function QuickActionHandler({
  onAnalysisComplete,
  onReportGenerated,
  onTradeExecuted
}: QuickActionHandlerProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isExecutingTrade, setIsExecutingTrade] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);

  // 分析実行
  const executeAnalysis = async () => {
    setIsAnalyzing(true);
    setLastAction('analysis');
    
    try {
      // 分析実行APIを呼び出し
      const response = await fetch('/api/execute-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'full_analysis',
          symbols: ['7203.T', '6758.T', '6861.T'],
          timeframe: '1d'
        })
      });

      if (response.ok) {
        const result = await response.json();
        onAnalysisComplete?.(result);
        
        // 成功通知
        showNotification('分析が完了しました', 'success');
      } else {
        throw new Error('分析実行に失敗しました');
      }
    } catch (error) {
      console.error('分析実行エラー:', error);
      showNotification('分析実行に失敗しました', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // レポート生成
  const generateReport = async () => {
    setIsGeneratingReport(true);
    setLastAction('report');
    
    try {
      // レポート生成APIを呼び出し
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'daily_summary',
          includeCharts: true,
          includeRecommendations: true
        })
      });

      if (response.ok) {
        const report = await response.json();
        onReportGenerated?.(report);
        
        // レポートページを開く
        window.open('/reports', '_blank');
        showNotification('レポートが生成されました', 'success');
      } else {
        throw new Error('レポート生成に失敗しました');
      }
    } catch (error) {
      console.error('レポート生成エラー:', error);
      showNotification('レポート生成に失敗しました', 'error');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // 売買指示実行
  const executeTrade = async () => {
    setIsExecutingTrade(true);
    setLastAction('trade');
    
    try {
      // 売買指示APIを呼び出し
      const response = await fetch('/api/execute-trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'recommended_actions',
          confirmBeforeExecute: true
        })
      });

      if (response.ok) {
        const trade = await response.json();
        onTradeExecuted?.(trade);
        
        showNotification('売買指示が実行されました', 'success');
      } else {
        throw new Error('売買指示実行に失敗しました');
      }
    } catch (error) {
      console.error('売買指示実行エラー:', error);
      showNotification('売買指示実行に失敗しました', 'error');
    } finally {
      setIsExecutingTrade(false);
    }
  };

  // 通知表示
  const showNotification = (message: string, type: 'success' | 'error' | 'info') => {
    // 簡単な通知実装（実際のプロジェクトではより高度な通知システムを使用）
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
      type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
      'bg-blue-100 text-blue-800 border border-blue-200'
    }`;
    notification.innerHTML = `
      <div class="flex items-center space-x-2">
        ${type === 'success' ? '<div class="w-4 h-4 bg-green-500 rounded-full"></div>' :
          type === 'error' ? '<div class="w-4 h-4 bg-red-500 rounded-full"></div>' :
          '<div class="w-4 h-4 bg-blue-500 rounded-full"></div>'}
        <span>${message}</span>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  };

  return {
    executeAnalysis,
    generateReport,
    executeTrade,
    isAnalyzing,
    isGeneratingReport,
    isExecutingTrade,
    lastAction
  };
}
