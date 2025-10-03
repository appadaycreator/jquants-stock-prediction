import { 
  formatDate, 
  parseDate, 
  getCurrentDate, 
  addDays, 
  subtractDays,
  getDaysBetween,
  isWeekend,
  getBusinessDays
} from "../datetime";

describe("datetime", () => {
  describe("formatDate", () => {
    it("formats date with default format", () => {
      const date = new Date("2024-01-15T10:30:00Z");
      const formatted = formatDate(date);
      expect(formatted).toBe("2024-01-15");
    });

    it("formats date with custom format", () => {
      const date = new Date("2024-01-15T10:30:00Z");
      const formatted = formatDate(date, "YYYY/MM/DD");
      expect(formatted).toBe("2024/01/15");
    });

    it("handles different date formats", () => {
      const date = new Date("2024-01-15T10:30:00Z");
      expect(formatDate(date, "MM-DD-YYYY")).toBe("01-15-2024");
      expect(formatDate(date, "DD/MM/YYYY")).toBe("15/01/2024");
    });
  });

  describe("parseDate", () => {
    it("parses valid date strings", () => {
      const date = parseDate("2024-01-15");
      expect(date).toBeInstanceOf(Date);
      expect(date.getFullYear()).toBe(2024);
      expect(date.getMonth()).toBe(0); // January
      expect(date.getDate()).toBe(15);
    });

    it("returns null for invalid date strings", () => {
      expect(parseDate("invalid-date")).toBeNull();
      expect(parseDate("")).toBeNull();
    });
  });

  describe("getCurrentDate", () => {
    it("returns current date", () => {
      const currentDate = getCurrentDate();
      expect(currentDate).toBeInstanceOf(Date);
      expect(currentDate.getTime()).toBeLessThanOrEqual(Date.now());
    });
  });

  describe("addDays", () => {
    it("adds days to date", () => {
      const date = new Date("2024-01-15");
      const result = addDays(date, 5);
      expect(result.getDate()).toBe(20);
    });

    it("handles month boundaries", () => {
      const date = new Date("2024-01-30");
      const result = addDays(date, 5);
      expect(result.getMonth()).toBe(1); // February
      expect(result.getDate()).toBe(4);
    });
  });

  describe("subtractDays", () => {
    it("subtracts days from date", () => {
      const date = new Date("2024-01-15");
      const result = subtractDays(date, 5);
      expect(result.getDate()).toBe(10);
    });

    it("handles month boundaries", () => {
      const date = new Date("2024-02-01");
      const result = subtractDays(date, 5);
      expect(result.getMonth()).toBe(0); // January
      expect(result.getDate()).toBe(27);
    });
  });

  describe("getDaysBetween", () => {
    it("calculates days between dates", () => {
      const date1 = new Date("2024-01-15");
      const date2 = new Date("2024-01-20");
      expect(getDaysBetween(date1, date2)).toBe(5);
    });

    it("handles reverse order", () => {
      const date1 = new Date("2024-01-20");
      const date2 = new Date("2024-01-15");
      expect(getDaysBetween(date1, date2)).toBe(5);
    });
  });

  describe("isWeekend", () => {
    it("identifies weekends correctly", () => {
      const saturday = new Date("2024-01-13"); // Saturday
      const sunday = new Date("2024-01-14"); // Sunday
      const monday = new Date("2024-01-15"); // Monday

      expect(isWeekend(saturday)).toBe(true);
      expect(isWeekend(sunday)).toBe(true);
      expect(isWeekend(monday)).toBe(false);
    });
  });

  describe("getBusinessDays", () => {
    it("calculates business days between dates", () => {
      const start = new Date("2024-01-15"); // Monday
      const end = new Date("2024-01-19"); // Friday
      expect(getBusinessDays(start, end)).toBe(5);
    });

    it("excludes weekends", () => {
      const start = new Date("2024-01-13"); // Saturday
      const end = new Date("2024-01-16"); // Tuesday
      expect(getBusinessDays(start, end)).toBe(2); // Monday and Tuesday
    });
  });
});

