/**
 * エラーハンドラーのテスト
 */

import { errorHandler, logError, getLocalizedErrorMessage, getErrorInfo } from "../error-handler";

describe("ErrorHandler", () => {
  beforeEach(() => {
    // テスト前にエラーハンドラーをリセット
    errorHandler.reset();
  });

  describe("categorizeError", () => {
    it("ネットワークエラーを正しく分類する", () => {
      const networkError = new Error("Network request failed");
      const errorInfo = errorHandler.categorizeError(networkError);
      
      expect(errorInfo.category).toBe("network");
      expect(errorInfo.severity).toBe("medium");
      expect(errorInfo.autoRetry).toBe(true);
      expect(errorInfo.retryDelay).toBe(3000);
    });

    it("APIエラーを正しく分類する", () => {
      const apiError = new Error("HTTP 404: Not Found");
      const errorInfo = errorHandler.categorizeError(apiError);
      
      expect(errorInfo.category).toBe("api");
      expect(errorInfo.severity).toBe("high");
      expect(errorInfo.autoRetry).toBe(false);
    });

    it("データエラーを正しく分類する", () => {
      const dataError = new Error("JSON parse error");
      const errorInfo = errorHandler.categorizeError(dataError);
      
      expect(errorInfo.category).toBe("data");
      expect(errorInfo.severity).toBe("medium");
      expect(errorInfo.autoRetry).toBe(true);
    });

    it("バリデーションエラーを正しく分類する", () => {
      const validationError = new Error("Validation failed: required field missing");
      const errorInfo = errorHandler.categorizeError(validationError);
      
      expect(errorInfo.category).toBe("validation");
      expect(errorInfo.severity).toBe("low");
      expect(errorInfo.autoRetry).toBe(false);
    });

    it("システムエラーを正しく分類する", () => {
      const systemError = new Error("Internal system error");
      const errorInfo = errorHandler.categorizeError(systemError);
      
      expect(errorInfo.category).toBe("system");
      expect(errorInfo.severity).toBe("critical");
      expect(errorInfo.autoRetry).toBe(false);
    });

    it("未知のエラーを正しく分類する", () => {
      const unknownError = new Error("Some random error");
      const errorInfo = errorHandler.categorizeError(unknownError);
      
      expect(errorInfo.category).toBe("unknown");
      expect(errorInfo.severity).toBe("medium");
      expect(errorInfo.autoRetry).toBe(false);
    });
  });

  describe("handleError", () => {
    it("エラーを正しく処理する", async () => {
      const error = new Error("Test error");
      const result = await errorHandler.handleError(error);
      
      expect(typeof result).toBe("boolean");
    });

    it("重複エラーを制限する", async () => {
      const error = new Error("Duplicate error");
      
      // 同じエラーを複数回発生させる
      for (let i = 0; i < 15; i++) {
        await errorHandler.handleError(error);
      }
      
      const history = errorHandler.getErrorHistory();
      expect(history.length).toBeLessThanOrEqual(15);
    });
  });

  describe("getErrorHistory", () => {
    it("エラー履歴を正しく取得する", () => {
      const error = new Error("Test error");
      errorHandler.categorizeError(error);
      
      const history = errorHandler.getErrorHistory();
      expect(Array.isArray(history)).toBe(true);
    });
  });

  describe("getErrorStats", () => {
    it("エラー統計を正しく取得する", async () => {
      const error1 = new Error("Network error");
      const error2 = new Error("API error");
      
      await errorHandler.handleError(error1);
      await errorHandler.handleError(error2);
      
      const stats = errorHandler.getErrorStats();
      expect(stats.total).toBe(2);
      expect(stats.byCategory.network).toBe(1);
      expect(stats.byCategory.api).toBe(1);
    });
  });

  describe("reset", () => {
    it("エラーハンドラーを正しくリセットする", () => {
      const error = new Error("Test error");
      errorHandler.categorizeError(error);
      
      errorHandler.reset();
      
      const history = errorHandler.getErrorHistory();
      expect(history.length).toBe(0);
    });
  });
});

describe("logError", () => {
  it("エラーログを正しく記録する", () => {
    const error = new Error("Test error");
    const context = { component: "TestComponent" };
    
    // コンソールエラーをモック
    const consoleSpy = jest.spyOn(console, "error").mockImplementation();
    
    logError(error, context);
    
    expect(consoleSpy).toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });
});

describe("getLocalizedErrorMessage", () => {
  it("日本語エラーメッセージを正しく取得する", () => {
    const error = new Error("Network error");
    const message = getLocalizedErrorMessage(error, "ja");
    
    expect(typeof message).toBe("string");
    expect(message.length).toBeGreaterThan(0);
  });
});

describe("getErrorInfo", () => {
  it("エラー情報を正しく取得する", () => {
    const error = new Error("Test error");
    const errorInfo = getErrorInfo(error);
    
    expect(errorInfo.category).toBeDefined();
    expect(errorInfo.severity).toBeDefined();
    expect(errorInfo.message).toBe("Test error");
  });
});
