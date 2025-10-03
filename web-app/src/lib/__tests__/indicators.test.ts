import { 
  calculateSMA, 
  calculateEMA, 
  calculateRSI, 
  calculateMACD,
  calculateBollingerBands,
  calculateStochastic,
  calculateWilliamsR,
  calculateCCI,
  calculateATR,
  calculateADX
} from "../indicators";

describe("indicators", () => {
  const testData = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109];

  describe("calculateSMA", () => {
    it("calculates simple moving average", () => {
      const sma = calculateSMA(testData, 5);
      expect(sma).toHaveLength(6); // 5期間のSMAなので6個の値
      expect(sma[0]).toBeCloseTo(101.6, 1);
    });

    it("handles insufficient data", () => {
      const sma = calculateSMA([1, 2], 5);
      expect(sma).toHaveLength(0);
    });
  });

  describe("calculateEMA", () => {
    it("calculates exponential moving average", () => {
      const ema = calculateEMA(testData, 5);
      expect(ema).toHaveLength(10);
      expect(ema[0]).toBeCloseTo(100, 1);
    });

    it("handles insufficient data", () => {
      const ema = calculateEMA([1, 2], 5);
      expect(ema).toHaveLength(2);
    });
  });

  describe("calculateRSI", () => {
    it("calculates RSI", () => {
      const rsi = calculateRSI(testData, 14);
      expect(rsi).toHaveLength(10);
      expect(rsi[0]).toBeCloseTo(50, 1);
    });

    it("handles insufficient data", () => {
      const rsi = calculateRSI([1, 2], 14);
      expect(rsi).toHaveLength(2);
    });
  });

  describe("calculateMACD", () => {
    it("calculates MACD", () => {
      const macd = calculateMACD(testData, 12, 26, 9);
      expect(macd).toHaveProperty("macd");
      expect(macd).toHaveProperty("signal");
      expect(macd).toHaveProperty("histogram");
    });

    it("handles insufficient data", () => {
      const macd = calculateMACD([1, 2], 12, 26, 9);
      expect(macd.macd).toHaveLength(2);
    });
  });

  describe("calculateBollingerBands", () => {
    it("calculates Bollinger Bands", () => {
      const bands = calculateBollingerBands(testData, 20, 2);
      expect(bands).toHaveProperty("upper");
      expect(bands).toHaveProperty("middle");
      expect(bands).toHaveProperty("lower");
    });

    it("handles insufficient data", () => {
      const bands = calculateBollingerBands([1, 2], 20, 2);
      expect(bands.upper).toHaveLength(2);
    });
  });

  describe("calculateStochastic", () => {
    it("calculates Stochastic", () => {
      const stoch = calculateStochastic(testData, testData, testData, 14);
      expect(stoch).toHaveProperty("k");
      expect(stoch).toHaveProperty("d");
    });

    it("handles insufficient data", () => {
      const stoch = calculateStochastic([1, 2], [1, 2], [1, 2], 14);
      expect(stoch.k).toHaveLength(2);
    });
  });

  describe("calculateWilliamsR", () => {
    it("calculates Williams %R", () => {
      const williamsR = calculateWilliamsR(testData, testData, testData, 14);
      expect(williamsR).toHaveLength(10);
      expect(williamsR[0]).toBeCloseTo(-50, 1);
    });

    it("handles insufficient data", () => {
      const williamsR = calculateWilliamsR([1, 2], [1, 2], [1, 2], 14);
      expect(williamsR).toHaveLength(2);
    });
  });

  describe("calculateCCI", () => {
    it("calculates Commodity Channel Index", () => {
      const cci = calculateCCI(testData, testData, testData, 20);
      expect(cci).toHaveLength(10);
      expect(cci[0]).toBeCloseTo(0, 1);
    });

    it("handles insufficient data", () => {
      const cci = calculateCCI([1, 2], [1, 2], [1, 2], 20);
      expect(cci).toHaveLength(2);
    });
  });

  describe("calculateATR", () => {
    it("calculates Average True Range", () => {
      const atr = calculateATR(testData, testData, testData, 14);
      expect(atr).toHaveLength(10);
      expect(atr[0]).toBeGreaterThanOrEqual(0);
    });

    it("handles insufficient data", () => {
      const atr = calculateATR([1, 2], [1, 2], [1, 2], 14);
      expect(atr).toHaveLength(2);
    });
  });

  describe("calculateADX", () => {
    it("calculates Average Directional Index", () => {
      const adx = calculateADX(testData, testData, testData, 14);
      expect(adx).toHaveLength(10);
      expect(adx[0]).toBeGreaterThanOrEqual(0);
    });

    it("handles insufficient data", () => {
      const adx = calculateADX([1, 2], [1, 2], [1, 2], 14);
      expect(adx).toHaveLength(2);
    });
  }),
});

