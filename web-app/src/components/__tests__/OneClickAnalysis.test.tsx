import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import OneClickAnalysis from "../OneClickAnalysis";

// Mock the useAnalysisWithSettings hook
jest.mock("@/hooks/useAnalysisWithSettings", () => ({
  useAnalysisWithSettings: () => ({
    runAnalysisWithSettings: jest.fn(),
    getAnalysisDescription: jest.fn(() => "Test analysis description"),
  }),
}));

// Mock the fetchJson function
jest.mock("@/lib/fetcher", () => ({
  fetchJson: jest.fn(),
}));

describe("OneClickAnalysis", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without crashing", () => {
    render(<OneClickAnalysis />);
    expect(screen.getByText("ワンクリック分析実行")).toBeInTheDocument();
  });

  it("displays analysis configuration options", () => {
    render(<OneClickAnalysis />);
    // 設定パネルを開く必要がある
    const configButton = screen.getByRole("button", { name: /設定/i });
    fireEvent.click(configButton);
    
    expect(screen.getByText("超高速分析")).toBeInTheDocument();
    expect(screen.getByText("包括的分析")).toBeInTheDocument();
    expect(screen.getByText("銘柄分析")).toBeInTheDocument();
  });

  it("shows configuration panel when config button is clicked", () => {
    render(<OneClickAnalysis />);
    const configButton = screen.getByRole("button", { name: /設定/i });
    fireEvent.click(configButton);
    expect(screen.getByText("分析タイプを選択")).toBeInTheDocument();
  });

  it("starts analysis when start button is clicked", async () => {
    const mockRunAnalysis = jest.fn().mockResolvedValue({});
    const { useAnalysisWithSettings } = require("@/hooks/useAnalysisWithSettings");
    useAnalysisWithSettings.mockReturnValue({
      runAnalysisWithSettings: mockRunAnalysis,
      getAnalysisDescription: jest.fn(() => "Test analysis description"),
    });

    render(<OneClickAnalysis />);
    const startButton = screen.getByRole("button", { name: /分析実行/i });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockRunAnalysis).toHaveBeenCalled();
    });
  });

  it("displays analysis history when history button is clicked", () => {
    render(<OneClickAnalysis />);
    const historyButton = screen.getByRole("button", { name: /分析履歴/i });
    fireEvent.click(historyButton);
    expect(screen.getByText("分析履歴")).toBeInTheDocument();
  });

  it("handles analysis type selection", () => {
    render(<OneClickAnalysis />);
    // 設定パネルを開く
    const configButton = screen.getByRole("button", { name: /設定/i });
    fireEvent.click(configButton);
    
    const comprehensiveOption = screen.getByText("包括的分析");
    fireEvent.click(comprehensiveOption);
    expect(comprehensiveOption).toHaveClass("bg-blue-50");
  });

  it("shows progress during analysis", async () => {
    const mockRunAnalysis = jest.fn().mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve({}), 100);
      });
    });
    const { useAnalysisWithSettings } = require("@/hooks/useAnalysisWithSettings");
    useAnalysisWithSettings.mockReturnValue({
      runAnalysisWithSettings: mockRunAnalysis,
      getAnalysisDescription: jest.fn(() => "Test analysis description"),
    });

    render(<OneClickAnalysis />);
    const startButton = screen.getByRole("button", { name: /分析実行/i });
    fireEvent.click(startButton);

    expect(screen.getByText("実行中...")).toBeInTheDocument();
  });
});
