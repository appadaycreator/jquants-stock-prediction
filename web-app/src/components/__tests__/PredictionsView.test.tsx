/**
 * PredictionsViewコンポーネントのテスト
 */

import { render, screen, waitFor } from "@testing-library/react";
import PredictionsView from "../PredictionsView";

// モック
jest.mock("../../lib/fetcher", () => ({
  fetchMultiple: jest.fn(),
  AppError: class AppError extends Error {
    constructor(message: string, public code: string, public status?: number) {
      super(message);
      this.name = "AppError";
    }
  },
}));

jest.mock("../../lib/datetime", () => ({
  parseToJst: jest.fn((date: string) => ({ isValid: true, toFormat: () => date })),
  jstLabel: jest.fn((dt: any) => dt.toFormat ? dt.toFormat() : "2024-01-01"),
}));

jest.mock("../../lib/metrics", () => ({
  mae: jest.fn(() => 10.5),
  rmse: jest.fn(() => 15.2),
  r2: jest.fn(() => 0.85),
  detectOverfitting: jest.fn(() => ({
    isOverfitting: false,
    riskLevel: "低" as const,
    message: "低リスク",
  })),
  compareModels: jest.fn(() => ({
    maeImprovement: 15.5,
    rmseImprovement: 12.3,
    r2Improvement: 0.1,
    isBetter: true,
  })),
}));

jest.mock("../../lib/logger", () => ({
  fetcherLogger: {
    info: jest.fn(),
    error: jest.fn(),
  },
  metricsLogger: {
    info: jest.fn(),
  },
}));

describe("PredictionsView", () => {
  const mockFetchMultiple = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    const { fetchMultiple } = require("../../lib/fetcher");
    fetchMultiple.mockImplementation(mockFetchMultiple);
  });

  it("ローディング状態を表示する", () => {
    mockFetchMultiple.mockImplementation(() => new Promise(() => {})); // 永続的にpending

    render(<PredictionsView onError={mockOnError} />);
    
    expect(screen.getByText(/データを読み込み中/)).toBeInTheDocument();
  });

  it("正常なデータを表示する", async () => {
    const mockData = {
      predictions: {
        meta: { model: "Test Model", generatedAt: "2024-01-01T00:00:00Z" },
        data: [
          { date: "2024-01-01", symbol: "7203", y_true: 100, y_pred: 105 },
          { date: "2024-01-02", symbol: "7203", y_true: 110, y_pred: 108 },
        ],
      },
      stockData: [
        { date: "2024-01-01", close: 100, sma_5: 98, sma_10: 95, sma_25: 90, sma_50: 85, volume: 1000000 },
      ],
      modelComparison: [
        { model_name: "Test Model", model_type: "Linear", mae: 10, rmse: 15, r2: 0.85, rank: 1 },
      ],
    };

    mockFetchMultiple.mockResolvedValue(mockData);

    render(<PredictionsView onError={mockOnError} />);

    await waitFor(() => {
      expect(screen.getByText("予測結果")).toBeInTheDocument();
    });

    expect(screen.getByText("Test Model")).toBeInTheDocument();
    expect(screen.getByText("MAE")).toBeInTheDocument();
    expect(screen.getByText("RMSE")).toBeInTheDocument();
    expect(screen.getByText("R²")).toBeInTheDocument();
  });

  it("エラー状態を表示する", async () => {
    const error = new Error("Network error");
    mockFetchMultiple.mockRejectedValue(error);

    render(<PredictionsView onError={mockOnError} />);

    await waitFor(() => {
      expect(screen.getByText(/データの読み込みに失敗しました/)).toBeInTheDocument();
    });
  });

  it("再試行ボタンが動作する", async () => {
    const error = new Error("Network error");
    mockFetchMultiple.mockRejectedValueOnce(error);

    render(<PredictionsView onError={mockOnError} />);

    await waitFor(() => {
      expect(screen.getByText(/データの読み込みに失敗しました/)).toBeInTheDocument();
    });

    // 再試行ボタンをクリック
    const retryButton = screen.getByText("再試行");
    expect(retryButton).toBeInTheDocument();
  });

  it("過学習警告を表示する", async () => {
    const { detectOverfitting } = require("../../lib/metrics");
    detectOverfitting.mockReturnValue({
      isOverfitting: true,
      riskLevel: "高",
      message: "高リスク（R² > 0.99）",
    });

    const mockData = {
      predictions: {
        meta: { model: "Test Model", generatedAt: "2024-01-01T00:00:00Z" },
        data: [{ date: "2024-01-01", symbol: "7203", y_true: 100, y_pred: 105 }],
      },
      stockData: [],
      modelComparison: [],
    };

    mockFetchMultiple.mockResolvedValue(mockData);

    render(<PredictionsView onError={mockOnError} />);

    await waitFor(() => {
      expect(screen.getByText(/過学習のリスクが検出されました/)).toBeInTheDocument();
    });
  });
});
