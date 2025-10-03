import { logger } from "../logger";
// console のモック
const consoleSpy = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};
Object.defineProperty(console, "log", { value: consoleSpy.log });
Object.defineProperty(console, "error", { value: consoleSpy.error });
Object.defineProperty(console, "warn", { value: consoleSpy.warn });
Object.defineProperty(console, "info", { value: consoleSpy.info });
Object.defineProperty(console, "debug", { value: consoleSpy.debug });
describe("logger", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe("log", () => {
    it("logs messages with default level", () => {
      logger.log("Test message");
      expect(consoleSpy.log).toHaveBeenCalledWith("Test message");
    });
    it("logs messages with custom level", () => {
      logger.log("Test message", "error");
      expect(consoleSpy.error).toHaveBeenCalledWith("Test message");
    });
    it("handles objects", () => {
      const obj = { test: "value" };
      logger.log(obj);
      expect(consoleSpy.log).toHaveBeenCalledWith(obj);
    });
  });
  describe("error", () => {
    it("logs error messages", () => {
      logger.error("Error message");
      expect(consoleSpy.error).toHaveBeenCalledWith("Error message");
    });
    it("handles error objects", () => {
      const error = new Error("Test error");
      logger.error(error);
      expect(consoleSpy.error).toHaveBeenCalledWith(error);
    });
  });
  describe("warn", () => {
    it("logs warning messages", () => {
      logger.warn("Warning message");
      expect(consoleSpy.warn).toHaveBeenCalledWith("Warning message");
    });
  });
  describe("info", () => {
    it("logs info messages", () => {
      logger.info("Info message");
      expect(consoleSpy.info).toHaveBeenCalledWith("Info message");
    });
  });
  describe("debug", () => {
    it("logs debug messages", () => {
      logger.debug("Debug message");
      expect(consoleSpy.debug).toHaveBeenCalledWith("Debug message");
    });
  });
  describe("group", () => {
    it("creates log groups", () => {
      logger.group("Test Group");
      logger.log("Group message");
      logger.groupEnd();
      
      expect(consoleSpy.log).toHaveBeenCalledWith("Test Group");
      expect(consoleSpy.log).toHaveBeenCalledWith("Group message");
    });
  });
  describe("time", () => {
    it("measures execution time", () => {
      logger.time("test-timer");
      logger.timeEnd("test-timer");
      
      expect(consoleSpy.log).toHaveBeenCalledWith("test-timer:");
    });
  });
  describe("table", () => {
    it("logs data as table", () => {
      const data = [{ name: "test", value: 123 }];
      logger.table(data);
      
      expect(consoleSpy.log).toHaveBeenCalledWith(data);
    });
  });
});
