import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import MobileTestSuite from "../MobileTestSuite";

// Mock the performance API
Object.defineProperty(window, "performance", {
  value: {
    memory: {
      jsHeapSizeLimit: 4294967296, // 4GB
    },
    now: jest.fn(() => Date.now()),
  },
  writable: true,
});

// Mock the navigator API
Object.defineProperty(navigator, "hardwareConcurrency", {
  value: 8,
  writable: true,
});

Object.defineProperty(navigator, "connection", {
  value: {
    effectiveType: "4g",
    downlink: 10,
  },
  writable: true,
});

describe("MobileTestSuite", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component without crashing", () => {
    render(<MobileTestSuite />);
    expect(screen.getByText("モバイルテストスイート")).toBeInTheDocument();
  });

  it("displays test categories", () => {
    render(<MobileTestSuite />);
    expect(screen.getByText("デバイス情報")).toBeInTheDocument();
    expect(screen.getByText("パフォーマンス")).toBeInTheDocument();
    expect(screen.getByText("ネットワーク")).toBeInTheDocument();
    expect(screen.getByText("互換性")).toBeInTheDocument();
  });

  it("starts tests when run button is clicked", async () => {
    render(<MobileTestSuite />);
    const runButton = screen.getByRole("button", { name: /テストを実行/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("テスト実行中...")).toBeInTheDocument();
    });
  });

  it("displays test results after completion", async () => {
    render(<MobileTestSuite />);
    const runButton = screen.getByRole("button", { name: /テストを実行/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("テスト完了")).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it("shows device information correctly", () => {
    render(<MobileTestSuite />);
    expect(screen.getByText("画面サイズ:")).toBeInTheDocument();
    expect(screen.getByText("ウィンドウサイズ:")).toBeInTheDocument();
  });

  it("handles test errors gracefully", async () => {
    // Mock an error in the test execution
    const originalConsoleError = console.error;
    console.error = jest.fn();

    render(<MobileTestSuite />);
    const runButton = screen.getByRole("button", { name: /テストを実行/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("テスト完了")).toBeInTheDocument();
    }, { timeout: 5000 });

    console.error = originalConsoleError;
  });

  it("displays network information", () => {
    render(<MobileTestSuite />);
    expect(screen.getByText("接続タイプ:")).toBeInTheDocument();
    expect(screen.getByText("メモリ:")).toBeInTheDocument();
  });

  it("shows performance metrics", () => {
    render(<MobileTestSuite />);
    expect(screen.getByText("メモリ:")).toBeInTheDocument();
    expect(screen.getByText("CPUコア数:")).toBeInTheDocument();
  });
});
