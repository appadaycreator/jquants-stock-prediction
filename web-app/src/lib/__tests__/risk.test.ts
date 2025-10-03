import { 
  calculateVaR, 
  calculateCVaR, 
  calculateSharpeRatio, 
  calculateSortinoRatio,
  calculateMaxDrawdown,
  calculateBeta,
  calculateCorrelation,
  calculateVolatility,
  calculateSkewness,
  calculateKurtosis,
} from "../risk";
describe("risk", () => {
  const testReturns = [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.01, 0.02];
  const testPrices = [100, 102, 101, 104, 102, 103, 105, 104, 105, 107];
  describe("calculateVaR", () => {
    it("calculates Value at Risk", () => {
      const var95 = calculateVaR(testReturns, 0.95);
      expect(var95).toBeLessThan(0);
      expect(var95).toBeGreaterThan(-0.1);
    });
    it("handles empty returns", () => {
      const var95 = calculateVaR([], 0.95);
      expect(var95).toBe(0);
    });
  });
  describe("calculateCVaR", () => {
    it("calculates Conditional Value at Risk", () => {
      const cvar95 = calculateCVaR(testReturns, 0.95);
      expect(cvar95).toBeLessThan(0);
      expect(cvar95).toBeLessThanOrEqual(calculateVaR(testReturns, 0.95));
    });
    it("handles empty returns", () => {
      const cvar95 = calculateCVaR([], 0.95);
      expect(cvar95).toBe(0);
    });
  });
  describe("calculateSharpeRatio", () => {
    it("calculates Sharpe ratio", () => {
      const sharpe = calculateSharpeRatio(testReturns, 0.02);
      expect(typeof sharpe).toBe("number");
      expect(sharpe).toBeGreaterThan(-10);
      expect(sharpe).toBeLessThan(10);
    });
    it("handles zero risk-free rate", () => {
      const sharpe = calculateSharpeRatio(testReturns, 0);
      expect(typeof sharpe).toBe("number");
    });
  });
  describe("calculateSortinoRatio", () => {
    it("calculates Sortino ratio", () => {
      const sortino = calculateSortinoRatio(testReturns, 0.02);
      expect(typeof sortino).toBe("number");
      expect(sortino).toBeGreaterThan(-10);
      expect(sortino).toBeLessThan(10);
    });
    it("handles zero risk-free rate", () => {
      const sortino = calculateSortinoRatio(testReturns, 0);
      expect(typeof sortino).toBe("number");
    });
  });
  describe("calculateMaxDrawdown", () => {
    it("calculates maximum drawdown", () => {
      const maxDD = calculateMaxDrawdown(testPrices);
      expect(maxDD).toBeLessThanOrEqual(0);
      expect(maxDD).toBeGreaterThan(-1);
    });
    it("handles single price", () => {
      const maxDD = calculateMaxDrawdown([100]);
      expect(maxDD).toBe(0);
    });
  });
  describe("calculateBeta", () => {
    it("calculates beta coefficient", () => {
      const beta = calculateBeta(testReturns, testReturns);
      expect(beta).toBeCloseTo(1, 1);
    });
    it("handles different return series", () => {
      const otherReturns = [0.02, 0.01, -0.02, 0.04, -0.01, 0.02, 0.01, -0.02, 0.02, 0.01];
      const beta = calculateBeta(testReturns, otherReturns);
      expect(typeof beta).toBe("number");
    });
  });
  describe("calculateCorrelation", () => {
    it("calculates correlation coefficient", () => {
      const correlation = calculateCorrelation(testReturns, testReturns);
      expect(correlation).toBeCloseTo(1, 1);
    });
    it("handles different return series", () => {
      const otherReturns = [0.02, 0.01, -0.02, 0.04, -0.01, 0.02, 0.01, -0.02, 0.02, 0.01];
      const correlation = calculateCorrelation(testReturns, otherReturns);
      expect(correlation).toBeGreaterThanOrEqual(-1);
      expect(correlation).toBeLessThanOrEqual(1);
    });
  });
  describe("calculateVolatility", () => {
    it("calculates volatility", () => {
      const volatility = calculateVolatility(testReturns);
      expect(volatility).toBeGreaterThan(0);
      expect(volatility).toBeLessThan(1);
    });
    it("handles empty returns", () => {
      const volatility = calculateVolatility([]);
      expect(volatility).toBe(0);
    });
  });
  describe("calculateSkewness", () => {
    it("calculates skewness", () => {
      const skewness = calculateSkewness(testReturns);
      expect(typeof skewness).toBe("number");
      expect(skewness).toBeGreaterThan(-10);
      expect(skewness).toBeLessThan(10);
    });
    it("handles empty returns", () => {
      const skewness = calculateSkewness([]);
      expect(skewness).toBe(0);
    });
  });
  describe("calculateKurtosis", () => {
    it("calculates kurtosis", () => {
      const kurtosis = calculateKurtosis(testReturns);
      expect(typeof kurtosis).toBe("number");
      expect(kurtosis).toBeGreaterThan(-10);
      expect(kurtosis).toBeLessThan(10);
    });
    it("handles empty returns", () => {
      const kurtosis = calculateKurtosis([]);
      expect(kurtosis).toBe(0);
    });
  });
});
