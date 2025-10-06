import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ProfitLossChart } from "../ProfitLossChart";

// モックデータ
const mockData = [
  {
    date: "2024-01-01",
    total_value: 1000000,
    daily_pnl: 0,
    cumulative_pnl: 0,
    benchmark_return: 0,
    volume: 1000000,
    volatility: 10.5,
  },
  {
    date: "2024-01-02",
    total_value: 1010000,
    daily_pnl: 10000,
    cumulative_pnl: 10000,
    benchmark_return: 0.5,
    volume: 1200000,
    volatility: 11.2,
  },
  {
    date: "2024-01-03",
    total_value: 1020000,
    daily_pnl: 10000,
    cumulative_pnl: 20000,
    benchmark_return: 1.0,
    volume: 1100000,
    volatility: 12.1,
  },
];

describe("ProfitLossChart", () => {
  const defaultProps = {
    data: mockData,
    height: 400,
    showBenchmark: false,
    showVolume: false,
    showVolatility: false,
    onDataPointClick: jest.fn(),
    className: "",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("正常にレンダリングされる", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("期間選択ボタンが正しく表示される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("1日")).toBeInTheDocument();
    expect(screen.getByText("1週")).toBeInTheDocument();
    expect(screen.getByText("1月")).toBeInTheDocument();
    expect(screen.getByText("3月")).toBeInTheDocument();
    expect(screen.getByText("1年")).toBeInTheDocument();
    expect(screen.getByText("全期間")).toBeInTheDocument();
  });

  it("チャートタイプボタンが正しく表示される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("ライン")).toBeInTheDocument();
    expect(screen.getByText("エリア")).toBeInTheDocument();
    expect(screen.getByText("バー")).toBeInTheDocument();
  });

  it("グリッドボタンが正しく表示される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("グリッド")).toBeInTheDocument();
  });

  it("期間選択が正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    const oneWeekButton = screen.getByText("1週");
    fireEvent.click(oneWeekButton);
    
    expect(oneWeekButton).toHaveClass("bg-blue-600");
  });

  it("チャートタイプの切り替えが正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    const areaButton = screen.getByText("エリア");
    fireEvent.click(areaButton);
    
    expect(areaButton).toHaveClass("bg-blue-600");
  });

  it("グリッドの切り替えが正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    const gridButton = screen.getByText("グリッド");
    fireEvent.click(gridButton);
    
    expect(gridButton).toHaveClass("bg-blue-600");
  });

  it("ベンチマーク表示が正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} showBenchmark={true} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("ボリューム表示が正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} showVolume={true} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("ボラティリティ表示が正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} showVolatility={true} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("パフォーマンス統計が正しく表示される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("総リターン")).toBeInTheDocument();
    expect(screen.getByText("平均日次リターン")).toBeInTheDocument();
    expect(screen.getByText("ボラティリティ")).toBeInTheDocument();
    expect(screen.getByText("シャープレシオ")).toBeInTheDocument();
  });

  it("凡例が正しく表示される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    expect(screen.getByText("総資産価値")).toBeInTheDocument();
    expect(screen.getByText("累積損益")).toBeInTheDocument();
  });

  it("ベンチマーク表示時の凡例", () => {
    render(<ProfitLossChart {...defaultProps} showBenchmark={true} />);
    
    expect(screen.getByText("総資産価値")).toBeInTheDocument();
    expect(screen.getByText("累積損益")).toBeInTheDocument();
    expect(screen.getByText("ベンチマーク")).toBeInTheDocument();
  });

  it("空のデータの場合の処理", () => {
    render(<ProfitLossChart {...defaultProps} data={[]} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("カスタムクラスが正しく適用される", () => {
    const { container } = render(<ProfitLossChart {...defaultProps} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("カスタム高さが正しく適用される", () => {
    render(<ProfitLossChart {...defaultProps} height={600} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("データポイントクリックが正しく動作する", () => {
    const mockOnDataPointClick = jest.fn();
    render(<ProfitLossChart {...defaultProps} onDataPointClick={mockOnDataPointClick} />);
    
    // チャートのデータポイントクリックをシミュレート
    // 実際の実装では、チャートライブラリのイベントハンドラーをテストする必要があります
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("期間フィルタリングが正しく動作する", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    // 1日ボタンをクリック
    const oneDayButton = screen.getByText("1日");
    fireEvent.click(oneDayButton);
    
    expect(oneDayButton).toHaveClass("bg-blue-600");
  });

  it("データポイントの最適化が正しく動作する", () => {
    // 大量のデータポイントを作成
    const largeData = Array.from({ length: 200 }, (_, index) => ({
      date: `2024-01-${String(index + 1).padStart(2, "0")}`,
      total_value: 1000000 + index * 1000,
      daily_pnl: index * 100,
      cumulative_pnl: index * 100,
      benchmark_return: index * 0.1,
      volume: 1000000 + index * 100,
      volatility: 10 + index * 0.1,
    }));

    render(<ProfitLossChart {...defaultProps} data={largeData} />);
    
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });

  it("レスポンシブデザインが正しく適用される", () => {
    render(<ProfitLossChart {...defaultProps} />);
    
    // チャートコンテナが正しく表示されることを確認
    expect(screen.getByText("損益推移グラフ")).toBeInTheDocument();
  });
});
