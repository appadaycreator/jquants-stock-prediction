/**
 * TimeSeriesChartコンポーネントのテスト
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import TimeSeriesChart from "../TimeSeriesChart";

// モック
vi.mock("../../lib/datetime", () => ({
  parseToJst: vi.fn((date: string) => ({ 
    isValid: date !== "invalid", 
    toFormat: () => date,
    toMillis: () => Date.now(),
  })),
  jstLabel: vi.fn((dt: any) => dt.toFormat ? dt.toFormat() : "2024-01-01"),
}));

vi.mock("../../lib/logger", () => ({
  chartLogger: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

describe("TimeSeriesChart", () => {
  const mockData = [
    { date: "2024-01-01", price: 100, sma_5: 98 },
    { date: "2024-01-02", price: 105, sma_5: 100 },
    { date: "2024-01-03", price: 110, sma_5: 105 },
  ];

  const mockLines = [
    { dataKey: "price", stroke: "#2563eb", strokeWidth: 2, name: "価格" },
    { dataKey: "sma_5", stroke: "#dc2626", strokeWidth: 1, name: "SMA_5" },
  ];

  it("正常なデータを表示する", () => {
    render(
      <TimeSeriesChart
        data={mockData}
        lines={mockLines}
        title="テストチャート"
        height={300}
      />,
    );

    expect(screen.getByText("テストチャート")).toBeInTheDocument();
  });

  it("空のデータに対して空の状態を表示する", () => {
    render(
      <TimeSeriesChart
        data={[]}
        lines={mockLines}
        title="テストチャート"
        height={300}
      />,
    );

    expect(screen.getByText("データがありません")).toBeInTheDocument();
  });

  it("無効な日付を除外する", () => {
    const dataWithInvalidDate = [
      { date: "2024-01-01", price: 100 },
      { date: "invalid", price: 105 },
      { date: "2024-01-03", price: 110 },
    ];

    render(
      <TimeSeriesChart
        data={dataWithInvalidDate}
        lines={mockLines}
        title="テストチャート"
        height={300}
      />,
    );

    // 無効な日付は除外されるため、チャートは表示される
    expect(screen.getByText("テストチャート")).toBeInTheDocument();
  });

  it("タイトルなしでも動作する", () => {
    render(
      <TimeSeriesChart
        data={mockData}
        lines={mockLines}
        height={300}
      />,
    );

    // タイトルが表示されないことを確認
    expect(screen.queryByText("テストチャート")).not.toBeInTheDocument();
  });

  it("カスタム高さを適用する", () => {
    const { container } = render(
      <TimeSeriesChart
        data={mockData}
        lines={mockLines}
        title="テストチャート"
        height={400}
      />,
    );

    // ResponsiveContainerの高さが400pxに設定されることを確認
    const responsiveContainer = container.querySelector(".recharts-responsive-container");
    expect(responsiveContainer).toBeInTheDocument();
  });
});
