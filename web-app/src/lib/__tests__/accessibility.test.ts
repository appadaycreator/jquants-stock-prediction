import { 
  checkAccessibility, 
  getAccessibilityScore, 
  getAccessibilityIssues,
  fixAccessibilityIssues,
  validateARIA,
  checkColorContrast,
  checkKeyboardNavigation,
  checkScreenReaderSupport,
  generateAccessibilityReport
} from "../accessibility";

// DOM のモック
const mockElement = {
  getAttribute: jest.fn(),
  setAttribute: jest.fn(),
  removeAttribute: jest.fn(),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn(() => []),
  style: {},
};

Object.defineProperty(document, "querySelector", {
  value: jest.fn(() => mockElement),
});

Object.defineProperty(document, "querySelectorAll", {
  value: jest.fn(() => [mockElement]),
});

describe("accessibility", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("checkAccessibility", () => {
    it("checks accessibility of an element", () => {
      const result = checkAccessibility(mockElement);
      expect(result).toHaveProperty("score");
      expect(result).toHaveProperty("issues");
      expect(result).toHaveProperty("recommendations");
    });

    it("handles null elements", () => {
      const result = checkAccessibility(null);
      expect(result.score).toBe(0);
      expect(result.issues).toHaveLength(0);
    });
  });

  describe("getAccessibilityScore", () => {
    it("calculates accessibility score", () => {
      const score = getAccessibilityScore(mockElement);
      expect(typeof score).toBe("number");
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });
  });

  describe("getAccessibilityIssues", () => {
    it("identifies accessibility issues", () => {
      const issues = getAccessibilityIssues(mockElement);
      expect(Array.isArray(issues)).toBe(true);
    });

    it("handles elements without issues", () => {
      mockElement.getAttribute.mockReturnValue("button");
      const issues = getAccessibilityIssues(mockElement);
      expect(issues).toHaveLength(0);
    });
  });

  describe("fixAccessibilityIssues", () => {
    it("fixes accessibility issues", () => {
      const result = fixAccessibilityIssues(mockElement);
      expect(result).toHaveProperty("fixed");
      expect(result).toHaveProperty("remaining");
    });

    it("handles elements without issues", () => {
      const result = fixAccessibilityIssues(mockElement);
      expect(result.fixed).toBe(0);
      expect(result.remaining).toBe(0);
    });
  });

  describe("validateARIA", () => {
    it("validates ARIA attributes", () => {
      mockElement.getAttribute.mockReturnValue("button");
      const result = validateARIA(mockElement);
      expect(result).toHaveProperty("valid");
      expect(result).toHaveProperty("errors");
    });

    it("identifies invalid ARIA attributes", () => {
      mockElement.getAttribute.mockReturnValue("invalid-aria");
      const result = validateARIA(mockElement);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe("checkColorContrast", () => {
    it("checks color contrast ratio", () => {
      const result = checkColorContrast("#000000", "#ffffff");
      expect(result).toHaveProperty("ratio");
      expect(result).toHaveProperty("passes");
      expect(result.ratio).toBeGreaterThan(0);
    });

    it("identifies low contrast", () => {
      const result = checkColorContrast("#000000", "#000001");
      expect(result.passes).toBe(false);
    });
  });

  describe("checkKeyboardNavigation", () => {
    it("checks keyboard navigation support", () => {
      const result = checkKeyboardNavigation(mockElement);
      expect(result).toHaveProperty("navigable");
      expect(result).toHaveProperty("tabIndex");
    });

    it("identifies non-navigable elements", () => {
      mockElement.getAttribute.mockReturnValue(null);
      const result = checkKeyboardNavigation(mockElement);
      expect(result.navigable).toBe(false);
    });
  });

  describe("checkScreenReaderSupport", () => {
    it("checks screen reader support", () => {
      const result = checkScreenReaderSupport(mockElement);
      expect(result).toHaveProperty("supported");
      expect(result).toHaveProperty("announcements");
    });

    it("identifies missing screen reader support", () => {
      mockElement.getAttribute.mockReturnValue(null);
      const result = checkScreenReaderSupport(mockElement);
      expect(result.supported).toBe(false);
    });
  });

  describe("generateAccessibilityReport", () => {
    it("generates accessibility report", () => {
      const report = generateAccessibilityReport();
      expect(report).toHaveProperty("overallScore");
      expect(report).toHaveProperty("issues");
      expect(report).toHaveProperty("recommendations");
    });

    it("includes element-specific information", () => {
      const report = generateAccessibilityReport([mockElement]);
      expect(report).toHaveProperty("elements");
      expect(Array.isArray(report.elements)).toBe(true);
    });
  });
});

