import { fetchJson, AppError } from "../fetcher";

// Mock the fetch function
global.fetch = jest.fn();

describe("fetcher", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("fetchJson", () => {
    it("fetches data successfully", async () => {
      const mockData = { message: "Success" };
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.resolve(mockData),
      });

      const result = await fetchJson("/api/test");

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith("/api/test", expect.objectContaining({
        cache: "no-cache",
        headers: expect.objectContaining({
          "Cache-Control": "no-cache",
          "Pragma": "no-cache",
        }),
      }));
    }, 10000);

    it("handles API errors with status codes", async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: () => Promise.resolve({ error: "Not Found" }),
      });

      await expect(fetchJson("/api/test")).rejects.toThrow("Not Found");
    }, 10000);

    it("handles network errors", async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error("Network Error"));

      await expect(fetchJson("/api/test")).rejects.toThrow("Network Error");
    }, 10000);

    it("handles JSON parsing errors", async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        json: () => Promise.reject(new Error("Invalid JSON")),
      });

      await expect(fetchJson("/api/test")).rejects.toThrow("Invalid JSON");
    }, 10000);
  });

  describe("AppError", () => {
    it("creates error with message and code", () => {
      const error = new AppError("Test error", "TEST_ERROR");
      expect(error.message).toBe("Test error");
      expect(error.code).toBe("TEST_ERROR");
      expect(error.name).toBe("AppError");
    });

    it("creates error with status and retry hint", () => {
      const error = new AppError("Test error", "TEST_ERROR", 404, "Retry later");
      expect(error.status).toBe(404);
      expect(error.retryHint).toBe("Retry later");
    });
  });
});