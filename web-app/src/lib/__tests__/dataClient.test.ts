import { dataClient } from "../dataClient";

// fetch のモック
global.fetch = jest.fn();

describe("dataClient", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("get", () => {
    it("makes GET request successfully", async () => {
      const mockResponse = { data: "test" };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await dataClient.get("/test");

      expect(fetch).toHaveBeenCalledWith("/api/test", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      expect(result).toEqual(mockResponse);
    });

    it("handles API errors", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
      });

      await expect(dataClient.get("/test")).rejects.toThrow("API Error: 404 Not Found");
    });

    it("handles network errors", async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

      await expect(dataClient.get("/test")).rejects.toThrow("Network error");
    });
  });

  describe("post", () => {
    it("makes POST request successfully", async () => {
      const mockResponse = { success: true };
      const requestData = { name: "test" };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await dataClient.post("/test", requestData);

      expect(fetch).toHaveBeenCalledWith("/api/test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });
      expect(result).toEqual(mockResponse);
    });

    it("handles POST request errors", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
      });

      await expect(dataClient.post("/test", {})).rejects.toThrow("API Error: 400 Bad Request");
    });
  });

  describe("put", () => {
    it("makes PUT request successfully", async () => {
      const mockResponse = { updated: true };
      const requestData = { id: 1, name: "updated" };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await dataClient.put("/test/1", requestData);

      expect(fetch).toHaveBeenCalledWith("/api/test/1", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe("delete", () => {
    it("makes DELETE request successfully", async () => {
      const mockResponse = { deleted: true };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await dataClient.delete("/test/1");

      expect(fetch).toHaveBeenCalledWith("/api/test/1", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe("request", () => {
    it("makes custom request", async () => {
      const mockResponse = { data: "test" };
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await dataClient.request("/test", {
        method: "PATCH",
        headers: { "Custom-Header": "value" },
      });

      expect(fetch).toHaveBeenCalledWith("/api/test", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Custom-Header": "value",
        },
      });
      expect(result).toEqual(mockResponse);
    });
  });
});

