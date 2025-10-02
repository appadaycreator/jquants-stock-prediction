/**
 * ダッシュボードクイックアクション
 * 主要機能への直接アクセスを提供
 */

"use client";

import React from 'react';
import Link from 'next/link';
import { 
  TrendingUp, 
  Target, 
  DollarSign, 
  BarChart3, 
  Clock, 
  Settings,
  ArrowRight,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

interface QuickActionProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  status?: 'success' | 'warning' | 'error' | 'loading';
  badge?: string;
  onClick?: () => void;
}

function QuickActionCard({
  title,
  description,
  icon,
  href,
  status = 'success',
  badge,
  onClick,
}: QuickActionProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-200 bg-green-50 hover:bg-green-100';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 hover:bg-yellow-100';
      case 'error':
        return 'border-red-200 bg-red-50 hover:bg-red-100';
      case 'loading':
        return 'border-blue-200 bg-blue-50 hover:bg-blue-100';
      default:
        return 'border-gray-200 bg-gray-50 hover:bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'loading':
        return <RefreshCw className="w-4 h-4 text-blue-600 animate-spin" />;
      default:
        return null;
    }
  };

  return (
    <Link
      href={href}
      onClick={onClick}
      className={`block p-6 rounded-lg border-2 transition-all duration-200 ${getStatusColor(status)}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            {icon}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
            <p className="text-sm text-gray-600 mb-3">{description}</p>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status)}
              <span className="text-sm text-gray-500">クリックして開く</span>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>
        {badge && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {badge}
          </span>
        )}
      </div>
    </Link>
  );
}

interface DashboardQuickActionsProps {
  todayData?: {
    hasData: boolean;
    lastUpdated?: string;
    signalCount?: number;
  };
  personalInvestmentData?: {
    hasData: boolean;
    lastUpdated?: string;
    portfolioValue?: number;
  };
  onRefresh?: () => void;
}

export default function DashboardQuickActions({
  todayData,
  personalInvestmentData,
  onRefresh,
}: DashboardQuickActionsProps) {
  const quickActions = [
    {
      title: '今日の投資指示',
      description: '本日の売買候補と投資指示を確認',
      icon: <Target className="w-8 h-8 text-blue-600" />,
      href: '/today',
      status: (todayData?.hasData ? 'success' : 'warning') as 'success' | 'warning' | 'error' | 'loading',
      badge: todayData?.signalCount ? `${todayData.signalCount}件` : undefined,
    },
    {
      title: '個人投資ポートフォリオ',
      description: '個人投資の状況と推奨銘柄を確認',
      icon: <DollarSign className="w-8 h-8 text-green-600" />,
      href: '/personal-investment',
      status: (personalInvestmentData?.hasData ? 'success' : 'warning') as 'success' | 'warning' | 'error' | 'loading',
      badge: personalInvestmentData?.portfolioValue 
        ? `¥${personalInvestmentData.portfolioValue.toLocaleString()}`
        : undefined,
    },
    {
      title: '5分ルーティン',
      description: '効率的な投資分析のためのステップガイド',
      icon: <Clock className="w-8 h-8 text-purple-600" />,
      href: '/five-min-routine',
      status: 'success' as 'success' | 'warning' | 'error' | 'loading',
    },
    {
      title: '詳細分析',
      description: '詳細な分析結果とチャートを確認',
      icon: <BarChart3 className="w-8 h-8 text-orange-600" />,
      href: '/dashboard',
      status: 'success' as 'success' | 'warning' | 'error' | 'loading',
    },
  ];

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">クイックアクション</h2>
          <p className="text-gray-600 mt-1">
            主要機能への直接アクセス
          </p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>更新</span>
          </button>
        )}
      </div>

      {/* クイックアクションカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {quickActions.map((action, index) => (
          <QuickActionCard
            key={index}
            {...action}
          />
        ))}
      </div>

      {/* データの鮮度表示 */}
      {(todayData?.lastUpdated || personalInvestmentData?.lastUpdated) && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">データの鮮度</h3>
          <div className="space-y-2">
            {todayData?.lastUpdated && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">今日の指示</span>
                <span className="text-gray-900">
                  {new Date(todayData.lastUpdated).toLocaleString()}
                </span>
              </div>
            )}
            {personalInvestmentData?.lastUpdated && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">個人投資</span>
                <span className="text-gray-900">
                  {new Date(personalInvestmentData.lastUpdated).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * ミニダッシュボードカード
 */
interface MiniDashboardCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
  href?: string;
}

export function MiniDashboardCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  href,
}: MiniDashboardCardProps) {
  const getChangeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />;
      case 'negative':
        return <TrendingUp className="w-4 h-4 rotate-180" />;
      default:
        return null;
    }
  };

  const content = (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center space-x-1 mt-1 ${getChangeColor(changeType)}`}>
              {getChangeIcon(changeType)}
              <span className="text-sm font-medium">
                {change > 0 ? '+' : ''}{change}%
              </span>
            </div>
          )}
        </div>
        <div className="text-gray-400">
          {icon}
        </div>
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="block">
        {content}
      </Link>
    );
  }

  return content;
}
