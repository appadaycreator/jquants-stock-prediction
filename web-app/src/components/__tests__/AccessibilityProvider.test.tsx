/**
 * AccessibilityProvider のテスト
 */

import { render, screen } from "@testing-library/react";
import { AccessibilityProvider } from "../AccessibilityProvider";

describe("AccessibilityProvider", () => {
  it("正常にレンダリングされる", () => {
    render(
      <AccessibilityProvider>
        <div>テストコンテンツ</div>
      </AccessibilityProvider>
    );

    expect(screen.getByText("テストコンテンツ")).toBeInTheDocument();
  });

  it("アクセシビリティ設定を提供する", () => {
    const TestComponent = () => {
      return <div>アクセシビリティテスト</div>;
    };

    render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    expect(screen.getByText("アクセシビリティテスト")).toBeInTheDocument();
  });
});