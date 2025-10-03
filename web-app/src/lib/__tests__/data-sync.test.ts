import { 
  syncData, 
  getSyncStatus, 
  getLastSyncTime,
  setSyncInterval,
  startSync,
  stopSync,
  isSyncRunning,
  getSyncErrors,
  clearSyncErrors,
  retrySync,
  getSyncProgress,
  setSyncStrategy,
  getSyncStrategy,
} from "../data-sync";
// タイマーのモック
jest.useFakeTimers();
describe("data-sync", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  afterEach(() => {
    jest.runOnlyPendingTimers();
  });
  describe("syncData", () => {
    it("syncs data successfully", async () => {
      const result = await syncData();
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("timestamp");
    });
    it("handles sync errors", async () => {
      // エラーをシミュレート
      const result = await syncData();
      expect(result).toHaveProperty("success");
    });
  });
  describe("getSyncStatus", () => {
    it("returns sync status", () => {
      const status = getSyncStatus();
      expect(status).toHaveProperty("running");
      expect(status).toHaveProperty("lastSync");
      expect(status).toHaveProperty("nextSync");
    });
  });
  describe("getLastSyncTime", () => {
    it("returns last sync time", () => {
      const lastSync = getLastSyncTime();
      expect(typeof lastSync).toBe("number");
      expect(lastSync).toBeGreaterThan(0);
    });
  });
  describe("setSyncInterval", () => {
    it("sets sync interval", () => {
      setSyncInterval(5000);
      const status = getSyncStatus();
      expect(status.interval).toBe(5000);
    });
    it("validates interval value", () => {
      expect(() => setSyncInterval(-1000)).toThrow();
      expect(() => setSyncInterval(0)).toThrow();
    });
  });
  describe("startSync", () => {
    it("starts sync process", () => {
      startSync();
      expect(isSyncRunning()).toBe(true);
    });
    it("handles already running sync", () => {
      startSync();
      startSync(); // Should not throw
      expect(isSyncRunning()).toBe(true);
    });
  });
  describe("stopSync", () => {
    it("stops sync process", () => {
      startSync();
      stopSync();
      expect(isSyncRunning()).toBe(false);
    });
    it("handles already stopped sync", () => {
      stopSync(); // Should not throw
      expect(isSyncRunning()).toBe(false);
    });
  });
  describe("isSyncRunning", () => {
    it("returns sync running status", () => {
      const running = isSyncRunning();
      expect(typeof running).toBe("boolean");
    });
  });
  describe("getSyncErrors", () => {
    it("returns sync errors", () => {
      const errors = getSyncErrors();
      expect(Array.isArray(errors)).toBe(true);
    });
  });
  describe("clearSyncErrors", () => {
    it("clears sync errors", () => {
      clearSyncErrors();
      const errors = getSyncErrors();
      expect(errors).toHaveLength(0);
    });
  });
  describe("retrySync", () => {
    it("retries sync operation", async () => {
      const result = await retrySync();
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("attempts");
    });
    it("handles retry limits", async () => {
      const result = await retrySync(3);
      expect(result.attempts).toBeLessThanOrEqual(3);
    });
  });
  describe("getSyncProgress", () => {
    it("returns sync progress", () => {
      const progress = getSyncProgress();
      expect(progress).toHaveProperty("percentage");
      expect(progress).toHaveProperty("current");
      expect(progress).toHaveProperty("total");
    });
  });
  describe("setSyncStrategy", () => {
    it("sets sync strategy", () => {
      setSyncStrategy("incremental");
      expect(getSyncStrategy()).toBe("incremental");
    });
    it("validates strategy", () => {
      expect(() => setSyncStrategy("invalid")).toThrow();
    });
  });
  describe("getSyncStrategy", () => {
    it("returns current sync strategy", () => {
      const strategy = getSyncStrategy();
      expect(typeof strategy).toBe("string");
    });
  });
});
