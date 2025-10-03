'use client';

import React, { useState, useEffect } from 'react';
import { MobileLayout } from '@/components/mobile/MobileLayout';
import { FirstView } from '@/components/mobile/FirstView';
import { LightweightChart } from '@/components/charts/LightweightChart';
import { SkeletonLoader } from '@/components/ui/SkeletonLoader';
import { TrendingUp, BarChart3, Settings } from 'lucide-react';

interface KPIData {
  label: string;
  value: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'neutral';
}

interface CandidateStock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  score: number;
  reason: string;
}

interface ChartData {
  time: number;
  value: number;
  volume?: number;
}

export default function MobilePage() {
  const [activeTab, setActiveTab] = useState('today');
  const [isLoading, setIsLoading] = useState(true);
  const [kpis, setKpis] = useState<KPIData[]>([]);
  const [candidates, setCandidates] = useState<CandidateStock[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);

  // モックデータの生成
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      
      // シミュレートされたローディング時間
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // KPIデータの生成
      setKpis([
        {
          label: 'ポートフォリオ',
          value: 1250000,
          change: 25000,
          changePercent: 2.04,
          trend: 'up'
        },
        {
          label: '今日の収益',
          value: 15000,
          change: 5000,
          changePercent: 50.0,
          trend: 'up'
        },
        {
          label: '保有銘柄',
          value: 12,
          change: 0,
          changePercent: 0,
          trend: 'neutral'
        },
        {
          label: 'リスクスコア',
          value: 3.2,
          change: -0.3,
          changePercent: -8.57,
          trend: 'down'
        }
      ]);

      // 候補銘柄データの生成
      setCandidates([
        {
          code: '7203',
          name: 'トヨタ自動車',
          price: 2850,
          change: 45,
          changePercent: 1.6,
          score: 8.5,
          reason: '業績好調、EV戦略が評価'
        },
        {
          code: '9984',
          name: 'ソフトバンクグループ',
          price: 8200,
          change: -120,
          changePercent: -1.44,
          score: 7.8,
          reason: 'AI投資が注目、技術革新期待'
        },
        {
          code: '6758',
          name: 'ソニーグループ',
          price: 12500,
          change: 180,
          changePercent: 1.46,
          score: 8.2,
          reason: 'エンターテイメント事業好調'
        },
        {
          code: '4568',
          name: '第一三共',
          price: 4200,
          change: 85,
          changePercent: 2.06,
          score: 7.9,
          reason: '新薬承認、医療需要増加'
        },
        {
          code: '8306',
          name: '三菱UFJフィナンシャル・グループ',
          price: 950,
          change: 12,
          changePercent: 1.28,
          score: 7.5,
          reason: '金利上昇期待、金融業界回復'
        }
      ]);

      // チャートデータの生成
      const now = Date.now();
      const chartData: ChartData[] = [];
      for (let i = 30; i >= 0; i--) {
        const time = now - (i * 24 * 60 * 60 * 1000);
        const baseValue = 1200000;
        const randomChange = (Math.random() - 0.5) * 50000;
        const value = baseValue + randomChange + (i * 1000);
        
        chartData.push({
          time,
          value,
          volume: Math.floor(Math.random() * 1000000) + 500000
        });
      }
      setChartData(chartData);
      
      setIsLoading(false);
    };

    loadData();
  }, []);

  const handleRefresh = async () => {
    setIsLoading(true);
    // 実際のAPI呼び出しをシミュレート
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsLoading(false);
  };

  const handleStockClick = (stock: CandidateStock) => {
    console.log('Stock clicked:', stock);
    // 銘柄詳細ページへの遷移
  };

  const handleDataPointClick = (data: ChartData) => {
    console.log('Data point clicked:', data);
    // データポイントの詳細表示
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'today':
        return (
          <FirstView
            kpis={kpis}
            candidates={candidates}
            isLoading={isLoading}
            onRefresh={handleRefresh}
            onStockClick={handleStockClick}
          />
        );

      case 'stocks':
        return (
          <div className="p-4 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">銘柄一覧</h2>
            {isLoading ? (
              <SkeletonLoader type="list" lines={10} />
            ) : (
              <div className="space-y-3">
                {candidates.map((stock) => (
                  <div key={stock.code} className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">{stock.name}</div>
                        <div className="text-sm text-gray-600">{stock.code}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-gray-900">
                          ¥{stock.price.toLocaleString()}
                        </div>
                        <div className={`text-sm ${
                          stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'analysis':
        return (
          <div className="p-4 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">分析</h2>
            {isLoading ? (
              <SkeletonLoader type="chart" />
            ) : (
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">ポートフォリオ推移</h3>
                <LightweightChart
                  data={chartData}
                  type="line"
                  height={200}
                  onDataPointClick={handleDataPointClick}
                />
              </div>
            )}
          </div>
        );

      case 'settings':
        return (
          <div className="p-4 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">設定</h2>
            <div className="space-y-3">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-medium text-gray-900">通知設定</h3>
                <p className="text-sm text-gray-600">重要な市場動向をお知らせします</p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-medium text-gray-900">アカウント</h3>
                <p className="text-sm text-gray-600">プロフィールと認証設定</p>
              </div>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-medium text-gray-900">データ管理</h3>
                <p className="text-sm text-gray-600">キャッシュと同期設定</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <MobileLayout
      currentTab={activeTab}
      onTabChange={setActiveTab}
    >
      {renderTabContent()}
    </MobileLayout>
  );
}
