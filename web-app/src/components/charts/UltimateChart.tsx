'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3, 
  Settings, 
  Download, 
  Share2, 
  Maximize2,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Move,
  Activity,
  Target,
  TrendingUp,
  TrendingDown,
  Cpu,
  Zap,
  Gauge,
  Eye,
  EyeOff,
  Layers,
  Filter,
  RefreshCw
} from 'lucide-react';

import ProfessionalChart from './ProfessionalChart';
import AnimatedChart from './AnimatedChart';
import WebGLChart from './WebGLChart';
import '../../styles/ultimate-chart.css';

interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ChartMode {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  component: React.ComponentType<any>;
  features: string[];
}

interface UltimateChartProps {
  data: CandleData[];
  symbol: string;
  height?: number;
  width?: number;
  defaultMode?: string;
  enableAllModes?: boolean;
  onDataPointClick?: (data: CandleData) => void;
  onExport?: (format: 'png' | 'svg' | 'pdf') => void;
  onShare?: () => void;
  className?: string;
}

export const UltimateChart: React.FC<UltimateChartProps> = ({
  data,
  symbol,
  height = 600,
  width,
  defaultMode = 'professional',
  enableAllModes = true,
  onDataPointClick,
  onExport,
  onShare,
  className = ''
}) => {
  const [currentMode, setCurrentMode] = useState(defaultMode);
  const [showSettings, setShowSettings] = useState(false);
  const [showIndicators, setShowIndicators] = useState(true);
  const [showVolume, setShowVolume] = useState(true);
  const [showTrendLines, setShowTrendLines] = useState(true);
  const [enableAnimation, setEnableAnimation] = useState(true);
  const [enableWebGL, setEnableWebGL] = useState(true);
  const [showPerformance, setShowPerformance] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // チャートモードの定義
  const chartModes: ChartMode[] = useMemo(() => [
    {
      id: 'professional',
      name: 'プロフェッショナル',
      description: '高度なテクニカル指標と分析機能',
      icon: <BarChart3 className="w-5 h-5" />,
      component: ProfessionalChart,
      features: ['テクニカル指標', '高度な分析', 'プロ仕様']
    },
    {
      id: 'animated',
      name: 'アニメーション',
      description: '滑らかなアニメーションとトレンド分析',
      icon: <Activity className="w-5 h-5" />,
      component: AnimatedChart,
      features: ['アニメーション', 'トレンド分析', '視覚効果']
    },
    {
      id: 'webgl',
      name: 'WebGL高速',
      description: 'GPU加速による超高速描画',
      icon: <Zap className="w-5 h-5" />,
      component: WebGLChart,
      features: ['GPU加速', '高速描画', '大量データ対応']
    }
  ], []);

  // 現在のチャートコンポーネント
  const CurrentChartComponent = useMemo(() => {
    const mode = chartModes.find(m => m.id === currentMode);
    return mode?.component || ProfessionalChart;
  }, [currentMode, chartModes]);

  // チャートの統計情報
  const chartStats = useMemo(() => {
    if (!data.length) return null;

    const prices = data.map(d => d.close);
    const volumes = data.map(d => d.volume);
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
    const maxVolume = Math.max(...volumes);
    const totalVolume = volumes.reduce((a, b) => a + b, 0);
    const priceChange = prices[prices.length - 1] - prices[0];
    const priceChangePercent = (priceChange / prices[0]) * 100;

    return {
      maxPrice,
      minPrice,
      avgPrice,
      maxVolume,
      totalVolume,
      priceChange,
      priceChangePercent,
      dataPoints: data.length
    };
  }, [data]);

  // エクスポート機能
  const handleExport = useCallback((format: 'png' | 'svg' | 'pdf') => {
    if (onExport) {
      onExport(format);
    } else {
      // デフォルトのエクスポート処理
      console.log(`Exporting chart as ${format}`);
    }
  }, [onExport]);

  // シェア機能
  const handleShare = useCallback(() => {
    if (onShare) {
      onShare();
    } else if (navigator.share) {
      navigator.share({
        title: `${symbol} チャート`,
        text: `${symbol} の株価チャートを共有`,
        url: window.location.href
      });
    }
  }, [onShare, symbol]);

  // フルスクリーン切り替え
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  return (
    <div className={`ultimate-chart-container ${className} ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm border-b">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">{symbol}</h2>
          </div>
          
          {/* チャートモード選択 */}
          {enableAllModes && (
            <div className="flex space-x-1">
              {chartModes.map((mode) => (
                <motion.button
                  key={mode.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentMode(mode.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    currentMode === mode.id
                      ? 'bg-blue-500 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {mode.icon}
                  <span>{mode.name}</span>
                </motion.button>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* 統計情報 */}
          {chartStats && (
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span>高値: ¥{chartStats.maxPrice.toLocaleString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <TrendingDown className="w-4 h-4 text-red-500" />
                <span>安値: ¥{chartStats.minPrice.toLocaleString()}</span>
              </div>
              <div className={`flex items-center space-x-1 ${
                chartStats.priceChange >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                <span>{chartStats.priceChange >= 0 ? '+' : ''}{chartStats.priceChangePercent.toFixed(2)}%</span>
              </div>
            </div>
          )}

          {/* コントロールボタン */}
          <div className="flex items-center space-x-1">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              title="設定"
            >
              <Settings className="w-4 h-4" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleFullscreen}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              title="フルスクリーン"
            >
              <Maximize2 className="w-4 h-4" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleExport('png')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              title="エクスポート"
            >
              <Download className="w-4 h-4" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleShare}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              title="シェア"
            >
              <Share2 className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* チャートエリア */}
      <div className="relative">
        <CurrentChartComponent
          data={data}
          symbol={symbol}
          height={height}
          width={width}
          showVolume={showVolume}
          showTrendLines={showTrendLines}
          enableAnimation={enableAnimation}
          enableWebGL={enableWebGL}
          showPerformance={showPerformance}
          theme={theme}
          onDataPointClick={onDataPointClick}
        />

        {/* 設定パネル */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              transition={{ duration: 0.3 }}
              className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-6 border border-gray-200 w-80"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">チャート設定</h3>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                {/* 表示設定 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">表示設定</h4>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">出来高表示</span>
                      <button
                        onClick={() => setShowVolume(!showVolume)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          showVolume ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          showVolume ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </label>
                    
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">トレンドライン</span>
                      <button
                        onClick={() => setShowTrendLines(!showTrendLines)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          showTrendLines ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          showTrendLines ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </label>
                    
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">アニメーション</span>
                      <button
                        onClick={() => setEnableAnimation(!enableAnimation)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          enableAnimation ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          enableAnimation ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </label>
                  </div>
                </div>

                {/* パフォーマンス設定 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">パフォーマンス</h4>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">WebGL加速</span>
                      <button
                        onClick={() => setEnableWebGL(!enableWebGL)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          enableWebGL ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          enableWebGL ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </label>
                    
                    <label className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">パフォーマンス表示</span>
                      <button
                        onClick={() => setShowPerformance(!showPerformance)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          showPerformance ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                          showPerformance ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </label>
                  </div>
                </div>

                {/* テーマ設定 */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">テーマ</h4>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setTheme('light')}
                      className={`px-3 py-2 rounded-md text-sm transition-colors ${
                        theme === 'light' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      ライト
                    </button>
                    <button
                      onClick={() => setTheme('dark')}
                      className={`px-3 py-2 rounded-md text-sm transition-colors ${
                        theme === 'dark' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      ダーク
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* フッター情報 */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t">
        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4" />
            <span>モード: {chartModes.find(m => m.id === currentMode)?.name}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4" />
            <span>データ数: {data.length}</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Cpu className="w-3 h-3" />
            <span>{enableWebGL ? 'WebGL' : 'Canvas'}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Gauge className="w-3 h-3" />
            <span>高性能</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UltimateChart;
