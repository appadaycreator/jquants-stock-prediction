/**
 * 新NISA枠管理ページ
 * 投資枠の利用状況、ポートフォリオ、取引履歴を管理
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  DollarSign, 
  TrendingUp, 
  AlertTriangle, 
  Plus, 
  RefreshCw,
  BarChart3,
  History,
  Settings
} from 'lucide-react';
import { useNisaData } from '@/hooks/useNisaData';
import NisaQuotaCard from '@/components/nisa/NisaQuotaCard';
import NisaPortfolioCard from '@/components/nisa/NisaPortfolioCard';
import NisaTransactionForm from '@/components/nisa/NisaTransactionForm';
import { NisaTransaction } from '@/lib/nisa/types';

export default function NisaPage() {
  const {
    data,
    calculationResult,
    loading,
    error,
    refreshData,
    addTransaction,
    updateTransaction,
    deleteTransaction,
    quotas,
    portfolio,
    optimization,
    taxCalculation,
    alerts,
    opportunities,
    statistics,
  } = useNisaData();

  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<NisaTransaction | null>(null);

  const handleAddTransaction = async (transaction: Omit<NisaTransaction, 'id' | 'createdAt' | 'updatedAt'>) => {
    const result = await addTransaction(transaction);
    if (result.isValid) {
      setShowTransactionForm(false);
      setEditingTransaction(null);
    }
  };

  const handleEditTransaction = (transaction: NisaTransaction) => {
    setEditingTransaction(transaction);
    setShowTransactionForm(true);
  };

  const handleCancelTransaction = () => {
    setShowTransactionForm(false);
    setEditingTransaction(null);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">データを読み込み中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription>
            データの読み込みに失敗しました: {error}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">新NISA枠管理</h1>
          <p className="text-gray-600 mt-2">投資枠の利用状況とポートフォリオを管理</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={refreshData}
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            更新
          </Button>
          <Button
            onClick={() => setShowTransactionForm(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            取引追加
          </Button>
        </div>
      </div>

      {/* アラート表示 */}
      {alerts.length > 0 && (
        <div className="mb-6 space-y-3">
          {alerts.map((alert) => (
            <Alert key={alert.id} variant={alert.type === 'CRITICAL' ? 'destructive' : 'default'}>
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>
                <div className="flex items-center justify-between">
                  <span>{alert.message}</span>
                  <Badge variant="outline">{alert.quotaType === 'GROWTH' ? '成長' : 'つみたて'}</Badge>
                </div>
                {alert.recommendedAction && (
                  <div className="mt-2 text-sm text-gray-600">
                    {alert.recommendedAction}
                  </div>
                )}
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* 取引フォーム */}
      {showTransactionForm && (
        <div className="mb-8">
          <NisaTransactionForm
            transaction={editingTransaction || undefined}
            onSubmit={handleAddTransaction}
            onCancel={handleCancelTransaction}
            loading={loading}
          />
        </div>
      )}

      {/* メインコンテンツ */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            概要
          </TabsTrigger>
          <TabsTrigger value="portfolio" className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            ポートフォリオ
          </TabsTrigger>
          <TabsTrigger value="transactions" className="flex items-center gap-2">
            <History className="w-4 h-4" />
            取引履歴
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            設定
          </TabsTrigger>
        </TabsList>

        {/* 概要タブ */}
        <TabsContent value="overview" className="space-y-6">
          {/* 統計サマリー */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <DollarSign className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">総投資額</p>
                    <p className="text-2xl font-bold">¥{statistics.totalInvested.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">現在価値</p>
                    <p className="text-2xl font-bold">¥{statistics.totalValue.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">損益</p>
                    <p className={`text-2xl font-bold ${statistics.totalProfitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {statistics.totalProfitLoss >= 0 ? '+' : ''}¥{statistics.totalProfitLoss.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <AlertTriangle className="w-8 h-8 text-orange-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">アラート</p>
                    <p className="text-2xl font-bold">{alerts.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 投資枠利用状況 */}
          {quotas && <NisaQuotaCard quotas={quotas} />}

          {/* 投資機会 */}
          {opportunities.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  投資機会
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {opportunities.map((opportunity) => (
                    <div key={opportunity.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <span className="font-medium">{opportunity.symbolName}</span>
                          <span className="text-sm text-gray-500 ml-2">({opportunity.symbol})</span>
                        </div>
                        <Badge variant="outline">
                          {opportunity.quotaRecommendation === 'GROWTH' ? '成長' : 'つみたて'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{opportunity.reason}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span>推奨投資額: ¥{opportunity.suggestedAmount.toLocaleString()}</span>
                        <span>期待リターン: {(opportunity.expectedReturn * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ポートフォリオタブ */}
        <TabsContent value="portfolio">
          {portfolio && <NisaPortfolioCard portfolio={portfolio} />}
        </TabsContent>

        {/* 取引履歴タブ */}
        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5" />
                取引履歴
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data?.transactions && data.transactions.length > 0 ? (
                <div className="space-y-3">
                  {data.transactions.map((transaction) => (
                    <div key={transaction.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge variant={transaction.type === 'BUY' ? 'default' : 'secondary'}>
                          {transaction.type === 'BUY' ? '買い' : '売り'}
                        </Badge>
                        <div>
                          <span className="font-medium">{transaction.symbolName}</span>
                          <span className="text-sm text-gray-500 ml-2">({transaction.symbol})</span>
                        </div>
                        <Badge variant="outline">
                          {transaction.quotaType === 'GROWTH' ? '成長' : 'つみたて'}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">¥{transaction.amount.toLocaleString()}</div>
                        <div className="text-sm text-gray-500">
                          {transaction.quantity}株 × ¥{transaction.price.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">取引履歴がありません</p>
                  <p className="text-sm">最初の取引を追加してください</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 設定タブ */}
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                設定
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Settings className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">設定機能</p>
                <p className="text-sm">設定機能は今後実装予定です</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
