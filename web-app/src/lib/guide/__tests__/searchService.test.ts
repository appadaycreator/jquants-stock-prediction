import { SearchService } from "../searchService";

describe("SearchService", () => {
  describe("searchHelp", () => {
    it("should return empty array for empty query", () => {
      const results = SearchService.searchHelp("");
      expect(results).toEqual([]);
    });

    it("should return empty array for whitespace query", () => {
      const results = SearchService.searchHelp("   ");
      expect(results).toEqual([]);
    });

    it("should find help sections by title", () => {
      const results = SearchService.searchHelp("ダッシュボード");
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toContain("ダッシュボード");
    });

    it("should find FAQ items by question", () => {
      const results = SearchService.searchHelp("MAE");
      expect(results.length).toBeGreaterThan(0);
      expect(results.some(r => r.title.includes("MAE"))).toBe(true);
    });
  });

  describe("searchGlossary", () => {
    it("should return empty array for empty query", () => {
      const results = SearchService.searchGlossary("");
      expect(results).toEqual([]);
    });

    it("should find glossary items by term", () => {
      const results = SearchService.searchGlossary("MAE");
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toBe("MAE");
    });

    it("should find glossary items by short description", () => {
      const results = SearchService.searchGlossary("平均絶対誤差");
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toBe("MAE");
    });
  });

  describe("searchAll", () => {
    it("should return empty array for empty query", () => {
      const results = SearchService.searchAll("");
      expect(results).toEqual([]);
    });

    it("should find results from all sources", () => {
      const results = SearchService.searchAll("MAE");
      expect(results.length).toBeGreaterThan(0);
      expect(results.some(r => r.title && r.title.includes("MAE"))).toBe(true);
    });
  });

  describe("getSuggestions", () => {
    it("should return empty array for empty query", () => {
      const suggestions = SearchService.getSuggestions("");
      expect(suggestions).toEqual([]);
    });

    it("should return suggestions for valid query", () => {
      const suggestions = SearchService.getSuggestions("MAE");
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0] && suggestions[0].includes("MAE")).toBe(true);
    });

    it("should respect limit parameter", () => {
      const suggestions = SearchService.getSuggestions("a", 2);
      expect(suggestions.length).toBeLessThanOrEqual(2);
    });
  });

  describe("searchByCategory", () => {
    it("should return empty array for empty query", () => {
      const results = SearchService.searchByCategory("", "指標");
      expect(results).toEqual([]);
    });

    it("should filter results by category", () => {
      const results = SearchService.searchByCategory("MAE", "指標");
      expect(results.length).toBeGreaterThan(0);
      expect(results.every(r => r.category === "指標")).toBe(true);
    });
  });
});
