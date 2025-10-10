import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ArrowUp,
  ArrowDown,
  Minus,
  Target,
  Shield,
} from "lucide-react";
import EnhancedTooltip from "../EnhancedTooltip";

interface SimpleDashboardCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export const SimpleDashboardCard: React.FC<SimpleDashboardCardProps> = ({
  title,
  children,
  className = "",
}) => {
  return (
    <Card className={`border-l-4 border-l-blue-500 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
};

interface RecommendationCardProps {
  recommendation: {
    id: string;
    symbol: string;
    symbolName: string;
    action: "BUY" | "SELL" | "HOLD";
    reason: string;
    confidence: number;
    expectedReturn: number;
    priority: "HIGH" | "MEDIUM" | "LOW";
    timeframe: string;
  };
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
}) => {
  const getActionIcon = (action: string) => {
    switch (action) {
      case "BUY":
        return <ArrowUp className="h-4 w-4 text-green-600" />;
      case "SELL":
        return <ArrowDown className="h-4 w-4 text-red-600" />;
      case "HOLD":
        return <Minus className="h-4 w-4 text-gray-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "BUY":
        return "bg-green-100 text-green-800 border-green-200";
      case "SELL":
        return "bg-red-100 text-red-800 border-red-200";
      case "HOLD":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "HIGH":
        return "bg-red-100 text-red-800";
      case "MEDIUM":
        return "bg-yellow-100 text-yellow-800";
      case "LOW":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? "+" : ""}${percent.toFixed(1)}%`;
  };

  return (
    <Card className="border-l-4 border-l-blue-500">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            {recommendation.symbolName}
          </CardTitle>
          <Badge className={getActionColor(recommendation.action)}>
            {getActionIcon(recommendation.action)}
            <span className="ml-1">{recommendation.action}</span>
          </Badge>
        </div>
        <p className="text-sm text-gray-600">{recommendation.symbol}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-gray-600 mb-1">理由</p>
            <p className="text-sm">{recommendation.reason}</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">信頼度</p>
              <p className="text-sm font-medium">{recommendation.confidence}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">期待リターン</p>
              <p className="text-sm font-medium">
                {formatPercent(recommendation.expectedReturn)}
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <Badge className={getPriorityColor(recommendation.priority)}>
              {recommendation.priority}
            </Badge>
            <span className="text-xs text-gray-500">{recommendation.timeframe}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface PortfolioSummaryCardProps {
  summary: {
    totalInvestment: number;
    currentValue: number;
    unrealizedPnL: number;
    unrealizedPnLPercent: number;
    bestPerformer: {
      symbol: string;
      symbolName: string;
      return: number;
    };
    worstPerformer: {
      symbol: string;
      symbolName: string;
      return: number;
    };
  };
}

export const PortfolioSummaryCard: React.FC<PortfolioSummaryCardProps> = ({
  summary,
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? "+" : ""}${percent.toFixed(1)}%`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">総投資額</p>
              <EnhancedTooltip
                content="これまでに投資した総金額です。株式の購入代金、手数料、税金などを含む実際の投資コストの合計です。例：100万円の株式を購入した場合、手数料1,000円、税金500円を含めて1,001,500円が総投資額となります。"
                type="info"
              >
                <p className="text-2xl font-bold cursor-help">
                  {formatCurrency(summary.totalInvestment)}
                </p>
              </EnhancedTooltip>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">現在価値</p>
              <EnhancedTooltip
                content="現在の市場価格で評価した保有株式の総額です。実際に売却した場合の概算価値となります。例：100万円で購入した株式が現在120万円の価値になっている場合、現在価値は120万円となります。"
                type="success"
              >
                <p className="text-2xl font-bold cursor-help">
                  {formatCurrency(summary.currentValue)}
                </p>
              </EnhancedTooltip>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            {summary.unrealizedPnL >= 0 ? (
              <TrendingUp className="h-8 w-8 text-green-600" />
            ) : (
              <TrendingDown className="h-8 w-8 text-red-600" />
            )}
            <div className="ml-4">
              <p className="text-sm text-gray-600">未実現損益</p>
              <EnhancedTooltip
                content="現在価値から総投資額を引いた未実現損益です。プラスは利益、マイナスは損失を示します。実際に売却するまで確定しません。例：100万円で購入した株式が現在120万円の価値の場合、未実現損益は+20万円となります。"
                type={summary.unrealizedPnL >= 0 ? "success" : "warning"}
              >
                <p className={`text-2xl font-bold cursor-help ${
                  summary.unrealizedPnL >= 0 ? "text-green-600" : "text-red-600"
                }`}>
                  {formatCurrency(summary.unrealizedPnL)}
                </p>
              </EnhancedTooltip>
              <EnhancedTooltip
                content="総投資額に対する損益の割合です。投資効率を測る重要な指標で、年率換算で比較することが一般的です。例：100万円の投資で20万円の利益の場合、損益率は+20%となります。"
                type={summary.unrealizedPnLPercent >= 0 ? "success" : "warning"}
              >
                <p className={`text-sm cursor-help ${
                  summary.unrealizedPnLPercent >= 0 ? "text-green-600" : "text-red-600"
                }`}>
                  {formatPercent(summary.unrealizedPnLPercent)}
                </p>
              </EnhancedTooltip>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <Shield className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">ベストパフォーマー</p>
              <p className="text-sm font-medium">
                {summary.bestPerformer.symbolName}
              </p>
              <p className="text-sm text-green-600">
                {formatPercent(summary.bestPerformer.return)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
