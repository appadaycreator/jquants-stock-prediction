"use client";

import { useState } from 'react';
import { fetchJson } from '../lib/fetcher';
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
      const result = await fetchJson<any>('/api/execute-analysis', {
        json: {
          type: 'full_analysis',
          symbols: ['7203.T', '6758.T', '6861.T'],
          timeframe: '1d'
        },
        idempotencyKey: true
      });
      onAnalysisComplete?.(result);
      showNotification('分析が完了しました', 'success');
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
      const report = await fetchJson<any>('/api/generate-report', {
        json: {
          type: 'daily_summary',
          includeCharts: true,
          includeRecommendations: true
        },
        idempotencyKey: true
      });
      onReportGenerated?.(report);
      window.open('/reports', '_blank');
      showNotification('レポートが生成されました', 'success');
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
      const trade = await fetchJson<any>('/api/execute-trade', {
        json: {
          type: 'recommended_actions',
          confirmBeforeExecute: true
        },
        idempotencyKey: true
      });
      onTradeExecuted?.(trade);
      showNotification('売買指示が実行されました', 'success');
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
