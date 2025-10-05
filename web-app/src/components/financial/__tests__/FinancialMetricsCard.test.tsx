/**
 * 財務指標カードコンポーネントのテスト
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import { FinancialMetricsCard } from "../FinancialMetricsCard";
import { FinancialMetrics } from "@/lib/financial/types";

describe("FinancialMetricsCard", () => {
  const mockMetrics: FinancialMetrics = {
    profitability: {
      roe: 15.5,
      roeRanking: 10,
      roeTrend: "improving",
      roeScore: 85,
      roa: 8.2,
      roaRanking: 15,
      roaTrend: "stable",
      roaScore: 75,
      profitMargin: 12.3,
      profitMarginRanking: 8,
      profitMarginTrend: "improving",
      profitMarginScore: 90,
    },
    marketValuation: {
      per: 18.5,
      perRanking: 20,
      perStatus: "fair",
      perScore: 70,
      pbr: 1.8,
      pbrRanking: 25,
      pbrStatus: "fair",
      pbrScore: 65,
      psr: 2.1,
      psrRanking: 18,
      psrStatus: "fair",
      psrScore: 70,
    },
    safety: {
      equityRatio: 45.2,
      equityRatioRanking: 12,
      equityRatioStatus: "good",
      equityRatioScore: 80,
      currentRatio: 180.5,
      currentRatioRanking: 8,
      currentRatioStatus: "excellent",
      currentRatioScore: 95,
      quickRatio: 120.3,
      quickRatioRanking: 15,
      quickRatioStatus: "good",
      quickRatioScore: 85,
    },
    growth: {
      revenueGrowthRate: 18.5,
      revenueGrowthRanking: 5,
      revenueGrowthTrend: "accelerating",
      revenueGrowthScore: 95,
      profitGrowthRate: 22.3,
      profitGrowthRanking: 3,
      profitGrowthTrend: "accelerating",
      profitGrowthScore: 98,
      assetGrowthRate: 15.2,
      assetGrowthRanking: 7,
      assetGrowthTrend: "stable",
      assetGrowthScore: 88,
    },
  };

  it("財務指標を正しく表示する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} />);
    
    // 収益性指標の表示確認
    expect(screen.getByText("ROE")).toBeInTheDocument();
    expect(screen.getByText("15.50%")).toBeInTheDocument();
    expect(screen.getAllByText("#10")[0]).toBeInTheDocument();
    
    expect(screen.getByText("ROA")).toBeInTheDocument();
    expect(screen.getByText("8.20%")).toBeInTheDocument();
    expect(screen.getAllByText("#15")[0]).toBeInTheDocument();
    
    expect(screen.getByText("売上高利益率")).toBeInTheDocument();
    expect(screen.getByText("12.30%")).toBeInTheDocument();
    expect(screen.getAllByText("#8")[0]).toBeInTheDocument();
  });

  it("市場評価指標を正しく表示する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} />);
    
    expect(screen.getByText("PER")).toBeInTheDocument();
    expect(screen.getByText("18.50")).toBeInTheDocument();
    expect(screen.getAllByText("#20")[0]).toBeInTheDocument();
    
    expect(screen.getByText("PBR")).toBeInTheDocument();
    expect(screen.getByText("1.80")).toBeInTheDocument();
    expect(screen.getAllByText("#25")[0]).toBeInTheDocument();
    
    expect(screen.getByText("PSR")).toBeInTheDocument();
    expect(screen.getByText("2.10")).toBeInTheDocument();
    expect(screen.getAllByText("#18")[0]).toBeInTheDocument();
  });

  it("安全性指標を正しく表示する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} />);
    
    expect(screen.getByText("自己資本比率")).toBeInTheDocument();
    expect(screen.getByText("45.20%")).toBeInTheDocument();
    expect(screen.getAllByText("#12")[0]).toBeInTheDocument();
    
    expect(screen.getByText("流動比率")).toBeInTheDocument();
    expect(screen.getByText("180.50%")).toBeInTheDocument();
    expect(screen.getAllByText("#8")[0]).toBeInTheDocument();
    
    expect(screen.getByText("当座比率")).toBeInTheDocument();
    expect(screen.getByText("120.30%")).toBeInTheDocument();
    expect(screen.getAllByText("#15")[0]).toBeInTheDocument();
  });

  it("成長性指標を正しく表示する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} />);
    
    expect(screen.getByText("売上高成長率")).toBeInTheDocument();
    expect(screen.getByText("18.50%")).toBeInTheDocument();
    expect(screen.getAllByText("#5")[0]).toBeInTheDocument();
    
    expect(screen.getByText("利益成長率")).toBeInTheDocument();
    expect(screen.getByText("22.30%")).toBeInTheDocument();
    expect(screen.getAllByText("#3")[0]).toBeInTheDocument();
    
    expect(screen.getByText("資産成長率")).toBeInTheDocument();
    expect(screen.getByText("15.20%")).toBeInTheDocument();
    expect(screen.getAllByText("#7")[0]).toBeInTheDocument();
  });

  it("カスタムタイトルを正しく表示する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} title="カスタム財務指標" />);
    
    expect(screen.getByText("カスタム財務指標")).toBeInTheDocument();
  });

  it("カスタムクラス名を正しく適用する", () => {
    const { container } = render(
      <FinancialMetricsCard metrics={mockMetrics} className="custom-class" />,
    );
    
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("レスポンシブレイアウトを正しく適用する", () => {
    render(<FinancialMetricsCard metrics={mockMetrics} />);
    
    const gridContainer = screen.getByText("収益性指標").closest(".grid");
    expect(gridContainer).toHaveClass("grid-cols-1", "md:grid-cols-2", "lg:grid-cols-4");
  });
});
