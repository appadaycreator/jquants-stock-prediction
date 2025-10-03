import { formatCurrency, formatPercentage, debounce } from "../utils";

describe("utils", () => {
  describe("formatCurrency", () => {
    it("formats positive numbers correctly", () => {
      expect(formatCurrency(1000)).toBe("￥1,000");
      expect(formatCurrency(1000000)).toBe("￥1,000,000");
    });

    it("formats negative numbers correctly", () => {
      expect(formatCurrency(-1000)).toBe("-￥1,000");
    });

    it("handles zero", () => {
      expect(formatCurrency(0)).toBe("￥0");
    });

    it("handles decimal numbers", () => {
      expect(formatCurrency(1234.56)).toBe("￥1,235");
    });
  });

  describe("formatPercentage", () => {
    it("formats percentages correctly", () => {
      expect(formatPercentage(0.1)).toBe("10.0%");
      expect(formatPercentage(0.1234)).toBe("12.3%");
    });

    it("handles negative percentages", () => {
      expect(formatPercentage(-0.1)).toBe("-10.0%");
    });

    it("handles zero", () => {
      expect(formatPercentage(0)).toBe("0.0%");
    });
  });

  describe("debounce", () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it("delays function execution", () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn();
      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it("cancels previous calls", () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });

});