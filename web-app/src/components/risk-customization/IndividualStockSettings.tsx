/**
 * 個別銘柄設定コンポーネント
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Target, 
  AlertTriangle, 
  Settings, 
  Save, 
  X,
  Plus,
  Trash2,
  Bell,
  Shield
} from 'lucide-react';
import { useRiskCustomization } from '@/hooks/useRiskCustomization';

interface IndividualStockSettingsProps {
  symbol: string;
  currentPrice?: number;
  onClose?: () => void;
}

export function IndividualStockSettings({ 
  symbol, 
  currentPrice = 0, 
  onClose 
}: IndividualStockSettingsProps) {
  const {
    settings,
    isLoading,
    updateIndividualStockSettings,
    removeIndividualStockSettings,
    getIndividualStockSettings,
  } = useRiskCustomization();

  const stockSettings = getIndividualStockSettings(symbol) || {
    targetPrice: undefined,
    stopLossPrice: undefined,
    maxPositionSize: undefined,
    riskLevel: 'MEDIUM' as const,
    notificationEnabled: true,
  };

  const [localSettings, setLocalSettings] = useState(stockSettings);
  const [hasChanges, setHasChanges] = useState(false);

  // 設定変更の検知
  React.useEffect(() => {
    const hasLocalChanges = JSON.stringify(localSettings) !== JSON.stringify(stockSettings);
    setHasChanges(hasLocalChanges);
  }, [localSettings, stockSettings]);

  // 設定を保存
  const handleSave = () => {
    updateIndividualStockSettings(symbol, localSettings);
    setHasChanges(false);
  };

  // 設定を削除
  const handleDelete = () => {
    removeIndividualStockSettings(symbol);
    if (onClose) onClose();
  };

  // 設定をリセット
  const handleReset = () => {
    setLocalSettings(stockSettings);
    setHasChanges(false);
  };

  // 設定の更新
  const updateSetting = (field: keyof typeof localSettings, value: any) => {
    setLocalSettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // 目標価格の計算（現在価格から）
  const calculateTargetPrice = (percentage: number) => {
    return currentPrice * (1 + percentage / 100);
  };

  // 損切ラインの計算（現在価格から）
  const calculateStopLoss = (percentage: number) => {
    return currentPrice * (1 - percentage / 100);
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-600" />
          <h2 className="text-xl font-semibold">{symbol} 個別設定</h2>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={!hasChanges}
          >
            変更を破棄
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
          >
            <Save className="h-4 w-4 mr-1" />
            保存
          </Button>
          {onClose && (
            <Button variant="outline" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 現在価格情報 */}
      {currentPrice > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            現在価格: ¥{currentPrice.toLocaleString()}
          </AlertDescription>
        </Alert>
      )}

      {/* 目標価格設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-green-600" />
            目標価格設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="target-price">目標価格 (¥)</Label>
            <Input
              id="target-price"
              type="number"
              value={localSettings.targetPrice || ''}
              onChange={(e) => updateSetting('targetPrice', parseFloat(e.target.value) || undefined)}
              placeholder="例: 5000"
            />
            {currentPrice > 0 && localSettings.targetPrice && (
              <p className="text-sm text-gray-600">
                上昇率: {(((localSettings.targetPrice - currentPrice) / currentPrice) * 100).toFixed(2)}%
              </p>
            )}
          </div>

          {/* クイック設定ボタン */}
          {currentPrice > 0 && (
            <div className="space-y-2">
              <Label>クイック設定</Label>
              <div className="flex gap-2 flex-wrap">
                {[5, 10, 15, 20, 25].map(percentage => (
                  <Button
                    key={percentage}
                    variant="outline"
                    size="sm"
                    onClick={() => updateSetting('targetPrice', calculateTargetPrice(percentage))}
                  >
                    +{percentage}%
                  </Button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 損切ライン設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            損切ライン設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="stop-loss-price">損切価格 (¥)</Label>
            <Input
              id="stop-loss-price"
              type="number"
              value={localSettings.stopLossPrice || ''}
              onChange={(e) => updateSetting('stopLossPrice', parseFloat(e.target.value) || undefined)}
              placeholder="例: 4000"
            />
            {currentPrice > 0 && localSettings.stopLossPrice && (
              <p className="text-sm text-gray-600">
                下落率: {(((currentPrice - localSettings.stopLossPrice) / currentPrice) * 100).toFixed(2)}%
              </p>
            )}
          </div>

          {/* クイック設定ボタン */}
          {currentPrice > 0 && (
            <div className="space-y-2">
              <Label>クイック設定</Label>
              <div className="flex gap-2 flex-wrap">
                {[5, 10, 15, 20, 25].map(percentage => (
                  <Button
                    key={percentage}
                    variant="outline"
                    size="sm"
                    onClick={() => updateSetting('stopLossPrice', calculateStopLoss(percentage))}
                  >
                    -{percentage}%
                  </Button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ポジションサイズ設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-purple-600" />
            ポジションサイズ設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="max-position-size">最大ポジションサイズ (株数)</Label>
            <Input
              id="max-position-size"
              type="number"
              value={localSettings.maxPositionSize || ''}
              onChange={(e) => updateSetting('maxPositionSize', parseInt(e.target.value) || undefined)}
              placeholder="例: 100"
            />
          </div>
        </CardContent>
      </Card>

      {/* リスクレベル設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-orange-600" />
            リスクレベル設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="risk-level">リスクレベル</Label>
            <Select
              value={localSettings.riskLevel}
              onValueChange={(value) => updateSetting('riskLevel', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="LOW">低い</SelectItem>
                <SelectItem value="MEDIUM">中程度</SelectItem>
                <SelectItem value="HIGH">高い</SelectItem>
                <SelectItem value="CRITICAL">極めて高い</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 通知設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-indigo-600" />
            通知設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="notification-enabled">通知を有効にする</Label>
            <Switch
              id="notification-enabled"
              checked={localSettings.notificationEnabled}
              onCheckedChange={(checked) => updateSetting('notificationEnabled', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* 設定サマリー */}
      <Card>
        <CardHeader>
          <CardTitle>設定サマリー</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            {localSettings.targetPrice && (
              <div className="flex justify-between">
                <span>目標価格:</span>
                <Badge variant="outline">¥{localSettings.targetPrice.toLocaleString()}</Badge>
              </div>
            )}
            {localSettings.stopLossPrice && (
              <div className="flex justify-between">
                <span>損切ライン:</span>
                <Badge variant="outline">¥{localSettings.stopLossPrice.toLocaleString()}</Badge>
              </div>
            )}
            {localSettings.maxPositionSize && (
              <div className="flex justify-between">
                <span>最大ポジション:</span>
                <Badge variant="outline">{localSettings.maxPositionSize}株</Badge>
              </div>
            )}
            <div className="flex justify-between">
              <span>リスクレベル:</span>
              <Badge variant="outline">{localSettings.riskLevel}</Badge>
            </div>
            <div className="flex justify-between">
              <span>通知:</span>
              <Badge variant={localSettings.notificationEnabled ? "default" : "secondary"}>
                {localSettings.notificationEnabled ? '有効' : '無効'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* アクションボタン */}
      <div className="flex justify-between">
        <Button
          variant="destructive"
          onClick={handleDelete}
          disabled={isLoading}
        >
          <Trash2 className="h-4 w-4 mr-1" />
          設定を削除
        </Button>
        {onClose && (
          <Button variant="outline" onClick={onClose}>
            閉じる
          </Button>
        )}
      </div>
    </div>
  );
}
