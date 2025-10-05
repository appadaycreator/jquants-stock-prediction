/**
 * 新NISA投資枠利用状況カードコンポーネントのテスト
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import NisaQuotaCard from "../NisaQuotaCard";
import { NisaQuotaStatus } from "@/lib/nisa/types";

// モックデータ
const mockQuotas: NisaQuotaStatus = {
  growthInvestment: {
    annualLimit: 2_400_000,
    taxFreeLimit: 12_000_000,
    usedAmount: 500_000,
    availableAmount: 1_900_000,
    utilizationRate: 20.83,
  },
  accumulationInvestment: {
    annualLimit: 400_000,
    taxFreeLimit: 2_000_000,
    usedAmount: 100_000,
    availableAmount: 300_000,
    utilizationRate: 25.0,
  },
  quotaReuse: {
    growthAvailable: 0,
    accumulationAvailable: 0,
    nextYearAvailable: 0,
  },
};

const highUtilizationQuotas: NisaQuotaStatus = {
  growthInvestment: {
    annualLimit: 2_400_000,
    taxFreeLimit: 12_000_000,
    usedAmount: 2_200_000,
    availableAmount: 200_000,
    utilizationRate: 91.67,
  },
  accumulationInvestment: {
    annualLimit: 400_000,
    taxFreeLimit: 2_000_000,
    usedAmount: 300_000,
    availableAmount: 100_000,
    utilizationRate: 75.0,
  },
  quotaReuse: {
    growthAvailable: 100_000,
    accumulationAvailable: 50_000,
    nextYearAvailable: 150_000,
  },
};

describe("NisaQuotaCard", () => {
  it("成長投資枠の情報を正しく表示する", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    expect(screen.getByText("成長投資枠")).toBeInTheDocument();
    expect(screen.getByText("20.8%")).toBeInTheDocument();
    expect(screen.getByText("¥500,000")).toBeInTheDocument();
    expect(screen.getByText("¥1,900,000")).toBeInTheDocument();
  });

  it("つみたて投資枠の情報を正しく表示する", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    expect(screen.getByText("つみたて投資枠")).toBeInTheDocument();
    expect(screen.getByText("25.0%")).toBeInTheDocument();
    expect(screen.getByText("¥100,000")).toBeInTheDocument();
    expect(screen.getByText("¥300,000")).toBeInTheDocument();
  });

  it("年間投資枠と非課税保有限度額を正しく表示する", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    expect(screen.getByText("年間投資枠")).toBeInTheDocument();
    expect(screen.getByText("¥2,400,000")).toBeInTheDocument();
    expect(screen.getByText("¥400,000")).toBeInTheDocument();
    expect(screen.getByText("非課税保有限度額")).toBeInTheDocument();
    expect(screen.getByText("¥12,000,000")).toBeInTheDocument();
    expect(screen.getByText("¥2,000,000")).toBeInTheDocument();
  });

  it("高利用率時にアラートを表示する", () => {
    render(<NisaQuotaCard quotas={highUtilizationQuotas} />);
    
    expect(screen.getByText("成長投資枠の利用率が90%を超えています。投資計画の見直しを検討してください。")).toBeInTheDocument();
    expect(screen.getByText("つみたて投資枠の利用率が70%を超えています。積立投資の見直しを検討してください。")).toBeInTheDocument();
  });

  it("枠の再利用状況を正しく表示する", () => {
    render(<NisaQuotaCard quotas={highUtilizationQuotas} />);
    
    expect(screen.getByText("枠の再利用状況")).toBeInTheDocument();
    expect(screen.getByText("成長枠再利用可能額")).toBeInTheDocument();
    expect(screen.getByText("¥100,000")).toBeInTheDocument();
    expect(screen.getByText("つみたて枠再利用可能額")).toBeInTheDocument();
    expect(screen.getByText("¥50,000")).toBeInTheDocument();
    expect(screen.getByText("翌年度に ¥150,000 の投資枠が再利用可能です")).toBeInTheDocument();
  });

  it("再利用可能額が0の場合は再利用状況を表示しない", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    expect(screen.queryByText("枠の再利用状況")).not.toBeInTheDocument();
  });

  it("カスタムクラス名を適用する", () => {
    const { container } = render(<NisaQuotaCard quotas={mockQuotas} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("利用率に応じて色分けされる", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    // 低利用率（緑色）
    const growthBadge = screen.getByText("20.8%").closest("[data-testid=\"badge\"]");
    expect(growthBadge).toHaveClass("bg-green-100", "text-green-800");
  });

  it("高利用率時に警告色で表示される", () => {
    render(<NisaQuotaCard quotas={highUtilizationQuotas} />);
    
    // 高利用率（赤色）
    const growthBadge = screen.getByText("91.7%").closest("[data-testid=\"badge\"]");
    expect(growthBadge).toHaveClass("bg-red-100", "text-red-800");
  });

  it("プログレスバーが正しく表示される", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    const progressBars = screen.getAllByRole("progressbar");
    expect(progressBars).toHaveLength(2); // 成長枠とつみたて枠
  });

  it("通貨フォーマットが正しく適用される", () => {
    render(<NisaQuotaCard quotas={mockQuotas} />);
    
    // 日本円のフォーマット（¥記号とカンマ区切り）
    expect(screen.getByText("¥500,000")).toBeInTheDocument();
    expect(screen.getByText("¥1,900,000")).toBeInTheDocument();
    expect(screen.getByText("¥2,400,000")).toBeInTheDocument();
  });
});
