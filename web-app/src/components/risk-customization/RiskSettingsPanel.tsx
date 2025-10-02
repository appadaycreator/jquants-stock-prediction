/**
 * リスク管理カスタマイズ設定パネル
 */

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Shield, 
  Target, 
  AlertTriangle, 
  TrendingUp, 
  Settings, 
  Save, 
  RotateCcw,
  Info,
} from "lucide-react";
import { useRiskCustomization } from "@/hooks/useRiskCustomization";
// risk-customization-store は削除され、統合設定管理を使用
// 一時的にローカル状態管理に変更
interface RiskCustomizationSettings {
  riskTolerance: {
    maxDrawdown: number;
    volatilityTolerance: number;
    varTolerance: number;
  };
  targetReturn: {
    annual: number;
    monthly: number;
    riskAdjusted: boolean;
  };
  notifications: {
    riskAlerts: boolean;
    returnAlerts: boolean;
    drawdownAlerts: boolean;
  };
  display: {
    showRiskMetrics: boolean;
    showReturnMetrics: boolean;
    showAlerts: boolean;
  };
}

const riskCustomizationStore = {
  getSettings: () => {
    const stored = localStorage.getItem("risk-customization");
    return stored ? JSON.parse(stored) : {
      riskTolerance: { maxDrawdown: 0.1, volatilityTolerance: 0.2, varTolerance: 0.05 },
      targetReturn: { annual: 0.08, monthly: 0.006, riskAdjusted: true },
      notifications: { riskAlerts: true, returnAlerts: true, drawdownAlerts: true },
      display: { showRiskMetrics: true, showReturnMetrics: true, showAlerts: true },
    };
  },
};

interface RiskSettingsPanelProps {
  onClose?: () => void;
}

