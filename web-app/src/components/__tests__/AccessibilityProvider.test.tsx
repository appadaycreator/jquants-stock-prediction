/**
 * AccessibilityProviderコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { AccessibilityProvider, useAccessibility } from "../AccessibilityProvider";

// テスト用コンポーネント
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
      <button onClick={() => setFontSize(fontSize + 1)}>Increase Font Size</button>
      <button onClick={() => setScreenReader(!screenReader)}>Toggle Screen Reader</button>
    </div>
  );
};

describe("AccessibilityProvider", () => {
  beforeEach(() => {
    // ローカルストレージをクリア
    localStorage.clear();
  });

  it("デフォルト値で初期化される", () => {
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

    // 高コントラストを有効にする
    fireEvent.click(screen.getByText("Toggle High Contrast"));
    expect(screen.getByTestId("high-contrast")).toHaveTextContent("enabled");

    // 大きなテキストを有効にする
    fireEvent.click(screen.getByText("Toggle Large Text"));
    expect(screen.getByTestId("large-text")).toHaveTextContent("enabled");

    // アニメーション削減を有効にする
    fireEvent.click(screen.getByText("Toggle Reduced Motion"));
    expect(screen.getByTestId("reduced-motion")).toHaveTextContent("enabled");

    // 色覚障害モードを有効にする
    fireEvent.click(screen.getByText("Toggle Color Blind Mode"));
    expect(screen.getByTestId("color-blind-mode")).toHaveTextContent("enabled");

    // フォントサイズを増やす
    fireEvent.click(screen.getByText("Increase Font Size"));
    expect(screen.getByTestId("font-size")).toHaveTextContent("17");

    // スクリーンリーダーを有効にする
    fireEvent.click(screen.getByText("Toggle Screen Reader"));
    expect(screen.getByTestId("screen-reader")).toHaveTextContent("enabled");
  });

  it("ローカルストレージから設定を読み込む", () => {
    const settings = {
      highContrast: true,
      largeText: true,
      reducedMotion: false,
      colorBlindMode: true,
      fontSize: 18,
      screenReader: true,
    };
    localStorage.setItem("accessibility-settings", JSON.stringify(settings));

    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    expect(screen.getByTestId("high-contrast")).toHaveTextContent("enabled");
    expect(screen.getByTestId("large-text")).toHaveTextContent("enabled");
    expect(screen.getByTestId("reduced-motion")).toHaveTextContent("disabled");
    expect(screen.getByTestId("color-blind-mode")).toHaveTextContent("enabled");
    expect(screen.getByTestId("font-size")).toHaveTextContent("18");
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
    fireEvent.click(screen.getByText("Toggle Large Text"));

    // ローカルストレージに保存されていることを確認
    const savedSettings = JSON.parse(localStorage.getItem("accessibility-settings") || "{}");
    expect(savedSettings.highContrast).toBe(true);
    expect(savedSettings.largeText).toBe(true);
  });

  it("HTMLにアクセシビリティクラスが適用される", () => {
    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>,
    );

    // 高コントラストを有効にする
    fireEvent.click(screen.getByText("Toggle High Contrast"));
    
    // HTML要素にクラスが適用されることを確認
    expect(document.documentElement.classList.contains("high-contrast-mode")).toBe(true);
  });
});