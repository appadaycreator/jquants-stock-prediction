import { 
  highlightText, 
  highlightFields, 
  createSnippet, 
  normalizeQuery, 
  isValidQuery, 
} from "../highlightUtils";

describe("highlightUtils", () => {
  describe("highlightText", () => {
    it("should return original text for empty query", () => {
      const result = highlightText("Hello world", "");
      expect(result).toBe("Hello world");
    });

    it("should highlight single word", () => {
      const result = highlightText("Hello world", "Hello");
      expect(result).toContain("<span class=\"bg-yellow-200 text-yellow-900 px-1 rounded\">Hello</span>");
    });

    it("should highlight multiple words", () => {
      const result = highlightText("Hello world", "Hello world");
      expect(result).toContain("<span class=\"bg-yellow-200 text-yellow-900 px-1 rounded\">Hello</span>");
      expect(result).toContain("<span class=\"bg-yellow-200 text-yellow-900 px-1 rounded\">world</span>");
    });

    it("should be case insensitive", () => {
      const result = highlightText("Hello world", "hello");
      expect(result).toContain("<span class=\"bg-yellow-200 text-yellow-900 px-1 rounded\">Hello</span>");
    });

    it("should use custom className", () => {
      const result = highlightText("Hello world", "Hello", "custom-class");
      expect(result).toContain("<span class=\"custom-class\">Hello</span>");
    });
  });

  describe("highlightFields", () => {
    it("should highlight multiple fields", () => {
      const fields = ["Hello world", "Test text"];
      const result = highlightFields(fields, "Hello");
      expect(result[0]).toContain("<span class=\"bg-yellow-200 text-yellow-900 px-1 rounded\">Hello</span>");
      expect(result[1]).toBe("Test text");
    });
  });

  describe("createSnippet", () => {
    it("should return original text for empty query", () => {
      const result = createSnippet("Hello world", "");
      expect(result).toBe("Hello world");
    });

    it("should create snippet around match", () => {
      const text = "This is a long text with Hello world in the middle";
      const result = createSnippet(text, "Hello", 20);
      expect(result).toContain("Hello");
      expect(result.length).toBeLessThanOrEqual(20 + 6); // 20 + '...' on both sides
    });

    it("should add ellipsis for long text", () => {
      const text = "This is a very long text that should be truncated";
      const result = createSnippet(text, "long", 20);
      expect(result).toContain("...");
    });
  });

  describe("normalizeQuery", () => {
    it("should trim whitespace", () => {
      const result = normalizeQuery("  hello world  ");
      expect(result).toBe("hello world");
    });

    it("should remove duplicate spaces", () => {
      const result = normalizeQuery("hello    world");
      expect(result).toBe("hello world");
    });

    it("should filter empty words", () => {
      const result = normalizeQuery("hello   world");
      expect(result).toBe("hello world");
    });
  });

  describe("isValidQuery", () => {
    it("should return false for empty query", () => {
      expect(isValidQuery("")).toBe(false);
    });

    it("should return false for whitespace only", () => {
      expect(isValidQuery("   ")).toBe(false);
    });

    it("should return false for single character", () => {
      expect(isValidQuery("a")).toBe(false);
    });

    it("should return true for valid query", () => {
      expect(isValidQuery("hello")).toBe(true);
    });

    it("should return true for query with spaces", () => {
      expect(isValidQuery("hello world")).toBe(true);
    });
  });
});