export function RiskSettingsPanel({ onClose }: RiskSettingsPanelProps) {
  const {
    settings,
    isLoading,
    updateSettings,
    resetSettings,
    getRiskThresholds,
    getReturnTargets,
  } = useRiskCustomization();

  const [localSettings, setLocalSettings] = useState<RiskCustomizationSettings>(settings);
  const [hasChanges, setHasChanges] = useState(false);

  // 設定変更の検知
  React.useEffect(() => {
    const hasLocalChanges = JSON.stringify(localSettings) !== JSON.stringify(settings);
    setHasChanges(hasLocalChanges);
  }, [localSettings, settings]);

  // 設定を保存
  const handleSave = () => {
    updateSettings(localSettings);
    setHasChanges(false);
  };

  // 設定をリセット
  const handleReset = () => {
    setLocalSettings(settings);
    setHasChanges(false);
  };

  // デフォルトに戻す
  const handleResetToDefault = () => {
    resetSettings();
    setLocalSettings(riskCustomizationStore.getSettings());
    setHasChanges(false);
  };

  // リスク許容度の更新
  const updateRiskTolerance = (field: keyof RiskCustomizationSettings["riskTolerance"], value: any) => {
    setLocalSettings(prev => ({
      ...prev,
      riskTolerance: {
        ...prev.riskTolerance,
        [field]: value,
      },
    }));
  };

  // 目標リターンの更新
  const updateTargetReturn = (field: keyof RiskCustomizationSettings["targetReturn"], value: any) => {
    setLocalSettings(prev => ({
      ...prev,
      targetReturn: {
        ...prev.targetReturn,
        [field]: value,
      },
    }));
  };

  // 通知設定の更新
  const updateNotifications = (field: keyof RiskCustomizationSettings["notifications"], value: boolean) => {
    setLocalSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [field]: value,
      },
    }));
  };

  // 表示設定の更新
  const updateDisplay = (field: keyof RiskCustomizationSettings["display"], value: boolean) => {
    setLocalSettings(prev => ({
      ...prev,
      display: {
        ...prev.display,
        [field]: value,
      },
    }));
  };

  // リスクレベルの説明
  const getRiskLevelDescription = (level: string) => {
    const descriptions = {
      "VERY_LOW": "非常に保守的 - 元本保護重視",
      "LOW": "保守的 - 安定した成長を重視",
      "MEDIUM": "バランス型 - リスクとリターンのバランス",
      "HIGH": "積極的 - 高いリターンを追求",
      "VERY_HIGH": "非常に積極的 - 高リスク高リターン",
      "CRITICAL": "極めて積極的 - 最大限のリターン追求",
    };
    return descriptions[level as keyof typeof descriptions] || "";
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-600" />
          <h2 className="text-xl font-semibold">リスク管理設定</h2>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={!hasChanges}
          >
            <RotateCcw className="h-4 w-4 mr-1" />
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
        </div>
      </div>

      {/* 許容リスクレベル設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            許容リスクレベル
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* リスクレベル選択 */}
          <div className="space-y-2">
            <Label htmlFor="risk-level">リスクレベル</Label>
            <Select
              value={localSettings.riskTolerance.level}
              onValueChange={(value) => updateRiskTolerance("level", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="VERY_LOW">非常に低い</SelectItem>
                <SelectItem value="LOW">低い</SelectItem>
                <SelectItem value="MEDIUM">中程度</SelectItem>
                <SelectItem value="HIGH">高い</SelectItem>
                <SelectItem value="VERY_HIGH">非常に高い</SelectItem>
                <SelectItem value="CRITICAL">極めて高い</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-gray-600">
              {getRiskLevelDescription(localSettings.riskTolerance.level)}
            </p>
          </div>

          {/* 最大ドローダウン許容値 */}
          <div className="space-y-2">
            <Label>最大ドローダウン許容値: {(localSettings.riskTolerance.maxDrawdown * 100).toFixed(1)}%</Label>
            <Slider
              value={[localSettings.riskTolerance.maxDrawdown * 100]}
              onValueChange={([value]) => updateRiskTolerance("maxDrawdown", value / 100)}
              max={50}
              min={1}
              step={0.5}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1%</span>
              <span>50%</span>
            </div>
          </div>

          {/* ボラティリティ許容値 */}
          <div className="space-y-2">
            <Label>ボラティリティ許容値: {(localSettings.riskTolerance.volatilityTolerance * 100).toFixed(1)}%</Label>
            <Slider
              value={[localSettings.riskTolerance.volatilityTolerance * 100]}
              onValueChange={([value]) => updateRiskTolerance("volatilityTolerance", value / 100)}
              max={100}
              min={5}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>5%</span>
              <span>100%</span>
            </div>
          </div>

          {/* VaR許容値 */}
          <div className="space-y-2">
            <Label>VaR許容値: {(localSettings.riskTolerance.varTolerance * 100).toFixed(1)}%</Label>
            <Slider
              value={[localSettings.riskTolerance.varTolerance * 100]}
              onValueChange={([value]) => updateRiskTolerance("varTolerance", value / 100)}
              max={20}
              min={1}
              step={0.5}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1%</span>
              <span>20%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 目標リターン設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-green-600" />
            目標リターン
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 年間目標リターン */}
          <div className="space-y-2">
            <Label htmlFor="annual-return">年間目標リターン (%)</Label>
            <Input
              id="annual-return"
              type="number"
              value={localSettings.targetReturn.annual * 100}
              onChange={(e) => updateTargetReturn("annual", parseFloat(e.target.value) / 100)}
              min={0}
              max={100}
              step={0.1}
            />
          </div>

          {/* 月間目標リターン */}
          <div className="space-y-2">
            <Label htmlFor="monthly-return">月間目標リターン (%)</Label>
            <Input
              id="monthly-return"
              type="number"
              value={localSettings.targetReturn.monthly * 100}
              onChange={(e) => updateTargetReturn("monthly", parseFloat(e.target.value) / 100)}
              min={0}
              max={20}
              step={0.1}
            />
          </div>

          {/* リスク調整後リターン使用 */}
          <div className="flex items-center space-x-2">
            <Switch
              id="risk-adjusted"
              checked={localSettings.targetReturn.riskAdjusted}
              onCheckedChange={(checked) => updateTargetReturn("riskAdjusted", checked)}
            />
            <Label htmlFor="risk-adjusted">リスク調整後リターンを使用</Label>
          </div>
        </CardContent>
      </Card>

      {/* 通知設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-purple-600" />
            通知設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="target-price-notification">目標価格到達通知</Label>
              <Switch
                id="target-price-notification"
                checked={localSettings.notifications.targetPriceReached}
                onCheckedChange={(checked) => updateNotifications("targetPriceReached", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="stop-loss-notification">損切ライン到達通知</Label>
              <Switch
                id="stop-loss-notification"
                checked={localSettings.notifications.stopLossTriggered}
                onCheckedChange={(checked) => updateNotifications("stopLossTriggered", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="risk-level-notification">リスクレベル変更通知</Label>
              <Switch
                id="risk-level-notification"
                checked={localSettings.notifications.riskLevelChanged}
                onCheckedChange={(checked) => updateNotifications("riskLevelChanged", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="daily-summary-notification">日次サマリー通知</Label>
              <Switch
                id="daily-summary-notification"
                checked={localSettings.notifications.dailySummary}
                onCheckedChange={(checked) => updateNotifications("dailySummary", checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 表示設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-600" />
            表示設定
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="show-risk-details">リスク詳細表示</Label>
              <Switch
                id="show-risk-details"
                checked={localSettings.display.showRiskDetails}
                onCheckedChange={(checked) => updateDisplay("showRiskDetails", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="show-recommendation-reasons">推奨理由表示</Label>
              <Switch
                id="show-recommendation-reasons"
                checked={localSettings.display.showRecommendationReasons}
                onCheckedChange={(checked) => updateDisplay("showRecommendationReasons", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="show-technical-indicators">テクニカル指標表示</Label>
              <Switch
                id="show-technical-indicators"
                checked={localSettings.display.showTechnicalIndicators}
                onCheckedChange={(checked) => updateDisplay("showTechnicalIndicators", checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="show-sentiment-analysis">センチメント分析表示</Label>
              <Switch
                id="show-sentiment-analysis"
                checked={localSettings.display.showSentimentAnalysis}
                onCheckedChange={(checked) => updateDisplay("showSentimentAnalysis", checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 現在の設定サマリー */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            設定サマリー
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <Badge variant="outline" className="mb-2">
                リスクレベル: {localSettings.riskTolerance.level}
              </Badge>
              <p className="text-gray-600">
                最大ドローダウン: {(localSettings.riskTolerance.maxDrawdown * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <Badge variant="outline" className="mb-2">
                目標リターン: {(localSettings.targetReturn.annual * 100).toFixed(1)}%
              </Badge>
              <p className="text-gray-600">
                リスク調整: {localSettings.targetReturn.riskAdjusted ? "有効" : "無効"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* アクションボタン */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleResetToDefault}
          disabled={isLoading}
        >
          デフォルトに戻す
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
