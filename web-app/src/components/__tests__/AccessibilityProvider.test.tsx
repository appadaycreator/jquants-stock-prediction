/**
 * AccessibilityProviderコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { AccessibilityProvider, useAccessibility } from "../AccessibilityProvider";

// テスト用のコンポーネント
const TestComponent = () => {
  const {
    highContrast,
    setHighContrast,
    largeText,
    setLargeText,
    reducedMotion,
    setReducedMotion,
    colorBlindMode,
    setColorBlindMode,
    fontSize,
    setFontSize,
    screenReader,
    setScreenReader,
  } = useAccessibility();

  return (
    <div>
      <div data-testid="high-contrast">{highContrast ? "enabled" : "disabled"}</div>
      <div data-testid="large-text">{largeText ? "enabled" : "disabled"}</div>
      <div data-testid="reduced-motion">{reducedMotion ? "enabled" : "disabled"}</div>
      <div data-testid="color-blind-mode">{colorBlindMode ? "enabled" : "disabled"}</div>
      <div data-testid="font-size">{fontSize}</div>
      <div data-testid="screen-reader">{screenReader ? "enabled" : "disabled"}</div>
      
      <button onClick={() => setHighContrast(!highContrast)}>Toggle High Contrast</button>
      <button onClick={() => setLargeText(!largeText)}>Toggle Large Text</button>
      <button onClick={() => setReducedMotion(!reducedMotion)}>Toggle Reduced Motion</button>
      <button onClick={() => setColorBlindMode(!colorBlindMode)}>Toggle Color Blind Mode</button>
      <button onClick={() => setFontSize(fontSize + 2)}>Increase Font Size</button>
      <button onClick={() => setScreenReader(!screenReader)}>Toggle Screen Reader</button>
    </div>
  );
};

describe("AccessibilityProvider", () => {
  beforeEach(() => {
    // ローカルストレージをクリア
    localStorage.clear();
  });

  it("デフォルト設定でレンダリングされる", () => {
    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    expect(screen.getByTestId("high-contrast")).toHaveTextContent("disabled");
    expect(screen.getByTestId("large-text")).toHaveTextContent("disabled");
    expect(screen.getByTestId("reduced-motion")).toHaveTextContent("disabled");
    expect(screen.getByTestId("color-blind-mode")).toHaveTextContent("disabled");
    expect(screen.getByTestId("font-size")).toHaveTextContent("16");
    expect(screen.getByTestId("screen-reader")).toHaveTextContent("disabled");
  });

  it("設定を変更できる", () => {
    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    // ハイコントラストを有効化
    fireEvent.click(screen.getByText("Toggle High Contrast"));
    expect(screen.getByTestId("high-contrast")).toHaveTextContent("enabled");

    // 大きなテキストを有効化
    fireEvent.click(screen.getByText("Toggle Large Text"));
    expect(screen.getByTestId("large-text")).toHaveTextContent("enabled");

    // フォントサイズを変更
    fireEvent.click(screen.getByText("Increase Font Size"));
    expect(screen.getByTestId("font-size")).toHaveTextContent("18");
  });

  it("ローカルストレージから設定を読み込む", () => {
    // ローカルストレージに設定を保存
    localStorage.setItem("accessibility-settings", JSON.stringify({
      highContrast: true,
      largeText: true,
      reducedMotion: false,
      colorBlindMode: true,
      fontSize: 20,
      screenReader: true,
    }));

    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    expect(screen.getByTestId("high-contrast")).toHaveTextContent("enabled");
    expect(screen.getByTestId("large-text")).toHaveTextContent("enabled");
    expect(screen.getByTestId("reduced-motion")).toHaveTextContent("disabled");
    expect(screen.getByTestId("color-blind-mode")).toHaveTextContent("enabled");
    expect(screen.getByTestId("font-size")).toHaveTextContent("20");
    expect(screen.getByTestId("screen-reader")).toHaveTextContent("enabled");
  });

  it("設定変更時にローカルストレージに保存される", () => {
    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    // 設定を変更
    fireEvent.click(screen.getByText("Toggle High Contrast"));
    fireEvent.click(screen.getByText("Increase Font Size"));

    // ローカルストレージを確認
    const savedSettings = JSON.parse(localStorage.getItem("accessibility-settings") || "{}");
    expect(savedSettings.highContrast).toBe(true);
    expect(savedSettings.fontSize).toBe(18);
  });

  it("useAccessibilityがProvider外で使用された場合にエラーを投げる", () => {
    // エラーをキャッチするためのモック
    const consoleError = jest.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow("useAccessibility must be used within an AccessibilityProvider");

    consoleError.mockRestore();
  });
});
