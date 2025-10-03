'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { 
  CheckCircle, 
  Clock, 
  RefreshCw, 
  TrendingUp, 
  Shield, 
  FileText,
  AlertTriangle,
  Play,
  Pause,
  RotateCcw,
  HelpCircle
} from 'lucide-react';
import IndicatorTooltip, { StockIndicatorTooltip } from '@/components/ranking/IndicatorTooltip';

interface RoutineStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
  inProgress: boolean;
  duration?: number; // 予想時間（秒）
}

interface CandidateStock {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  reason: string;
  indicators: {
    name: string;
    value: number;
    threshold: number;
    status: 'good' | 'warning' | 'bad';
  }[];
}

interface HoldingStock {
  code: string;
  name: string;
  price: number;
  change: number;
  health: {
    earnings: 'good' | 'warning' | 'bad';
    gap: 'good' | 'warning' | 'bad';
    volume: 'good' | 'warning' | 'bad';
  };
  issues: string[];
}

interface ActionMemo {
  stockCode: string;
  action: 'buy' | 'watch' | 'skip';
  reason: string;
  timestamp: string;
}

export default function RoutineWizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<RoutineStep[]>([
    {
      id: 'update',
      title: 'データ更新',
      description: '最新の株価データを取得します',
      icon: <RefreshCw className="h-5 w-5" />,
      completed: false,
      inProgress: false,
      duration: 30
    },
    {
      id: 'candidates',
      title: '本日の買い候補',
      description: '最大5銘柄の候補を表示します',
      icon: <TrendingUp className="h-5 w-5" />,
      completed: false,
      inProgress: false,
      duration: 60
    },
    {
      id: 'holdings',
      title: '保有銘柄ヘルスチェック',
      description: '保有銘柄の状態を確認します',
      icon: <Shield className="h-5 w-5" />,
      completed: false,
      inProgress: false,
      duration: 90
    },
    {
      id: 'memo',
      title: 'アクションメモ',
      description: '今日の行動を記録します',
      icon: <FileText className="h-5 w-5" />,
      completed: false,
      inProgress: false,
      duration: 30
    }
  ]);

  const [candidates, setCandidates] = useState<CandidateStock[]>([]);
  const [holdings, setHoldings] = useState<HoldingStock[]>([]);
  const [actionMemos, setActionMemos] = useState<ActionMemo[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // 経過時間の計算
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, startTime]);

  // ステップの実行
  const executeStep = async (stepIndex: number) => {
    const step = steps[stepIndex];
    setError(null);

    // ステップを進行中に設定
    setSteps(prev => prev.map((s, i) => 
      i === stepIndex ? { ...s, inProgress: true } : s
    ));

    try {
      switch (step.id) {
        case 'update':
          await executeDataUpdate();
          break;
        case 'candidates':
          await executeCandidatesGeneration();
          break;
        case 'holdings':
          await executeHoldingsCheck();
          break;
        case 'memo':
          await executeMemoCreation();
          break;
      }

      // ステップ完了
      setSteps(prev => prev.map((s, i) => 
        i === stepIndex ? { ...s, completed: true, inProgress: false } : s
      ));

      // 次のステップへ
      if (stepIndex < steps.length - 1) {
        setCurrentStep(stepIndex + 1);
      } else {
        setIsRunning(false);
      }

    } catch (error) {
      setError(`ステップ ${step.title} でエラーが発生しました: ${error}`);
      setSteps(prev => prev.map((s, i) => 
        i === stepIndex ? { ...s, inProgress: false } : s
      ));
    }
  };

  // データ更新の実行
  const executeDataUpdate = async () => {
    try {
      const response = await fetch('/api/routine/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('データ更新に失敗しました');
      }

      const data = await response.json();
      console.log('データ更新完了:', data);
    } catch (error) {
      throw new Error(`データ更新エラー: ${error}`);
    }
  };

  // 候補生成の実行
  const executeCandidatesGeneration = async () => {
    try {
      const response = await fetch('/api/routine/candidates', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('候補生成に失敗しました');
      }

      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (error) {
      throw new Error(`候補生成エラー: ${error}`);
    }
  };

  // 保有銘柄チェックの実行
  const executeHoldingsCheck = async () => {
    try {
      const response = await fetch('/api/routine/holdings', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('保有銘柄チェックに失敗しました');
      }

      const data = await response.json();
      setHoldings(data.holdings || []);
    } catch (error) {
      throw new Error(`保有銘柄チェックエラー: ${error}`);
    }
  };

  // メモ作成の実行
  const executeMemoCreation = async () => {
    // メモ作成は既に完了しているとみなす
    console.log('メモ作成完了');
  };

  // ルーティン開始
  const startRoutine = () => {
    setIsRunning(true);
    setStartTime(new Date());
    setElapsedTime(0);
    setCurrentStep(0);
    setError(null);
    executeStep(0);
  };

  // ルーティン停止
  const stopRoutine = () => {
    setIsRunning(false);
    setStartTime(null);
  };

  // ルーティンリセット
  const resetRoutine = () => {
    setIsRunning(false);
    setStartTime(null);
    setElapsedTime(0);
    setCurrentStep(0);
    setSteps(prev => prev.map(step => ({ ...step, completed: false, inProgress: false })));
    setCandidates([]);
    setHoldings([]);
    setActionMemos([]);
    setError(null);
  };

  // アクションメモの保存
  const saveActionMemo = async (stockCode: string, action: 'buy' | 'watch' | 'skip', reason: string) => {
    const memo: ActionMemo = {
      stockCode,
      action,
      reason,
      timestamp: new Date().toISOString()
    };

    setActionMemos(prev => [...prev, memo]);

    try {
      await fetch('/api/routine/memo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(memo)
      });
    } catch (error) {
      console.error('メモ保存エラー:', error);
    }
  };

  // 完了率の計算
  const completionRate = (steps.filter(step => step.completed).length / steps.length) * 100;

  // 経過時間の表示
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">今日の5分ルーティン</h1>
        <p className="text-gray-600">毎日5分で完結する投資ルーティン</p>
      </div>

      {/* 進捗表示 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            進捗状況
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>完了率</span>
              <span className="font-semibold">{completionRate.toFixed(0)}%</span>
            </div>
            <Progress value={completionRate} className="w-full" />
            
            {isRunning && (
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>経過時間</span>
                <span className="font-mono">{formatTime(elapsedTime)}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* エラー表示 */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* ステップ表示 */}
      <div className="grid gap-4">
        {steps.map((step, index) => (
          <Card key={step.id} className={`transition-all ${
            index === currentStep ? 'ring-2 ring-blue-500' : ''
          } ${step.completed ? 'bg-green-50' : ''}`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {step.completed ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : step.inProgress ? (
                    <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
                  ) : (
                    step.icon
                  )}
                  <div>
                    <CardTitle className="text-lg">{step.title}</CardTitle>
                    <CardDescription>{step.description}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {step.completed && <Badge variant="default">完了</Badge>}
                  {step.inProgress && <Badge variant="secondary">実行中</Badge>}
                  {step.duration && (
                    <span className="text-sm text-gray-500">
                      予想: {step.duration}秒
                    </span>
                  )}
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* 制御ボタン */}
      <div className="flex justify-center gap-4">
        {!isRunning ? (
          <Button onClick={startRoutine} size="lg" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            ルーティン開始
          </Button>
        ) : (
          <Button onClick={stopRoutine} variant="outline" size="lg" className="flex items-center gap-2">
            <Pause className="h-4 w-4" />
            一時停止
          </Button>
        )}
        
        <Button onClick={resetRoutine} variant="outline" size="lg" className="flex items-center gap-2">
          <RotateCcw className="h-4 w-4" />
          リセット
        </Button>
      </div>

      {/* 候補銘柄表示 */}
      {candidates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              本日の買い候補
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {candidates.map((candidate, index) => (
                <div key={candidate.code} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold">{candidate.name} ({candidate.code})</h3>
                      <p className="text-sm text-gray-600">{candidate.reason}</p>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">¥{candidate.price.toLocaleString()}</div>
                      <div className={`text-sm ${candidate.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {candidate.change >= 0 ? '+' : ''}{candidate.change} ({candidate.changePercent.toFixed(2)}%)
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                    {candidate.indicators.map((indicator, idx) => (
                      <StockIndicatorTooltip
                        key={idx}
                        name={indicator.name}
                        value={indicator.value}
                        threshold={indicator.threshold}
                        status={indicator.status}
                      />
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      onClick={() => saveActionMemo(candidate.code, 'buy', '候補として選択')}
                    >
                      買う
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => saveActionMemo(candidate.code, 'watch', '監視対象として追加')}
                    >
                      監視
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => saveActionMemo(candidate.code, 'skip', '今回は見送り')}
                    >
                      見送り
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 保有銘柄ヘルスチェック */}
      {holdings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              保有銘柄ヘルスチェック
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {holdings.map((holding) => (
                <div key={holding.code} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold">{holding.name} ({holding.code})</h3>
                      <div className="text-sm text-gray-600">
                        価格: ¥{holding.price.toLocaleString()} 
                        <span className={`ml-2 ${holding.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {holding.change >= 0 ? '+' : ''}{holding.change}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant={holding.health.earnings === 'good' ? 'default' : 'destructive'}>
                        決算: {holding.health.earnings}
                      </Badge>
                      <Badge variant={holding.health.gap === 'good' ? 'default' : 'destructive'}>
                        ギャップ: {holding.health.gap}
                      </Badge>
                      <Badge variant={holding.health.volume === 'good' ? 'default' : 'destructive'}>
                        出来高: {holding.health.volume}
                      </Badge>
                    </div>
                  </div>
                  
                  {holding.issues.length > 0 && (
                    <div className="mt-2">
                      <div className="text-sm font-medium text-red-600 mb-1">注意事項:</div>
                      <ul className="text-sm text-red-600 list-disc list-inside">
                        {holding.issues.map((issue, idx) => (
                          <li key={idx}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* アクションメモ */}
      {actionMemos.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              アクションメモ
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {actionMemos.map((memo, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                  <Badge variant="outline">{memo.stockCode}</Badge>
                  <Badge variant={memo.action === 'buy' ? 'default' : 'secondary'}>
                    {memo.action === 'buy' ? '買う' : memo.action === 'watch' ? '監視' : '見送り'}
                  </Badge>
                  <span className="text-sm">{memo.reason}</span>
                  <span className="text-xs text-gray-500 ml-auto">
                    {new Date(memo.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
