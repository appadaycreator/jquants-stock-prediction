import { 
  startUpdateWorker, 
  stopUpdateWorker, 
  isUpdateWorkerRunning,
  getUpdateWorkerStatus,
  setUpdateWorkerInterval,
  getUpdateWorkerInterval,
  pauseUpdateWorker,
  resumeUpdateWorker,
  getUpdateWorkerProgress,
  getUpdateWorkerErrors,
  clearUpdateWorkerErrors,
  retryUpdateWorker,
  getUpdateWorkerHistory,
  clearUpdateWorkerHistory
} from "../updateWorker";

// タイマーのモック
jest.useFakeTimers();

describe("updateWorker", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
  });

  describe("startUpdateWorker", () => {
    it("starts update worker", () => {
      startUpdateWorker();
      expect(isUpdateWorkerRunning()).toBe(true);
    });

    it("handles already running worker", () => {
      startUpdateWorker();
      startUpdateWorker(); // Should not throw
      expect(isUpdateWorkerRunning()).toBe(true);
    });
  });

  describe("stopUpdateWorker", () => {
    it("stops update worker", () => {
      startUpdateWorker();
      stopUpdateWorker();
      expect(isUpdateWorkerRunning()).toBe(false);
    });

    it("handles already stopped worker", () => {
      stopUpdateWorker(); // Should not throw
      expect(isUpdateWorkerRunning()).toBe(false);
    });
  });

  describe("isUpdateWorkerRunning", () => {
    it("returns worker running status", () => {
      const running = isUpdateWorkerRunning();
      expect(typeof running).toBe("boolean");
    });
  });

  describe("getUpdateWorkerStatus", () => {
    it("returns worker status", () => {
      const status = getUpdateWorkerStatus();
      expect(status).toHaveProperty("running");
      expect(status).toHaveProperty("lastUpdate");
      expect(status).toHaveProperty("nextUpdate");
    });
  });

  describe("setUpdateWorkerInterval", () => {
    it("sets update interval", () => {
      setUpdateWorkerInterval(5000);
      expect(getUpdateWorkerInterval()).toBe(5000);
    });

    it("validates interval value", () => {
      expect(() => setUpdateWorkerInterval(-1000)).toThrow();
      expect(() => setUpdateWorkerInterval(0)).toThrow();
    });
  });

  describe("getUpdateWorkerInterval", () => {
    it("returns current interval", () => {
      const interval = getUpdateWorkerInterval();
      expect(typeof interval).toBe("number");
      expect(interval).toBeGreaterThan(0);
    });
  });

  describe("pauseUpdateWorker", () => {
    it("pauses update worker", () => {
      startUpdateWorker();
      pauseUpdateWorker();
      expect(isUpdateWorkerRunning()).toBe(false);
    });
  });

  describe("resumeUpdateWorker", () => {
    it("resumes update worker", () => {
      startUpdateWorker();
      pauseUpdateWorker();
      resumeUpdateWorker();
      expect(isUpdateWorkerRunning()).toBe(true);
    });
  });

  describe("getUpdateWorkerProgress", () => {
    it("returns update progress", () => {
      const progress = getUpdateWorkerProgress();
      expect(progress).toHaveProperty("percentage");
      expect(progress).toHaveProperty("current");
      expect(progress).toHaveProperty("total");
    });
  });

  describe("getUpdateWorkerErrors", () => {
    it("returns update errors", () => {
      const errors = getUpdateWorkerErrors();
      expect(Array.isArray(errors)).toBe(true);
    });
  });

  describe("clearUpdateWorkerErrors", () => {
    it("clears update errors", () => {
      clearUpdateWorkerErrors();
      const errors = getUpdateWorkerErrors();
      expect(errors).toHaveLength(0);
    });
  });

  describe("retryUpdateWorker", () => {
    it("retries update operation", async () => {
      const result = await retryUpdateWorker();
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("attempts");
    });

    it("handles retry limits", async () => {
      const result = await retryUpdateWorker(3);
      expect(result.attempts).toBeLessThanOrEqual(3);
    });
  });

  describe("getUpdateWorkerHistory", () => {
    it("returns update history", () => {
      const history = getUpdateWorkerHistory();
      expect(Array.isArray(history)).toBe(true);
    });
  });

  describe("clearUpdateWorkerHistory", () => {
    it("clears update history", () => {
      clearUpdateWorkerHistory();
      const history = getUpdateWorkerHistory();
      expect(history).toHaveLength(0);
    });
  }),
});

