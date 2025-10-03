'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Settings, 
  TrendingUp, 
  DollarSign, 
  Star, 
  Shield,
  AlertTriangle,
  Save,
  RotateCcw
} from 'lucide-react';

interface RankingSettingsProps {
  onConfigChange?: (config: any) => void;
}

export default function RankingSettings({ onConfigChange }: RankingSettingsProps) {
  const [config, setConfig] = useState({
    maxCandidates: 5,
    minScore: 0.6,
    rules: {
      liquidity: {
        enabled: true,
        percentile: 70
      },
      trend: {
        enabled: true,
        weeks13vs26: true,
        returnPercentile: 40
      },
      valuation: {
        enabled: true,
        pbrPercentile: 50,
        perPercentile: 40
      },
      quality: {
        enabled: true,
        roePercentile: 40
      },
      exclusions: {
        enabled: true,
        excludeNonTSE: true,
        excludeSpecialAttention: true,
        excludeEarningsDay: true,
        excludeLimitUp: true
      }
    },
    weights: {
      trend: 0.4,
      valuation: 0.3,
      quality: 0.3
    }
  });

  const [presets] = useState({
    safe: {
      name: '安全重視',
      description: 'リスクを抑えた安定投資',
      config: {
        minScore: 0.8,
        rules: {
          liquidity: { enabled: true, percentile: 80 },
          trend: { enabled: true, weeks13vs26: true, returnPercentile: 30 },
          valuation: { enabled: true, pbrPercentile: 40, perPercentile: 30 },
          quality: { enabled: true, roePercentile: 30 },
          exclusions: { enabled: true, excludeNonTSE: true, excludeSpecialAttention: true, excludeEarningsDay: true, excludeLimitUp: true }
        },
        weights: { trend: 0.3, valuation: 0.4, quality: 0.3 }
      }
    },
    standard: {
      name: '標準',
      description: 'バランスの取れた投資',
      config: {
        minScore: 0.6,
        rules: {
          liquidity: { enabled: true, percentile: 70 },
          trend: { enabled: true, weeks13vs26: true, returnPercentile: 40 },
          valuation: { enabled: true, pbrPercentile: 50, perPercentile: 40 },
          quality: { enabled: true, roePercentile: 40 },
          exclusions: { enabled: true, excludeNonTSE: true, excludeSpecialAttention: true, excludeEarningsDay: true, excludeLimitUp: true }
        },
        weights: { trend: 0.4, valuation: 0.3, quality: 0.3 }
      }
    },
    aggressive: {
      name: '攻め',
      description: '成長性を重視した投資',
      config: {
        minScore: 0.4,
        rules: {
          liquidity: { enabled: true, percentile: 60 },
          trend: { enabled: true, weeks13vs26: true, returnPercentile: 50 },
          valuation: { enabled: true, pbrPercentile: 60, perPercentile: 50 },
          quality: { enabled: true, roePercentile: 50 },
          exclusions: { enabled: true, excludeNonTSE: true, excludeSpecialAttention: false, excludeEarningsDay: false, excludeLimitUp: false }
        },
        weights: { trend: 0.5, valuation: 0.2, quality: 0.3 }
      }
    }
  });

  const [selectedPreset, setSelectedPreset] = useState<string>('standard');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // プリセット適用
  const applyPreset = (presetName: string) => {
    const preset = presets[presetName as keyof typeof presets];
    if (preset) {
      setConfig(prev => ({
        ...prev,
        ...preset.config
      }));
      setSelectedPreset(presetName);
    }
  };

  // 設定保存
  const saveConfig = async () => {
    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch('/api/ranking/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        setMessage('設定が保存されました');
        onConfigChange?.(config);
      } else {
        setMessage('設定の保存に失敗しました');
      }
    } catch (error) {
      setMessage('設定の保存中にエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  // 設定リセット
  const resetConfig = () => {
    applyPreset('standard');
    setMessage('設定をリセットしました');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">候補銘柄抽出設定</h1>
        <p className="text-gray-600">簡潔で透明なルールベースの候補抽出</p>
      </div>

      {/* プリセット選択 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            投資スタイルプリセット
          </CardTitle>
          <CardDescription>
            投資スタイルに応じて設定を自動調整します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(presets).map(([key, preset]) => (
              <Card 
                key={key} 
                className={`cursor-pointer transition-all ${
                  selectedPreset === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                }`}
                onClick={() => applyPreset(key)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">{preset.name}</h3>
                    {selectedPreset === key && (
                      <Badge variant="default">選択中</Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{preset.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ルール設定 */}
      <div className="grid gap-6">
        {/* 流動性ルール */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              流動性ルール
            </CardTitle>
            <CardDescription>
              前日出来高による流動性チェック
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">流動性チェック</div>
                <div className="text-sm text-gray-600">前日出来高が上位{config.rules.liquidity.percentile}%分位以上</div>
              </div>
              <Switch
                checked={config.rules.liquidity.enabled}
                onCheckedChange={(checked) => 
                  setConfig(prev => ({
                    ...prev,
                    rules: {
                      ...prev.rules,
                      liquidity: { ...prev.rules.liquidity, enabled: checked }
                    }
                  }))
                }
              />
            </div>
            {config.rules.liquidity.enabled && (
              <div>
                <label className="text-sm font-medium">分位値: {config.rules.liquidity.percentile}%</label>
                <Slider
                  value={[config.rules.liquidity.percentile]}
                  onValueChange={([value]) => 
                    setConfig(prev => ({
                      ...prev,
                      rules: {
                        ...prev.rules,
                        liquidity: { ...prev.rules.liquidity, percentile: value }
                      }
                    }))
                  }
                  min={50}
                  max={90}
                  step={5}
                  className="mt-2"
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* トレンドルール */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              トレンドルール
            </CardTitle>
            <CardDescription>
              移動平均とリターンによるトレンド分析
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">トレンド分析</div>
                <div className="text-sm text-gray-600">13週＞26週、直近20営業日リターン上位{config.rules.trend.returnPercentile}%</div>
              </div>
              <Switch
                checked={config.rules.trend.enabled}
                onCheckedChange={(checked) => 
                  setConfig(prev => ({
                    ...prev,
                    rules: {
                      ...prev.rules,
                      trend: { ...prev.rules.trend, enabled: checked }
                    }
                  }))
                }
              />
            </div>
            {config.rules.trend.enabled && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">13週移動平均＞26週移動平均</span>
                  <Switch
                    checked={config.rules.trend.weeks13vs26}
                    onCheckedChange={(checked) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          trend: { ...prev.rules.trend, weeks13vs26: checked }
                        }
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">リターン分位値: {config.rules.trend.returnPercentile}%</label>
                  <Slider
                    value={[config.rules.trend.returnPercentile]}
                    onValueChange={([value]) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          trend: { ...prev.rules.trend, returnPercentile: value }
                        }
                      }))
                    }
                    min={20}
                    max={60}
                    step={5}
                    className="mt-2"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* バリュエーションルール */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              バリュエーションルール
            </CardTitle>
            <CardDescription>
              PBR・PERによるバリュー分析
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">バリュー分析</div>
                <div className="text-sm text-gray-600">PBR市場中央値以下、PER分位下位{config.rules.valuation.perPercentile}%</div>
              </div>
              <Switch
                checked={config.rules.valuation.enabled}
                onCheckedChange={(checked) => 
                  setConfig(prev => ({
                    ...prev,
                    rules: {
                      ...prev.rules,
                      valuation: { ...prev.rules.valuation, enabled: checked }
                    }
                  }))
                }
              />
            </div>
            {config.rules.valuation.enabled && (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">PBR分位値: {config.rules.valuation.pbrPercentile}%</label>
                  <Slider
                    value={[config.rules.valuation.pbrPercentile]}
                    onValueChange={([value]) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          valuation: { ...prev.rules.valuation, pbrPercentile: value }
                        }
                      }))
                    }
                    min={30}
                    max={70}
                    step={5}
                    className="mt-2"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">PER分位値: {config.rules.valuation.perPercentile}%</label>
                  <Slider
                    value={[config.rules.valuation.perPercentile]}
                    onValueChange={([value]) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          valuation: { ...prev.rules.valuation, perPercentile: value }
                        }
                      }))
                    }
                    min={20}
                    max={60}
                    step={5}
                    className="mt-2"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* クオリティルール */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              クオリティルール
            </CardTitle>
            <CardDescription>
              ROEによるクオリティ分析
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">クオリティ分析</div>
                <div className="text-sm text-gray-600">ROEが上位{config.rules.quality.roePercentile}%</div>
              </div>
              <Switch
                checked={config.rules.quality.enabled}
                onCheckedChange={(checked) => 
                  setConfig(prev => ({
                    ...prev,
                    rules: {
                      ...prev.rules,
                      quality: { ...prev.rules.quality, enabled: checked }
                    }
                  }))
                }
              />
            </div>
            {config.rules.quality.enabled && (
              <div>
                <label className="text-sm font-medium">ROE分位値: {config.rules.quality.roePercentile}%</label>
                <Slider
                  value={[config.rules.quality.roePercentile]}
                  onValueChange={([value]) => 
                    setConfig(prev => ({
                      ...prev,
                      rules: {
                        ...prev.rules,
                        quality: { ...prev.rules.quality, roePercentile: value }
                      }
                    }))
                  }
                  min={20}
                  max={60}
                  step={5}
                  className="mt-2"
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* 除外条件 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              除外条件
            </CardTitle>
            <CardDescription>
              リスクを避けるための除外条件
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">除外条件適用</div>
                <div className="text-sm text-gray-600">リスクの高い銘柄を除外</div>
              </div>
              <Switch
                checked={config.rules.exclusions.enabled}
                onCheckedChange={(checked) => 
                  setConfig(prev => ({
                    ...prev,
                    rules: {
                      ...prev.rules,
                      exclusions: { ...prev.rules.exclusions, enabled: checked }
                    }
                  }))
                }
              />
            </div>
            {config.rules.exclusions.enabled && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">東証以外を除外</span>
                  <Switch
                    checked={config.rules.exclusions.excludeNonTSE}
                    onCheckedChange={(checked) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          exclusions: { ...prev.rules.exclusions, excludeNonTSE: checked }
                        }
                      }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">特別注意銘柄を除外</span>
                  <Switch
                    checked={config.rules.exclusions.excludeSpecialAttention}
                    onCheckedChange={(checked) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          exclusions: { ...prev.rules.exclusions, excludeSpecialAttention: checked }
                        }
                      }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">決算当日を除外</span>
                  <Switch
                    checked={config.rules.exclusions.excludeEarningsDay}
                    onCheckedChange={(checked) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          exclusions: { ...prev.rules.exclusions, excludeEarningsDay: checked }
                        }
                      }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">ストップ高直後を除外</span>
                  <Switch
                    checked={config.rules.exclusions.excludeLimitUp}
                    onCheckedChange={(checked) => 
                      setConfig(prev => ({
                        ...prev,
                        rules: {
                          ...prev.rules,
                          exclusions: { ...prev.rules.exclusions, excludeLimitUp: checked }
                        }
                      }))
                    }
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 重み付け */}
        <Card>
          <CardHeader>
            <CardTitle>スコア重み付け</CardTitle>
            <CardDescription>
              トレンド・バリュー・クオリティの重み付け
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">トレンド: {Math.round(config.weights.trend * 100)}%</label>
              <Slider
                value={[config.weights.trend]}
                onValueChange={([value]) => {
                  const remaining = 1 - value;
                  const valuation = Math.min(config.weights.valuation, remaining * 0.8);
                  const quality = remaining - valuation;
                  setConfig(prev => ({
                    ...prev,
                    weights: { trend: value, valuation, quality }
                  }));
                }}
                min={0.1}
                max={0.7}
                step={0.05}
                className="mt-2"
              />
            </div>
            <div>
              <label className="text-sm font-medium">バリュー: {Math.round(config.weights.valuation * 100)}%</label>
              <Slider
                value={[config.weights.valuation]}
                onValueChange={([value]) => {
                  const remaining = 1 - config.weights.trend;
                  const quality = remaining - value;
                  setConfig(prev => ({
                    ...prev,
                    weights: { ...prev.weights, valuation: value, quality }
                  }));
                }}
                min={0.1}
                max={0.7}
                step={0.05}
                className="mt-2"
              />
            </div>
            <div>
              <label className="text-sm font-medium">クオリティ: {Math.round(config.weights.quality * 100)}%</label>
              <Slider
                value={[config.weights.quality]}
                onValueChange={([value]) => {
                  const remaining = 1 - config.weights.trend;
                  const valuation = remaining - value;
                  setConfig(prev => ({
                    ...prev,
                    weights: { ...prev.weights, valuation, quality: value }
                  }));
                }}
                min={0.1}
                max={0.7}
                step={0.05}
                className="mt-2"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* メッセージ表示 */}
      {message && (
        <Alert className={message.includes('失敗') || message.includes('エラー') ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* アクションボタン */}
      <div className="flex justify-center gap-4">
        <Button onClick={saveConfig} disabled={isLoading} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {isLoading ? '保存中...' : '設定保存'}
        </Button>
        <Button onClick={resetConfig} variant="outline" className="flex items-center gap-2">
          <RotateCcw className="h-4 w-4" />
          リセット
        </Button>
      </div>
    </div>
  );
}
