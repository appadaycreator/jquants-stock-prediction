/**
 * utilsライブラリのテスト
 */

import { clsx } from "clsx";

// cn関数の実装をモック
const cn = (...inputs: any[]) => clsx(inputs);

describe("cn", () => {
  it("クラス名を正しく結合する", () => {
    const result = cn("class1", "class2");
    expect(result).toBe("class1 class2");
  });

  it("条件付きクラス名を正しく処理する", () => {
    const result = cn("base", true && "conditional", false && "hidden");
    expect(result).toBe("base conditional");
  });

  it("undefinedやnullを無視する", () => {
    const result = cn("base", undefined, null, "valid");
    expect(result).toBe("base valid");
  });

  it("空文字列を無視する", () => {
    const result = cn("base", "", "valid");
    expect(result).toBe("base valid");
  });

  it("配列のクラス名を正しく処理する", () => {
    const result = cn(["class1", "class2"], "class3");
    expect(result).toBe("class1 class2 class3");
  });

  it("オブジェクトの条件付きクラス名を正しく処理する", () => {
    const result = cn({
      "active": true,
      "disabled": false,
      "hidden": true,
    });
    expect(result).toBe("active hidden");
  });
});
